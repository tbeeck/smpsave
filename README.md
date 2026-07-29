# smpsave - Dynamic Provisioner for Private Game Servers
![PyPI - Version](https://img.shields.io/pypi/v/smpsave)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/smpsave)
[![PyPI Deploy](https://github.com/tbeeck/smpsave/actions/workflows/python-publish.yml/badge.svg)](https://github.com/tbeeck/smpsave/actions/workflows/python-publish.yml)

Save money hosting private game servers on demand.

* Start and stop your game server on demand through Discord, let your friends do the same.
* Back up server files between restarts.
* Automatically shut off the server to save on costs.

See [documentation](https://www.timbeck.me/smpsave/) for more info.

![image](https://github.com/tbeeck/smpsave/assets/15240347/824f87da-94ff-46f2-b827-1da16da6cb7d)

![image](https://github.com/tbeeck/smpsave/assets/15240347/cdbd1bde-6624-4c5e-88e3-e887878b3fb9)


## Installing
Install as a standalone tool with [uv](https://docs.astral.sh/uv/):
```bash
uv tool install smpsave
```
This puts `smpsave-cli` on your `PATH` in its own isolated environment. You can also run it
without installing:
```bash
uvx --from smpsave smpsave-cli --help
```

Or install via [pip](https://pypi.org/project/smpsave/):
```bash
pip install smpsave
```

To install from a checkout of this repository:
```bash
uv tool install .
```

## Developing
Create the virtualenv and install all dependencies (including dev and docs tools):
```bash
uv sync
```

Run the CLI from the checkout:
```bash
uv run smpsave-cli --help
```

Build the docs:
```bash
uv run sphinx-build docs docs/_build
```

### Testing and code quality
Run the unit tests with [pytest](https://docs.pytest.org/):
```bash
uv run pytest
```

Lint with [ruff](https://docs.astral.sh/ruff/) (add `--fix` to auto-fix):
```bash
uv run ruff check
uv run ruff check --fix
```

Check or apply formatting with ruff (use `--check` to verify without changing files):
```bash
uv run ruff format --check
uv run ruff format
```

Type-check with [mypy](https://mypy.readthedocs.io/):
```bash
uv run mypy smpsave
```

## Building
Build the sdist and wheel into `dist/`:
```bash
uv build
```

## Releasing
1. Bump the version:
   ```bash
   uv version --bump patch   # or minor, major
   ```
2. Commit `pyproject.toml` and `uv.lock`, then push.
3. Publish a GitHub release with the tag `v<version>` (e.g. `v0.2.3`). This triggers the PyPI deploy workflow.

## Elevator pitch
Want a dedicated server powerful enough for your favorite game, but don't want to pay a cloud host
nearly $50 per month? Use `smpsave` to only pay for what you need.

Let's say you play on your private game server 10 hours a week.

Billing before using `smpsave`:
* Linode 8GB shared CPU, running 24/7 for all ~720 hours in a month: $48
* With only ~40 hours of actual play, ~94% of that cost is wasted money.

Billing after using `smpsave`:
* Linode 8GB shared CPU, running 10 hours a week or ~40 hours a month: **$2.88**

While this could be achieved by having someone manually provision the server as needed, that individual becomes a single point of failure for keeping the game running. By exposing the server controls through Discord, anyone in the group can spin up the server when they want to play.
