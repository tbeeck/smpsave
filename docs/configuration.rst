Configuration
*************

Example configuration:

.. literalinclude:: ../examples/feedthebeast/config.ini
	:language: INI

Some configuration values can be overriden at runtime by an environment variable.

The classes below detail each available configuration option, the namespace they exist under,
their default values and their environment variable name, if applicable.

Core
====

Namespace: '[core]'

.. autoclass:: smpsave.core.config.CoreConfig
	:members:


Linode
======

Namespace: '[linode]'

.. autoclass:: smpsave.provisioning.LinodeProvisionerConfig
	:members:


Discord
=======

Namespace: '[discord]'

.. autoclass:: smpsave.discordbot.config.DiscordBotConfig
	:members:
