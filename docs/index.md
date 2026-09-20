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

libraries
microservices
microservice-stack
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

The root VHP package is the entry point for the repository. It is intentionally
small so that the packaging concepts are easy to see before moving to the
larger libraries. It demonstrates a `src/` layout, package metadata, a build
backend, a lock file, and an installed command-line entry point.

The package teaches:

- how Python discovers code inside a `src/` directory;
- how `pyproject.toml` describes a package and its dependencies;
- how a console script maps a shell command to a Python function;
- how `uv sync` creates a reproducible development environment;
- how a package can be tested independently from the projects it documents.

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

**Next exercise:** add a `--version` option to the command, expose the version
from one source of truth, and add a test for the command output. The point is
to learn the relationship between package metadata, importable code, and
user-facing commands.

### 2. Learn JSON and REST payloads with Jospy

Jospy solves a common application problem: every API needs to convert,
validate, clean, and shape data before it is returned to a client. Instead of
reimplementing these small transformations in every route, Jospy provides
focused helpers and a chainable data layer.

Jospy is useful when an application needs:

- JSON text, bytes, files, and Python values
- null and default handling
- field selection and filtering
- nested dot-path access
- consistent API and pagination envelopes
- a chainable `data()` layer

The important design boundary is that Jospy handles data shaping, not business
rules, authentication, database access, or HTTP transport. A route should
still decide whether a user is allowed to see a record and whether the input
is valid for the domain.

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

**What to study next:**

1. `clean()` and JSON serialization of dates, UUIDs, enums, and decimals.
2. `filter_data()` for public/private field boundaries.
3. `get_path()` and `set_path()` for nested request data.
4. `api_response()` and `paginated()` for stable client contracts.
5. The `DataLayer` implementation to understand fluent, non-route-specific
   transformations.

### 3. Learn data access with DBDuck

DBDuck provides a Universal Data Object Model (UDOM): a common Python API for
SQL, MongoDB, Neo4j, Qdrant, and asynchronous workflows. Its purpose is to
keep application-level operations recognizable while adapters handle backend
specific connection and query details.

DBDuck is useful for learning:

- how a common interface can hide backend-specific clients;
- how SQL, document, graph, and vector workloads differ;
- how transactions and lifecycle operations should be exposed;
- how query builders can make filters composable;
- how adapters, routers, validation, and error types form a library design.

It is not a promise that all databases have identical capabilities. Graph
relationships and vector similarity require operations that do not map to a
simple SQL CRUD interface, so DBDuck exposes backend-specific helpers where
that distinction matters.

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

**Suggested DBDuck progression:**

1. Start with SQLite and inspect the generated records.
2. Add a transaction that creates related data and rolls back on failure.
3. Replace direct calls with the fluent query builder.
4. Run the same repository operation against PostgreSQL or MongoDB.
5. Add a graph relationship and query related nodes.
6. Create a Qdrant collection and compare vector search with exact filtering.
7. Read the adapter and connection-manager code to see where backend
   differences are isolated.

Use the official [DBDuck documentation](https://dbduck.org.in/) for the latest
API and backend support details.

### 4. Learn environment automation with Dompack

Dompack packages useful dependency groups as named bundles. It is useful when
you are starting a project and want a repeatable developer setup without
copying a long list of unrelated packages into every project.

The bundle idea separates two concerns:

- the project declares the libraries it truly needs;
- the developer can install a practical toolset for a domain such as web
  development, databases, testing, or security.

Dompack also demonstrates installer selection, aliases, package discovery,
and fallback behavior for externally managed Linux Python environments.

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

**Good engineering practice:** treat bundles as starting points, not as a
replacement for a project's lock file. After bootstrapping, record the exact
dependencies and versions required by the application.

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

### 6. Compare the microservice communication styles

The examples intentionally show more than one integration style:

| Style | Example | Best lesson |
| --- | --- | --- |
| Synchronous HTTP | Flask order service to FastAPI inventory service | A caller needs an immediate decision |
| Asynchronous messaging | User events through NATS or order events through Kafka | A producer should not wait for every downstream action |
| Shared short-lived state | Valkey idempotency and counters | Multiple replicas need coordinated temporary state |
| Gateway routing | Django gateway or Flask edge | Clients should not need to know every internal service |

When studying a service, identify the timeout, retry policy, ownership of
data, and failure response for every network call. A diagram alone is not
enough: reliable systems make failure behavior explicit.

## Project-by-project outcomes

After working through the repository, you should be able to:

- package a Python project and expose a command-line entry point;
- build predictable JSON responses without leaking private fields;
- choose between CRUD, document, graph, and vector data access patterns;
- create a repeatable virtual environment and dependency workflow;
- split a feature into services with explicit ownership;
- decide when to use HTTP and when to publish an event;
- implement idempotency for retried requests;
- use Valkey for short-lived coordination rather than durable business data;
- design a Kafka event envelope and an idempotent consumer;
- explain why production systems need an outbox, observability, and
  authenticated service communication.

## A complete learning project

Combine the projects by building a small catalog application:

1. Use Dompack to prepare a web and testing environment.
2. Use FastAPI or Flask for the HTTP API.
3. Use Jospy to shape public responses and pagination.
4. Use DBDuck with SQLite for the first persistence implementation.
5. Add a `catalog.item.created` Kafka event.
6. Store a short-lived response cache or request idempotency key in Valkey.
7. Add tests for validation, duplicate requests, and insufficient stock.
8. Document the service contract and run the system through Docker or WSL.

This exercise is intentionally incremental. Start with one process and one
database, then introduce a second service only when there is a clear ownership
or scaling reason. That approach teaches the trade-offs of microservices
without turning every feature into deployment overhead.

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
