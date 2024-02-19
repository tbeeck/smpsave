import logging

import click

from bootstrap.factory import build_linode_provisioner


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

@cli.command()
def get_ip():
    provisioner = build_linode_provisioner()
    print("host", provisioner.get_host())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s  %(message)s')
    cli()
