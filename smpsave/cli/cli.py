import logging

import click

from smpsave.cli.log_config import configure_logging
from smpsave.core.factory import build_provisioner
from smpsave.discordbot.factory import get_bot_and_token


@click.group()
@click.option("--save-logs", is_flag=True, help="Use rotating log files")
def cli(save_logs: bool):
    configure_logging(logging.INFO, save_logs)


@cli.command()
def start():
    provisioner = build_provisioner()
    provisioner.start()


@cli.command()
@click.option("-f",
              "--force",
              is_flag=True,
              help="Skip stop hooks and directly deprovision the server.")
def stop(force: bool):
    provisioner = build_provisioner()
    provisioner.stop(force)


@cli.command()
def get_ip():
    provisioner = build_provisioner()
    print("Host:", provisioner.get_host())


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


@cli.command
def bot():
    bot, token = get_bot_and_token()
    bot.run(token)
