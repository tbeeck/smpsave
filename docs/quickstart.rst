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
* Linux / MacOS (not tested on windows)
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

Currently, smpsave can only be installed from source.

After cloning the repository, create and activate a virtual environment, then install the dependencies:

.. code-block:: shell

	$ python3 -m venv venv
	$ source venv/bin/activate
	(venv) $ pip install -r requirements.txt

Then, either install from source:

.. code-block:: shell

	(venv) $ pip install .

Or, build the package and install it:

.. code-block:: shell

	(venv) $ python -m build
	(venv) $ pip install dist/smpsave-$VERSION.tar.gz


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
the dependencies of `smpsave` itself, documented in the above :ref:`requirements` section.

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

In this case, the config.ini would likely contain these core configuration values:

.. code-block:: INI

	[core]
	local_server_dir = ./server-files/
	remote_server_dir = ~/server-files/
	remote_server_user = root
	server_bootstrap = bootstrap.sh
	server_entry_point = start.sh
	server_graceful_stop = stop.sh

Within the directory containing your configuration file (in this case, `smpsave-home`) 
you may now run `smpsave-cli` to start and stop your game sever as needed.
