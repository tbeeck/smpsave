import logging
from configparser import ConfigParser

import click

from servermanager import LinodeProvisioner, LinodeProvisionerConfig


def build_provisioner():
    config = ConfigParser()
    config.read("config.ini")
    server_config = LinodeProvisionerConfig(**config['linode'])
    return LinodeProvisioner(server_config)


@click.group()
def cli():
    pass


@cli.command()
def start():
    print("Running start")
    provisioner = build_provisioner()
    provisioner.start()


@cli.command()
def stop():
    print("Running stop")
    provisioner = build_provisioner()
    provisioner.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s  %(message)s')
    cli()
