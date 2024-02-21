import logging

import click

from core.factory import build_provisioner
from discordbot.factory import get_bot_and_token


@click.group()
def cli():
    pass


@cli.command()
def start():
    provisioner = build_provisioner()
    provisioner.start()


@cli.command()
@click.option("-f", "--force", is_flag=True, help="Skip stop hooks and force stop.")
def stop(force: bool):
    provisioner = build_provisioner()
    provisioner.stop(force)


@cli.command()
def get_ip():
    provisioner = build_provisioner()
    print("Host:", provisioner.get_host())


@cli.command()
@click.argument("lifecycle", nargs=1, type=click.STRING)
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s  %(message)s')
    cli()
