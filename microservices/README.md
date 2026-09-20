# Microservices

This directory contains independent microservice examples. Each system has
its own deployment files and documentation so it can evolve without changing
the other examples.

## Systems

### Existing Django and NATS system

[`microservice-system/`](microservice-system/) is the existing assignment
system. It contains a Django API gateway, Django user and notification
services, and NATS JetStream.

### Polyglot event-driven system

[`polyglot-system/`](polyglot-system/) is a separate reference architecture
using:

- Django for identity and administration
- FastAPI for a high-throughput catalog API
- Flask for a small edge/aggregation API
- Kafka for durable domain events
- Valkey for caching and distributed rate-limit state
- rate limiting at the public edge

Start with its
[`README.md`](polyglot-system/README.md). The documentation records the
meaning of “ratlelmilt” as rate limiting and the service boundaries, event
contracts, local topology, and production checklist.

### Learn-by-doing order system

[`learning-system/`](learning-system/) is a small runnable exercise. A Flask
order service calls a FastAPI inventory service, stores an idempotency record
in Valkey, and publishes `order.created` to Kafka. It includes Docker
Compose, curl exercises, and tests so the flow can be learned one step at a
time.
