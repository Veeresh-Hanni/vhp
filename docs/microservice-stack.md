# Microservice libraries and infrastructure

The VHP examples use several frameworks and infrastructure libraries. Each
one solves a different problem. Learning the boundaries is more valuable than
memorizing commands.

## Django and Django REST Framework

Django is a batteries-included web framework. It provides URL routing,
settings, middleware, ORM models, migrations, authentication primitives, and
an administration site. Django REST Framework (DRF) adds serializers,
request/response classes, authentication, permissions, and API views.

Use Django when a service needs a rich domain model, migrations, admin
workflows, and a conventional application structure. In the VHP Django +
NATS example, the user service owns registration and authentication while the
notification service owns notification records.

Important learning questions:

- Which Django app owns each model?
- When is a migration required?
- Where should authorization be checked?
- Does a request need a serializer, a service function, or both?
- What happens if database work succeeds but event publication fails?

The API gateway should route and authenticate, but it should not become the
owner of user or notification data.

## FastAPI and Pydantic

FastAPI is an ASGI framework suited to typed HTTP APIs and asynchronous
handlers. Pydantic models validate request and response data and produce an
OpenAPI description.

In the learning order system, FastAPI owns inventory reservation. The
`Reservation` model rejects missing or invalid quantities before the handler
changes stock.

```python
class Reservation(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
```

Validation is not business authorization. A valid quantity can still exceed
available stock, which is why the inventory service must perform an atomic
reservation check.

## Flask

Flask is a small WSGI framework that exposes the request/response lifecycle
with little ceremony. It is useful for a focused edge service, webhook
receiver, or small API where the team wants to choose its own extensions.

The order service uses Flask to:

1. validate the idempotency key and basic request shape;
2. call the inventory service over HTTP;
3. save the accepted response in Valkey;
4. publish an `order.created` event to Kafka;
5. return a response to the client.

This also demonstrates why an edge service should have explicit timeouts and
failure responses. A downstream HTTP call must not be allowed to hang a web
worker indefinitely.

## Kafka

Kafka is a durable, partitioned event log. Producers write records to topics;
consumers read them and commit offsets after processing. A topic is not just a
remote function call: events may be replayed, delayed, duplicated, or
processed by multiple consumer groups.

The learning system publishes an `order.created` event. A production event
should include a stable ID, event type, version, producer, timestamp, and
domain data:

```json
{
  "event_id": "evt-123",
  "event_type": "order.created",
  "event_version": 1,
  "producer": "order-service",
  "data": {"order_id": "ord-123", "sku": "book-1", "quantity": 2}
}
```

Study these Kafka concepts:

- partitions and ordering scope;
- consumer groups and independent subscriptions;
- offset commits and replay;
- retry and dead-letter topics;
- schema compatibility;
- idempotent consumers;
- the outbox pattern for database-to-event reliability.

The local Compose file uses a single KRaft broker for learning. It is not a
production availability configuration.

## Valkey

Valkey is an in-memory key-value server compatible with the Redis protocol.
The examples use it for two different short-lived coordination tasks:

- inventory counters in the learning example;
- idempotency responses keyed by `Idempotency-Key`.

The `DECRBY` operation lets the inventory service reserve stock atomically
enough for the single-key exercise. If the result is negative, the service
restores the value and returns a conflict.

Valkey is appropriate for caches, rate-limit counters, locks with carefully
defined expiry, and short-lived idempotency records. A production inventory
system normally needs durable storage, reservation expiration, audit history,
and recovery behavior. Do not treat a cache as the only source of truth
without deliberately accepting that data-loss risk.

## NATS JetStream

The Django assignment uses NATS JetStream for authenticated asynchronous
events. JetStream adds persistence, streams, acknowledgements, and durable
consumers to NATS messaging.

The notification consumer acknowledges a user-created event only after its
database write succeeds. This is the important reliability lesson: an
acknowledgement means the consumer has completed the work, not merely that it
received bytes.

Compare NATS with Kafka:

| Concern | NATS JetStream | Kafka |
| --- | --- | --- |
| Learning emphasis | Simple subjects, durable consumers, acknowledgements | Topics, partitions, consumer groups, replay |
| Typical event unit | Message on a subject | Record in a partitioned topic |
| Scaling model | Lightweight messaging with persistence options | Distributed log with high-throughput partitions |
| Required design | Ack after successful processing | Commit offset after successful processing |

Both systems still require idempotent consumers and explicit retry behavior.

## HTTP clients and service boundaries

The examples use HTTP between services when the caller needs an immediate
answer. A service call should define:

- URL and authentication;
- request and response schema;
- connect and read timeouts;
- retryable versus non-retryable failures;
- correlation/request ID propagation;
- behavior when the downstream service is unavailable.

Do not retry a non-idempotent write blindly. If a request can be repeated,
use an idempotency key or a domain-level command ID.

## Docker Compose and WSL

Docker Compose describes the local dependency topology. Container-to-container
names use service DNS names such as `kafka` and `valkey`; a Python process
running directly in WSL uses published host ports such as Kafka `9094`.

This distinction is a common source of local failures:

```text
inside Compose: kafka:9092, valkey:6379
inside WSL:     localhost:9094, localhost:6379
```

The recommended learning workflow is to run infrastructure in Docker and
application servers in WSL when live reload and debugging are more important
than reproducing the final container image.

## Reliability checklist

For each endpoint and event, write down:

1. who owns the data;
2. what happens on a timeout;
3. whether a retry is safe;
4. how duplicate delivery is handled;
5. how the operation is observed in logs and metrics;
6. how the system recovers after a process or broker restart.

Then implement one answer at a time. This turns the microservice examples
from framework demonstrations into an applied reliability curriculum.
