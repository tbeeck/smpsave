import logging

import click

from bootstrapper.factory import build_linode_provisioner


@click.group()
def cli():
    pass


@cli.command()
def start():
    print("Running start")
    provisioner = build_linode_provisioner()
    provisioner.start()


@cli.command()
def stop():
    print("Running stop")
    provisioner = build_linode_provisioner()
    provisioner.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s  %(message)s')
    cli()
