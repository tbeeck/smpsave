Quick-Start Guide
*****************

This page serves as a single page which should provide all of the information 
required to install and set up `smpsave` for use.

You may still wish to consult the :doc:`provisioners` page for more detailed 
information on your provisioner of choice.

Overview
========

`smpsave` provides a command line interface, `smpsave-cli` which can be directly 
used to provision and deprovision a game server on demand. In order to facilitate this,
the user must provide three things:

1. **Server lifecycle shell scripts** which can start, stop and install the necessary dependencies for your game server.

2. **A configuration file** with properties that will be elaborated on later.

3. The complete set of **files for your game server**.


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

Server Lifecycle Scripts
========================


