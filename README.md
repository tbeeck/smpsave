# smpsave - Dynamic Private Game Server Provisioner
Save money hosting private game servers on demand.

See documentation for more info (docs link)

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

## Installing
Install from source:
```bash
# in root dir of repository, with venv activated
pip install .
```

### Elevator pitch
Want a dedicated server powerful enough for your favorite game, but don't want to pay a cloud host
nearly $50 per month? Use `smpsave` to only pay for what you need.

Lets say you play on your private game server 10 hours a week.

Billing before using `smpsave`: 
* Linode 8gb shared CPU: 24/7 for all ~720 hours in a month: $48
* ~40 hours total usage ~94% of this cost is wasted money.

Billing after using `smpsave`:
* Linode 8gb shared CPU: 10 hours a week or ~40 hours a month: **$2.88**

While this could be achieved by having someone manually provision the server as needed, that individual becomes a single point of failure for keeping the game running. By exposing the server controls through discord, anyone in the group can spin up the server when they want to play.
