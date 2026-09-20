# VHP libraries and tools

This page explains the problem each VHP library solves, the boundary of its
responsibility, and a practical way to study its implementation. The examples
are intentionally small, but the design questions apply to larger Python
projects.

## Jospy: predictable JSON and REST payloads

### Problem

Web applications repeatedly perform the same data-shaping work:

- convert JSON input to Python values;
- remove private fields before responding;
- fill optional values;
- access nested fields safely;
- return one response shape for success and errors;
- paginate collections consistently.

Duplicating these operations in every route creates inconsistent APIs. One
endpoint may return `{"data": ...}`, another may return a bare list, and a
third may accidentally expose an internal field. Jospy provides small,
composable functions for this boundary.

### Main concepts

**Conversion** turns JSON strings, bytes, files, and Python values into one
working representation. `to_python()` and `to_json()` are useful at the edge
of an application, where serialization details should not leak into domain
code.

**Cleaning** makes values JSON-friendly. Dates, UUIDs, decimals, enums, paths,
tuples, sets, and dataclasses need an explicit representation before they can
be sent over HTTP.

**Filtering** defines a public projection of data. `pick()` and `omit()` are
simple field operations; `filter_data()` adds predicates, list handling, and
null/empty removal. This is useful for response shaping, but it is not an
authorization system. Permission checks still belong in the service layer.

**Nested paths** provide a small vocabulary for structured payloads:
`get_path(payload, "user.profile.email")` and
`set_path(payload, "user.profile.email", value)`. This is useful for
configuration and forms, where nested data is common.

**Response envelopes** make client code easier to maintain. `api_response()`
and `paginated()` define a predictable shape with data, status, messages,
errors, and metadata.

### Example

```python
from jospy import api_response, filter_data, paginated

users = [
    {"id": 1, "name": "Ada", "role": "admin", "password_hash": "private"},
    {"id": 2, "name": "Grace", "role": "developer", "password_hash": "private"},
]

public_users = filter_data(users, exclude=["password_hash"])
response = paginated(public_users, page=1, per_page=25)
body = api_response(response, message="Users loaded")
```

### Study exercises

1. Add a response metadata field containing a request ID.
2. Create a serializer for a dataclass containing a `datetime` and a UUID.
3. Use a predicate to return only active records.
4. Add a test proving `password_hash` never appears in a public response.
5. Compare a bare list response with a paginated response and document the
   client-side trade-off.

Read the complete [Jospy documentation](https://jospy.readthedocs.io/) for the
current helper reference.

## DBDuck: a common data access vocabulary

### Problem

An application may start with SQLite, move to PostgreSQL, add MongoDB for
document data, and later use Neo4j or Qdrant for a different workload. If each
feature directly imports a different client, connection setup, error handling,
health checks, and test strategy become scattered.

DBDuck's Universal Data Object Model (UDOM) provides a common vocabulary for
basic operations while keeping backend adapters responsible for backend
details. It is a learning tool for understanding abstraction boundaries as
well as a database library.

### Main concepts

**Connection management** owns URLs, clients, lifecycle, and health checks.
Application code should not create a new database client for every request.

**Adapters** translate common operations to SQLAlchemy, MongoDB, Neo4j, or
Qdrant. An adapter should normalize common behavior without pretending that
all databases have the same data model.

**CRUD and queries** cover common application work: create, find, update,
delete, count, ordering, filtering, and pagination. The fluent query builder
helps compose these operations.

**Transactions** protect related changes in transactional stores. A graph
relationship or a vector upsert may have different atomicity rules, so code
must understand the selected backend rather than assuming every operation has
the same guarantees.

**Specialized operations** preserve useful differences:

- graph relationships, traversal, and shortest paths for Neo4j;
- collection creation, vector upserts, and similarity searches for Qdrant;
- asynchronous connection and query methods for async applications.

### Example progression

```python
from DBDuck import UDOM

db = UDOM(url="sqlite:///learning.db")
db.create("users", {"id": 1, "name": "Ada", "active": True})
active = db.table("users").where(active=True).order("name").find()
print(active)
db.close()
```

Move through these stages:

1. Run CRUD operations against SQLite.
2. Add validation for required fields.
3. Add a transaction for two related writes.
4. Replace direct methods with the query builder.
5. Run the same repository operation against PostgreSQL or MongoDB.
6. Add a graph relationship and a vector search as separate features.
7. Read the adapter code and record what cannot be shared between backends.

Read the latest [DBDuck documentation](https://dbduck.org.in/) before using a
backend-specific feature.

## Dompack: repeatable developer setup

### Problem

New Python projects often need the same groups of tools: HTTP clients,
FastAPI, Django, database drivers, testing, formatting, security, or data
science. A new developer should be able to create an environment without
manually searching for every package.

Dompack, published as `dompk`, groups related dependencies into named bundles.
It is a bootstrap tool, not an application dependency lock file.

### Main concepts

- **Bundles** describe a domain such as `web`, `db`, `fa`, `dj`, `testing`, or
  `security`.
- **Aliases** make common workflows discoverable, such as `pydev` and
  `bootstrap`.
- **Installer backends** allow `uv` or `pip` to be selected.
- **Environment fallback** handles Linux systems where the global interpreter
  is externally managed.
- **Doctor and search commands** help inspect available setup options.

### Example

```bash
python -m pip install dompk
dompack list
dompack install pydev
dompack doctor
dompack req fastapi
```

After bootstrapping, inspect the generated environment and record the
application's actual dependencies in its own `pyproject.toml` or lock file.
This keeps a convenient learning bundle separate from reproducible production
installation.

### Study exercises

1. Compare the `fa`, `dj`, and `testing` bundles.
2. Run the same install with `--installer uv` and `--installer pip`.
3. Create a small bundle for the learning order service.
4. Test the command on a fresh WSL virtual environment.
5. Explain why a bundle should not replace a project lock file.

## How the libraries work together

A service can use the projects at different boundaries:

```text
Dompack -> prepares a developer environment
VHP     -> packages the project and documents the workflow
DBDuck  -> persists domain data
Jospy   -> shapes JSON at the HTTP boundary
Kafka   -> publishes durable domain events
Valkey  -> stores short-lived coordination state
```

These responsibilities should remain distinct. Jospy should not become a
database layer, Valkey should not silently become the source of truth for
orders, and a dependency bundle should not decide an application's runtime
architecture.
