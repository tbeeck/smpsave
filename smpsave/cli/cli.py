import logging

import click

from smpsave.__init__ import __version__
from smpsave.cli.log_config import configure_logging
from smpsave.core.factory import build_provisioner
from smpsave.discordbot.factory import get_bot_and_token


@click.group()
@click.option("--save-logs",
              is_flag=True,
              help="Write rotating log files under the 'logs' subdirectory.")
def cli(save_logs: bool):
    """
    Command line interface for smpsave. All subcommands use the configuration files
    in the present working directory.
    """
    configure_logging(logging.INFO, save_logs)


@cli.command(help="Provision and start the gameserver.")
def start():
    provisioner = build_provisioner()
    provisioner.start()


@cli.command(help="""\
Stop and deprovision the gameserver.
Pre-stop lifecycle hooks will back up the remote gameserver files to the local machine.
""")
@click.option("-f",
              "--force",
              is_flag=True,
              help="Skip stop hooks and immediately deprovision the server. This destroys any data on the remote machine.")
def stop(force: bool):
    provisioner = build_provisioner()
    provisioner.stop(force)


@cli.command(help="Check if the server is online, and if it is, print its IP address.")
def status():
    provisioner = build_provisioner()
    ip = provisioner.get_host()
    if not ip:
        print("Server is not up.")
    else:
        print("Server is up, IP:", ip)


@cli.command(help="Starts the discord bot.")
def discord():
    bot, token = get_bot_and_token()
    bot.run(token)


@cli.command(help="Re-run lifecycle hooks for a particular stage. For testing/development only.")
@click.argument("lifecycle",
                nargs=1,
                type=click.STRING)
def run(lifecycle: str):
    provisioner = build_provisioner()
    if lifecycle == "start":
        provisioner.run_poststart_hooks()
    elif lifecycle == "stop":
        provisioner.run_prestop_hooks()
    else:
        print("Unknown lifecycle stage:", lifecycle)
        exit(1)

@cli.command(help="Print the current version of smpsave.")
def version():
    print(__version__)
