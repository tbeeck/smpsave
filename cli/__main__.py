import logging

import click

from core.factory import build_linode_provisioner


@click.group()
def cli():
    pass


@cli.command()
def start():
    print("Running start")
    provisioner = build_linode_provisioner()
    provisioner.start()


@cli.command()
@click.option("-f", "--force", is_flag=True, help="Skip stop hooks and force stop.")
def stop(force: bool):
    print("Running stop")
    provisioner = build_linode_provisioner()
    provisioner.stop(force)


@cli.command()
def get_ip():
    provisioner = build_linode_provisioner()
    print("host", provisioner.get_host())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s  %(message)s')
    cli()
