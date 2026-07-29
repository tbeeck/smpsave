Quick-Start Guide
*****************

This page serves as a guide to get you set up using `smpsave` for your game of choice.

Overview
========

`smpsave` provides a command line interface, `smpsave-cli` which can be directly 
used to provision and deprovision a game server on demand. In order to facilitate this,
the user must provide three things:

1. **Server lifecycle shell scripts** which can start, stop and install the necessary dependencies for your game server.

2. **A configuration file** with properties that will be elaborated on later.

3. The complete set of **files for your game server**.

.. _requirements:

Requirements
============

Requirements for the system running `smpsave`, or 'facilitator':

* Python 3.9+
* Linux / macOS (not tested on Windows)
* ssh available on the $PATH
* rsync available on the $PATH
* An SSH key that can be used to authenticate an SSH session with the game server.

Requirements for the **game server**:

* Linux
* accepts ssh connections using the public key of the 'facilitator'
* rsync available on the $PATH
* Necessary libraries to support your server application

Installation
============

The recommended way to install smpsave is as a standalone tool with `uv <https://docs.astral.sh/uv/>`_,
which installs the ``smpsave-cli`` command into its own isolated environment:

.. code-block:: shell

	$ uv tool install smpsave

It can also be installed with pip:

.. code-block:: shell

	$ pip install smpsave

To install from a clone of the repository instead of PyPI:

.. code-block:: shell

	$ uv tool install .

Or, build the package and install the resulting artifact:

.. code-block:: shell

	$ uv build
	$ uv tool install dist/smpsave-$VERSION.tar.gz


Configuring smpsave
===================

smpsave reads its configurations from two files in the current working directory, in this order:

1. `config.ini`

2. `user.ini`

Properties set in `user.ini` take precedence over `config.ini`.

You can choose to only use one or the other, but it is recommended that if you wish to put sensitive 
information into one of these files, do so in `user.ini`.
Sensitive configuration properties should generally support being set via an environment variable.

See the :doc:`configuration` page for all available configuration values.

**At a minimum**, the properties in the 'core' namespace and the selected provisioner's
configuration namespace should be specified.

Server Lifecycle Scripts
========================

Because `smpsave` is agnostic to what game you wish to play, three 'lifecycle' shell scripts must 
be provided to enable `smpsave` to setup, start and stop your application:

1. 'bootstrap': This should install any required dependencies on the game server.
This is run before the game server files are synced. Note that these dependencies include
those that `smpsave` itself relies on being present on the game server, listed under
'Requirements for the **game server**' in the :ref:`requirements` section above.

2. 'start': This should start the game server application in a background process.
The game server does not need to accept connections by the time this script finishes running.

3. 'stop': This should gracefully stop the game server such that no data is lost.
In contrast to the 'start' script, this must run synchronously, and only exit once the server has
fully stopped.

Example scripts for a minecraft FTB server are provided below:

'bootstrap.sh'

.. literalinclude:: ../examples/feedthebeast/gameserver/bootstrap.sh
	:language: bash

'start.sh'

.. literalinclude:: ../examples/feedthebeast/gameserver/start.sh
	:language: bash

'stop.sh'

.. literalinclude:: ../examples/feedthebeast/gameserver/stop.sh
	:language: bash


Each of these scripts should be located alongside your game server files.


Putting It All Together
=======================

Once you've authored your configuration files and lifecycle scripts, you should have a folder that 
looks something like this:

.. code-block:: text

	smpsave-home
	├── config.ini
	└── server-files
		├── server_binary.bin
		├── start.sh
		├── stop.sh
		└── bootstrap.sh

In this case, the config.ini would likely contain these configuration values:

.. code-block:: INI

	[core]
	provisioner = linode
	local_server_dir = ./server-files/
	remote_server_dir = ~/server-files/
	remote_server_user = root
	server_bootstrap = bootstrap.sh
	server_entry_point = start.sh
	server_graceful_stop = stop.sh
	ssh_private_key_path = ~/.ssh/id_ed25519

	[linode]
	access_token = TOKEN
	public_key_path = ~/.ssh/id_ed25519.pub
	linode_type = g6-standard-4
	linode_image = linode/debian12
	linode_label = my-server
	linode_region = us-west

The `provisioner` property selects which provisioner backend to use, and each provisioner
reads its own configuration namespace: here, `linode` selects the Linode provisioner, which
is configured under `[linode]`. See :doc:`provisioners` for the available backends.

Note that `local_server_dir` and `remote_server_dir` should include a trailing slash.
These paths are passed directly to `rsync`, which treats a path with a trailing slash as
'the contents of this directory' and one without as 'this directory itself'.

The `ssh_private_key_path` property points `ssh` at the private key used to connect to the
game server (via `ssh -i`), so the key may live at any path rather than the default
`~/.ssh/id_*`. Two further `[core]` options control host-key handling:
`ssh_strict_host_key_checking` (default `accept-new`) and `ssh_known_hosts_path`
(default `/dev/null`). The defaults suit a freshly provisioned server that receives a new
host key each time, and they let smpsave run without a writable `~/.ssh` (useful in
containerized/Kubernetes deployments). Point `ssh_known_hosts_path` at a real, writable file
if you want trust-on-first-use host-key pinning across connections.

Within the directory containing your configuration file (in this case, `smpsave-home`)
you may now run `smpsave-cli` to start and stop your game server as needed.
