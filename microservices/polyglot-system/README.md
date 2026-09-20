# Polyglot event-driven microservice system

This is a separate system from
[`../microservice-system/`](../microservice-system/). It is an implementation
blueprint for a small platform composed of Django, FastAPI, Flask, Kafka, and
Valkey.

> **Terminology note:** this document interprets “ratlelmilt” as **rate
> limiting**. The edge service owns request quotas and stores counters in
> Valkey so all edge replicas share the same limits.

## Goals

- Keep identity and administration in Django.
- Use FastAPI for an async, read-heavy catalog API.
- Use Flask for a deliberately small public edge/aggregation service.
- Publish business changes through Kafka rather than coupling services with
  synchronous calls.
- Use Valkey for cache data and short-lived rate-limit counters.
- Make each service independently deployable and independently observable.

This is a starter architecture, not a claim that every service should use a
different framework in production. A real system should prefer one framework
unless a clear operational or team reason justifies the extra complexity.

## Architecture

```mermaid
flowchart LR
    Client --> Edge[Flask edge :8000]
    Edge -->|rate limit + proxy| Identity[Django identity :8001]
    Edge -->|rate limit + proxy| Catalog[FastAPI catalog :8002]
    Edge <--> Cache[(Valkey)]
    Identity -->|user.created| Kafka[(Kafka)]
    Catalog -->|product.updated| Kafka
    Kafka --> Consumers[Independent consumers]
```

### Service responsibilities

| Service | Framework | Owns | Public port |
| --- | --- | --- | --- |
| `edge-service` | Flask | routing, request IDs, rate limits, response aggregation | 8000 |
| `identity-service` | Django + DRF | users, sessions/JWT issuance, admin workflows | 8001 |
| `catalog-service` | FastAPI | catalog reads/writes and OpenAPI contract | 8002 |
| `kafka` | Kafka in KRaft mode | durable event transport | 9092 |
| `valkey` | Valkey | cache and shared rate-limit counters | 6379 |

The edge is the only service exposed to clients. Internal services must
validate the caller identity and must not trust headers that can be supplied
by an external client. The edge may add a signed internal identity header
after authentication, or the services may validate the original token.

## Event contracts

Events use a versioned envelope. Producers must write the event to Kafka only
after the local transaction succeeds; use an outbox table when delivery must
be guaranteed.

```json
{
  "event_id": "01J...",
  "event_type": "user.created",
  "event_version": 1,
  "occurred_at": "2026-01-01T12:00:00Z",
  "producer": "identity-service",
  "data": {
    "user_id": "user-123",
    "email": "person@example.com"
  }
}
```

Recommended topics:

| Topic | Producer | Consumers |
| --- | --- | --- |
| `identity.user.v1` | Django identity | analytics, email, audit |
| `catalog.product.v1` | FastAPI catalog | search index, analytics |

Consumers must be idempotent using `event_id`, commit offsets only after
successful processing, and send poison messages to a dead-letter topic.

## Rate limiting

Apply limits in the Flask edge before proxying:

| Scope | Example key | Starter limit |
| --- | --- | --- |
| Anonymous client | `ip:{client_ip}` | 60 requests/minute |
| Authenticated client | `user:{user_id}` | 300 requests/minute |
| Expensive endpoint | `user:{user_id}:search` | 30 requests/minute |

Use Valkey atomic operations with an expiry (for example, a fixed-window
counter or a Lua-backed token bucket). Do not use process-local memory: it
breaks as soon as the edge has more than one replica. Return HTTP `429` with a
`Retry-After` header and do not log tokens or passwords.

## Local development topology

The intended local dependencies are:

```text
Flask edge -> Django identity
           -> FastAPI catalog
           -> Valkey
Django/FastAPI -> Kafka
```

Run Kafka in KRaft mode for local development to avoid a separate ZooKeeper
dependency. For a real deployment, pin image versions, configure persistent
volumes, use TLS/SASL for Kafka, require authentication for Valkey, and use
managed databases rather than SQLite.

Suggested environment variables:

```text
DJANGO_SECRET_KEY=replace-in-development
DATABASE_URL=postgresql://identity:password@postgres:5432/identity
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
VALKEY_URL=redis://valkey:6379/0
IDENTITY_SERVICE_URL=http://identity-service:8000
CATALOG_SERVICE_URL=http://catalog-service:8000
RATE_LIMIT_PER_MINUTE=60
```

Keep secrets in an untracked `.env` file or a secret manager. Never use the
development values in a shared or production environment.

## Request flow

1. A client calls the Flask edge with a request ID and access token.
2. The edge checks the Valkey-backed limit for the client.
3. The edge forwards identity requests to Django and catalog requests to
   FastAPI with a short timeout.
4. Django or FastAPI validates the request and performs its own authorization.
5. A successful state change emits a versioned Kafka event.
6. The edge returns the downstream response and propagates the request ID.

Timeouts, retries, and idempotency keys must be explicit. Do not blindly retry
non-idempotent writes.

## Production checklist

- Use PostgreSQL per service; do not share service-owned tables.
- Add health and readiness endpoints to every service.
- Add structured logs with `request_id`, `event_id`, and service name.
- Export metrics for latency, HTTP errors, rate-limit responses, Kafka lag,
  Valkey errors, and downstream timeouts.
- Configure Kafka replication, retention, ACLs, TLS, and dead-letter topics.
- Configure Valkey authentication, TLS, eviction policy, and persistence
  according to the cache/counter data classification.
- Add contract tests for edge-to-service APIs and event schemas.
- Add consumer retry backoff and a replay procedure.
- Run database migrations as a release step, not on every web-container
  startup.
- Set resource limits and graceful shutdown timeouts for every container.

## Suggested repository layout

```text
polyglot-system/
  edge-service/       # Flask
  identity-service/   # Django + DRF
  catalog-service/    # FastAPI
  contracts/          # OpenAPI and event JSON schemas
  deploy/             # Compose and production manifests
  README.md
```

The existing Django/NATS project remains available for comparison; this
system intentionally uses Kafka and Valkey instead of NATS and local-only
state.
