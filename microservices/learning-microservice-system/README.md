# Learn by doing: Flask + FastAPI + Kafka + Valkey

**Veeresh Hanni Project learning example.**

This is a deliberately small second microservice example:

```text
client -> Flask order-service -> FastAPI inventory-service
                         |              |
                         +--> Valkey    +--> Valkey stock
                         +--> Kafka: order.created
```

- **Flask `order-service`** owns order requests and publishes events.
- **FastAPI `inventory-service`** owns stock and reserves an item.
- **Valkey** stores idempotency keys and stock counters.
- **Kafka** stores the `order.created` event.

This is a learning project, not a production-ready checkout service.

The order service uses `kafka-python-ng`, not the older `kafka-python`
package. The older package fails during import on Python 3.13 with
`ModuleNotFoundError: No module named 'kafka.vendor.six.moves'`.

## Prerequisites

- Docker Desktop with Compose
- PowerShell, or a shell with `curl`

## Run the example

From this directory:

```powershell
docker compose build --no-cache order-service
docker compose up -d
docker compose ps
curl.exe http://localhost:8000/health
curl.exe http://localhost:8001/health
```

Both health requests should return `{"status":"ok"}`.

## Run the application servers inside WSL

This workflow keeps Docker for Kafka and Valkey, but runs the Flask and
FastAPI application servers directly inside Ubuntu on WSL. It is useful when
you want to edit, debug, and reload Python code without rebuilding images.

### 1. Install WSL prerequisites

In an Ubuntu WSL terminal:

```bash
sudo apt update
sudo apt install -y python3 python3-venv
python3 --version
docker --version
docker compose version
```

Docker Desktop must have WSL 2 integration enabled for the Ubuntu
distribution. From the Windows host, start the infrastructure containers:

```powershell
docker compose up -d valkey kafka
```

### 2. Create a WSL virtual environment

From the WSL checkout of this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r order_service/requirements.txt
python -m pip install -r inventory_service/requirements.txt
```

### 3. Start FastAPI in WSL

Use a first WSL terminal:

```bash
cd /path/to/vhp/microservices/learning-system
source .venv/bin/activate
export VALKEY_URL=redis://localhost:6379/0
python -m uvicorn inventory_service.app:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Start Flask in WSL

Use a second WSL terminal:

```bash
cd /path/to/vhp/microservices/learning-microservice-system
source .venv/bin/activate
export INVENTORY_URL=http://localhost:8001
export VALKEY_URL=redis://localhost:6379/1
export KAFKA_BOOTSTRAP_SERVERS=localhost:9094
python -m flask --app order_service.app run --host 0.0.0.0 --port 8000 --debug
```

In a third WSL terminal, run the same curl exercises from this document.
For a Windows browser or terminal, `http://localhost:8000` and
`http://localhost:8001` are normally reachable through WSL 2 localhost
forwarding.

Stop the two Python servers with `Ctrl+C`, then stop infrastructure from
PowerShell:

```powershell
docker compose down
```

The Compose file uses Kafka port `9092` for container-to-container traffic
and port `9094` for WSL/host traffic. If `localhost:9094` is unavailable from
WSL, use the Docker host address shown by
`ip route | awk '/default/ {print $3}'` and set
`KAFKA_BOOTSTRAP_SERVERS=<docker-host>:9094`. Keep the advertised Kafka
listener reachable from the WSL process.

## Exercise 1: inspect inventory

```powershell
curl.exe http://localhost:8000/inventory/book-1
```

The initial stock is 10. The request is proxied by Flask to FastAPI.

## Exercise 2: create an order

The `Idempotency-Key` prevents a client retry from creating a second order:

```powershell
curl.exe -X POST http://localhost:8000/orders `
  -H "Content-Type: application/json" `
  -H "Idempotency-Key: lesson-001" `
  -d "{\"sku\":\"book-1\",\"quantity\":2}"
```

Repeat the exact command. You should receive the same order response and
stock must not decrease a second time. Try a different key and quantity:

```powershell
curl.exe -X POST http://localhost:8000/orders `
  -H "Content-Type: application/json" `
  -H "Idempotency-Key: lesson-002" `
  -d "{\"sku\":\"book-1\",\"quantity\":3}"
```

## Exercise 3: observe Kafka

```powershell
docker compose exec kafka kafka-console-consumer `
  --bootstrap-server localhost:9092 `
  --topic order.created `
  --from-beginning `
  --timeout-ms 5000
```

The command exits after five seconds. Events contain `order_id`, `sku`, and
`quantity`.

## Exercise 4: tests and cleanup

```powershell
docker compose run --rm order-service python -m unittest discover
docker compose logs --tail=100 order-service
docker compose logs --tail=100 inventory-service
docker compose down
```

## Code tour

1. Open [`order_service/app.py`](order_service/app.py) and follow validation,
   idempotency, the HTTP call, and Kafka publication.
2. Open [`inventory_service/app.py`](inventory_service/app.py) and follow the
   FastAPI route and atomic Valkey decrement.
3. Open [`docker-compose.yml`](docker-compose.yml) and map containers to the
   diagram.
4. Change initial stock from `10`, rebuild, and repeat the order request.
5. Stop Kafka, create an order, inspect logs, then restart Kafka.

## Production follow-up exercises

- Add an outbox so a durable order write and Kafka event cannot diverge.
- Move stock to durable storage and add reservation expiration.
- Add service authentication, schema validation, retries, dead-letter topics,
  metrics, tracing, and contract tests.
