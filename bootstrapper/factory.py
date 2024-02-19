from configparser import ConfigParser

from servermanager import LinodeProvisioner, LinodeProvisionerConfig


def build_linode_provisioner() -> LinodeProvisioner:
    config = ConfigParser()
    config.read("config.ini")
    server_config = LinodeProvisionerConfig(**config['linode'])
    provisioner = LinodeProvisioner(server_config)
    provisioner.poststart_hooks = [
        # todo
    ]
    provisioner.prestop_hooks = [
        # todo
    ]
    return provisioner
