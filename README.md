# smpsave - Dynamic Provisioner for Private Game Servers
![PyPI - Version](https://img.shields.io/pypi/v/smpsave)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/smpsave)
[![Docs](https://github.com/tbeeck/smpsave/actions/workflows/docs.yml/badge.svg)](https://github.com/tbeeck/smpsave/actions/workflows/docs.yml)
[![PyPI Deploy](https://github.com/tbeeck/smpsave/actions/workflows/python-publish.yml/badge.svg)](https://github.com/tbeeck/smpsave/actions/workflows/python-publish.yml)

Save money hosting private game servers on demand.

* Start and stop your game server on demand through discord, let your friends do the same.
* Back up server files between restarts.
* Automatically shut off the server to save on costs.

See [documentation](https://www.timbeck.me/smpsave/) for more info.

![image](https://github.com/tbeeck/smpsave/assets/15240347/824f87da-94ff-46f2-b827-1da16da6cb7d)

![image](https://github.com/tbeeck/smpsave/assets/15240347/cdbd1bde-6624-4c5e-88e3-e887878b3fb9)


## Installing
Install via [pip](https://pypi.org/project/smpsave/):
```bash
pip install smpsave
```

Or install from source:
```bash
# in root dir of repository, with venv activated
pip install .
```

## Building
Setup and activate venv, install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Build the package:
```bash
python -m build
```

## Elevator pitch
Want a dedicated server powerful enough for your favorite game, but don't want to pay a cloud host
nearly $50 per month? Use `smpsave` to only pay for what you need.

Lets say you play on your private game server 10 hours a week.

Billing before using `smpsave`: 
* Linode 8gb shared CPU: 24/7 for all ~720 hours in a month: $48
* ~40 hours total usage ~94% of this cost is wasted money.

Billing after using `smpsave`:
* Linode 8gb shared CPU: 10 hours a week or ~40 hours a month: **$2.88**

While this could be achieved by having someone manually provision the server as needed, that individual becomes a single point of failure for keeping the game running. By exposing the server controls through discord, anyone in the group can spin up the server when they want to play.
