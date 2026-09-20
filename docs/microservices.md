# Microservice documentation

The VHP microservice examples are designed to be run, inspected, changed,
and run again. They progress from a Django event-driven assignment to a
polyglot architecture and then to a small order-and-inventory system.

## Choose an example

| Example | Main lesson | Local source |
| --- | --- | --- |
| Django + NATS | API gateway, JWT authentication, service ownership, and asynchronous notifications | [`microservice-system`](https://github.com/Veeresh-Hanni/microservice-system) |
| Polyglot design | Django, FastAPI, Flask, Kafka, Valkey, and rate limiting | [`polyglot-system`](https://github.com/Veeresh-Hanni/vhp/tree/main/microservices/polyglot-system) |
| Learn-by-doing order system | Flask-to-FastAPI calls, Valkey idempotency, inventory reservation, and Kafka events | [`learning-microservice-system`](https://github.com/Veeresh-Hanni/vhp/tree/main/microservices/learning-microservice-system)


The local source documentation remains useful when working from a checkout:

- [`microservices/README.md`](https://github.com/Veeresh-Hanni/vhp/blob/main/microservices/README.md)
- [`learning-microservice-system/README.md`](https://github.com/Veeresh-Hanni/vhp/blob/main/microservices/learning-microservice-system/README.md)

## What a microservice should own

Each service should have a clear responsibility and its own data boundary.
For the learning order system:

```text
Client
  |
  v
Flask order-service (:8000)
  |                         \
  v                          v
FastAPI inventory-service   Kafka: order.created
(:8001)                     |
  |                         v
  +--> Valkey            Future consumers
```

- Flask owns the order request and idempotency key.
- FastAPI owns stock reservation.
- Valkey stores short-lived idempotency records and learning stock counters.
- Kafka carries the `order.created` event.

The services communicate over HTTP when an immediate response is required.
They communicate through Kafka when a downstream action can happen
asynchronously.

## Run the learning system

From WSL:

```bash
cd /mnt/d/vhp/microservices/learning-microservice-system
docker compose up --build -d
docker compose ps
```

Check both services:

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

Create an order:

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: lesson-001" \
  -d '{"sku":"book-1","quantity":2}'
```

Repeat the same request. The idempotency key should return the original order
instead of reserving stock again.

Inspect the event:

```bash
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic order.created \
  --from-beginning \
  --timeout-ms 5000
```

Stop the example:

```bash
docker compose down
```

## Learn by breaking and improving

Perform these exercises in order:

1. Change the initial stock and observe reservation behavior.
2. Submit a quantity larger than the available stock and inspect the `409`
   response.
3. Repeat an order with the same `Idempotency-Key`.
4. Stop Kafka, submit an order, and inspect the failure logs.
5. Add a `customer_id` to the request and Kafka event.
6. Add an event consumer that writes an audit record.
7. Replace the Valkey stock counter with a durable database.
8. Add an outbox so a committed order and its Kafka event cannot diverge.

## WSL-native application servers

Docker can run only Kafka and Valkey while Python servers run directly in
WSL. This is convenient for debugging and live reload:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r order_service/requirements.txt
python -m pip install -r inventory_service/requirements.txt
```

Start FastAPI in one terminal:

```bash
export VALKEY_URL=redis://localhost:6379/0
python -m uvicorn inventory_service.app:app --host 0.0.0.0 --port 8001 --reload
```

Start Flask in another:

```bash
export INVENTORY_URL=http://localhost:8001
export VALKEY_URL=redis://localhost:6379/1
export KAFKA_BOOTSTRAP_SERVERS=localhost:9094
python -m flask --app order_service.app run --host 0.0.0.0 --port 8000 --debug
```

The Compose file uses Kafka `9092` for container traffic and `9094` for
host/WSL traffic.

## Production concerns

These examples are educational. A production system also needs:

- durable service-owned databases;
- authentication for users and internal service calls;
- request timeouts and carefully scoped retries;
- Kafka schemas, consumer groups, retries, and dead-letter topics;
- database transactions plus an outbox for reliable event publication;
- structured logs, metrics, traces, health checks, and readiness checks;
- secret management, TLS, dependency pinning, and resource limits.

The goal is not to add every production feature at once. Add one concern,
write a test or observable exercise, and then document what changed.
