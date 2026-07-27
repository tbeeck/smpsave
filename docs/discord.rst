Discord Bot
***********

In addition to the command line interface, `smpsave` ships a Discord bot so that anyone in
your group can bring the game server up without needing access to the facilitator machine.

The bot is started with:

.. code-block:: shell

	$ smpsave-cli discord

Like every other subcommand, it reads its configuration from the present working directory,
using the `[discord]` namespace documented on the :doc:`configuration` page. The process runs
in the foreground until interrupted, so the facilitator machine must stay online for the bot
to respond.

Setting Up the Bot
==================

1. Create an application and a bot user in the
   `Discord developer portal <https://discord.com/developers/applications>`_.

2. Enable the **Message Content Intent** for the bot under the 'Bot' section of the portal.
   `smpsave` uses prefix commands (such as `!start`), which Discord will not deliver without
   this intent.

3. Copy the bot token into the `token` property of the `[discord]` namespace, or set it at
   runtime via the `DISCORD_TOKEN` environment variable. Since this value is sensitive, it is
   recommended to put it in `user.ini` rather than `config.ini`.

4. Decide which role may control the server and set `allowed_role` to that role's snowflake ID.
   To find it, enable Developer Mode in Discord (User Settings → Advanced), then right-click
   the role and choose 'Copy ID'.

5. Invite the bot to your server with permissions to read and send messages in the channel you
   intend to use.

Commands
========

All commands are prefixed with the configured `command_prefix`, which defaults to `!`.

`!start`
	Provision the machine, sync your game server files to it, and start the game server.
	Once the server is up, the bot replies with its IP address. Requires `allowed_role`.

`!stop`
	Gracefully stop the game server, back its files up to the facilitator machine, and
	deprovision the machine so that billing stops. Requires `allowed_role`.

`!status`
	Report whether the server is online, along with its IP address and the time remaining on
	the current lease. This command is available to everyone, not just holders of
	`allowed_role`.

`!extend`
	Extend the lease on a running server. Requires `allowed_role`.

Leases
======

To make sure a forgotten server does not keep accruing charges, a server started through the
bot is held under a *lease*:

* When the server starts, the lease is set to expire `lease_max_remaining_minutes` from now.

* `!extend` pushes the expiry out by `lease_increment_minutes`, but never further than
  `lease_max_remaining_minutes` from the present moment. In other words, that property caps
  how far into the future the shutdown can ever be scheduled, not the total session length.

* Once the remaining time falls below `lease_warning_threshold_minutes`, the bot posts a
  single warning in the channel that the command was issued from. Extending the lease re-arms
  the warning.

* When the lease expires, the bot announces the shutdown and stops the server exactly as if
  `!stop` had been used, backing up the server files in the process.

Leases are tracked in memory by the running bot process, so restarting the bot clears the
lease of an already-running server. Note also that a server started with `smpsave-cli start`
is not under a lease at all, and will keep running until it is stopped explicitly.
