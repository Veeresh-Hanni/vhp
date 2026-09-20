# Veeresh Hanni Project

`vhp` is the root Python package for the Veeresh Hanni Project's. It uses a
standard `src/` layout and is built with `uv`.

## Install and run

From the repository root:

```powershell
uv sync
uv run vhp
```

The package requires Python 3.14 or newer, as declared in `pyproject.toml`.
The installed `vhp` command is backed by `vhp.main`.

## Repository areas

- `src/vhp/` - the root package and command-line entry point.
- `microservices/` - independent service-system examples and architecture
  documentation.
- `DBDuck/`, `dompack/`, and `jospy/` - project components tracked as git
  submodules.

See [`microservices/polyglot-system/README.md`](microservices/polyglot-system/README.md)
for the Django, FastAPI, Flask, Valkey, Kafka, and rate-limiting system.

## Learn the VHP projects

The complete learning guide is available at
[`docs/index.md`](docs/index.md). It explains what each project teaches and
provides a recommended order:

1. Learn the root `vhp` package and `uv` workflow.
2. Learn JSON/API payload design with Jospy.
3. Learn multi-database access with DBDuck.
4. Learn Python environment and bundle automation with Dompack.
5. Learn service boundaries and event-driven systems in `microservices/`.

Project documentation:

- [DBDuck documentation](https://dbduck.org.in/)
- [Jospy documentation](https://jospy.readthedocs.io/)
- [Microservices examples](microservices/README.md)

## Support the project

If VHP, DBDuck, Jospy, Dompack, or the microservice examples help you learn
or build Python software, you can sponsor the project. Sponsorship supports
improving documentation, maintaining examples, and building new open-source
libraries and coding tools for Python developers.

- [Sponsor on GitHub](https://github.com/sponsors/Veeresh-Hanni)
- [Support through Razorpay](https://razorpay.me/@veereshhanni)

Thank you for supporting open-source learning and developer tooling.