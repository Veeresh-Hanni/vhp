# Veeresh Hanni Project learning guide

Welcome to the **Veeresh Hanni Project's (VHP)**. This repository brings
together Python libraries, developer tooling, and microservice examples built
by Veeresh Hanni.

The hosted version of this guide is available at
[vhp.readthedocs.io](https://vhp.readthedocs.io/).

The goal of this guide is to make the repository useful as a learning path:
read a small project, run it, change it, and then use the same idea in a
larger service.

```{toctree}
:maxdepth: 2
:caption: Learning modules

microservices
```

## Projects at a glance

| Project | What it teaches | Start here |
| --- | --- | --- |
| `vhp` | Python package layout, `uv`, console scripts | [`src/vhp/__init__.py`](../src/vhp/__init__.py) |
| [Jospy](https://jospy.readthedocs.io/) | JSON conversion, payload shaping, REST response envelopes | [source README](https://github.com/Veeresh-Hanni/jospy/blob/main/README.md) |
| [DBDuck](https://dbduck.org.in/) | One data API across SQL, NoSQL, graph, and vector stores | [source README](https://github.com/Veeresh-Hanni/DBDuck/blob/main/README.md) |
| [Dompack](https://github.com/Veeresh-Hanni/dDrive/tree/main/dompack) | Domain-based Python dependency bundles and installation | [source README](https://github.com/Veeresh-Hanni/dDrive/blob/main/dompack/README.md) |
| Microservices | Django, FastAPI, Flask, Kafka, Valkey, NATS, Docker, and WSL workflows | [source README](https://github.com/Veeresh-Hanni/vhp/tree/main/microservices/README.md) |

## Recommended learning path

### 1. Start with the VHP package

The root package is intentionally small. It demonstrates a `src/` layout,
package metadata, and an installed command-line entry point.

From WSL or PowerShell:

```bash
uv sync
uv run vhp
```

Expected output:

```text
Hello from vhp 0.1.0!
```

Read:

- [`pyproject.toml`](../pyproject.toml) for metadata, Python requirements, and
  the `vhp` script.
- [`src/vhp/__init__.py`](../src/vhp/__init__.py) for the package entry point.

Try changing the greeting, running `uv run vhp`, and inspecting the generated
lock file. This is the smallest safe way to learn the repository workflow.

### 2. Learn JSON and REST payloads with Jospy

Jospy is a small, dependency-free utility package for common API payload
operations:

- JSON text, bytes, files, and Python values
- null and default handling
- field selection and filtering
- nested dot-path access
- consistent API and pagination envelopes
- a chainable `data()` layer

Install the package while learning:

```bash
python -m pip install jospy
```

Read the [hosted Jospy docs](https://jospy.readthedocs.io/) or the local
`jospy/docs/index.md` file. Then try:

```python
from jospy import api_response, filter_data, to_json, to_python

payload = to_python('{"name": "Ada", "password": "secret"}')
public = filter_data(payload, exclude=["password"])
print(to_json(api_response(public, message="ok"), pretty=True))
```

Learning exercise: add a `request_id` field to the response metadata without
including private fields in the public payload.

### 3. Learn data access with DBDuck

DBDuck provides a Universal Data Object Model (UDOM): a common Python API for
SQL, MongoDB, Neo4j, Qdrant, and asynchronous workflows.

Read the official documentation at **[dbduck.org.in](https://dbduck.org.in/)**
or the local `DBDuck/README.md` file.

Start with SQLite because it requires no server:

```bash
python -m pip install "dbduck"
```

```python
from DBDuck import UDOM

db = UDOM(url="sqlite:///learning.db")
db.create("users", {"id": 1, "name": "Ada", "active": True})
print(db.find("users", where={"active": True}))
```

Study these concepts in order:

1. `create`, `find`, `update`, `delete`, and `count`.
2. Transactions and `ping`/`close`.
3. The fluent query builder.
4. Backend adapters and normalized errors.
5. MongoDB, graph, vector, and async adapters.

Learning exercise: implement the same small “active users” example with
SQLite and MongoDB, then compare what the application code does and what the
adapter owns.

### 4. Learn environment automation with Dompack

Dompack packages useful dependency groups as named bundles. It is useful when
you are starting a project and want a repeatable developer setup.

From the `dompack/README.md` file:

```bash
python -m pip install dompk
dompack list
dompack install pydev
dompack doctor
```

Important detail: the PyPI package name is `dompk`, while the command names
are `dompack` and `dompk`.

Learning exercise: inspect the `pyproject.toml` optional dependencies, create
a small bundle for your own project, and verify it in a new virtual
environment.

### 5. Learn microservices

The `microservices/` directory contains separate
examples. Learn them in this order:

1. **Django + NATS**: `microservice-system/` teaches
   an API gateway, user service, notification service, JWT authentication,
   and asynchronous events.
2. **Polyglot architecture**: `polyglot-system/` documents Django,
   FastAPI, Flask, Kafka, Valkey, and rate limiting.
3. **Runnable order system**: `learning-microservice-system/` lets you create
   an order, reserve inventory, store idempotency state in
   Valkey, and publish `order.created` to Kafka.

For the runnable system, follow its Docker and WSL instructions in the
project checkout:

```bash
cd microservices/learning-microservice-system
docker compose up --build -d
curl http://localhost:8000/health
```

Then create an order:

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: lesson-001" \
  -d '{"sku":"book-1","quantity":2}'
```

The most important learning questions are:

- Which service owns each piece of data?
- What happens when a request is retried?
- Which calls are synchronous HTTP calls?
- Which changes become Kafka events?
- Which state belongs in Valkey, and which state needs durable storage?
- How would an outbox, authentication, retries, and observability improve it?

## How the projects fit together

```text
Jospy       -> clean JSON and REST payloads
DBDuck      -> access application data
Dompack     -> prepare a Python development environment
VHP         -> package and organize the projects
Microservices -> combine APIs, data, messaging, and operations
```

For example, a future service can use Jospy for response envelopes, DBDuck
for persistence, Dompack to bootstrap dependencies, and the microservice
patterns for service boundaries and event delivery.

## Repository and submodules

DBDuck, Dompack, Jospy, and the existing microservice system are tracked as
git submodules or independent project areas. To initialize submodules in a
fresh clone:

```bash
git submodule update --init --recursive
```

Do not commit virtual environments, `.env` files, build output, or generated
cache directories. Use each project's own README for project-specific tests
and release commands.

## Safety and production notes

The examples are designed for learning. Before using them in production:

- pin and audit dependencies;
- use secret management instead of example keys;
- use durable, service-owned databases;
- authenticate internal service calls;
- add timeouts, retry policy, idempotency, and dead-letter handling;
- add structured logs, metrics, traces, health checks, and readiness checks;
- validate event schemas and plan Kafka/Valkey persistence and access control.

## Next project exercise

Choose one small feature and implement it end to end:

1. Add a `customer_id` to the learning order request.
2. Validate it at the Flask boundary.
3. Include it in the Kafka event.
4. Add a consumer that writes an audit record.
5. Document the event contract and test duplicate delivery.

That exercise connects payload design, service boundaries, messaging, and
idempotency across the VHP projects.

## Support open source

Your support helps me (Veeresh Hanni) improve the documentation, maintain the
learning examples, and build new open-source libraries and coding tools for
Python developers.

- [Sponsor on GitHub](https://github.com/sponsors/Veeresh-Hanni)
- [Support through Razorpay](https://razorpay.me/@veereshhanni)

Thank you for helping make Python learning resources and open-source
development work more accessible.
