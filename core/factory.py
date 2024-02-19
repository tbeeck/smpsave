import logging
from configparser import ConfigParser

from core.config import CORE_CONFIG_NAMESPACE, CoreConfig
from core.filesync import rsync
from servermanager import LinodeProvisioner, LinodeProvisionerConfig
from servermanager.config import LINODE_CONFIG_NAMESPACE

log = logging.getLogger(__name__)


def build_linode_provisioner() -> LinodeProvisioner:
    config = ConfigParser()
    config.read("config.ini")
    server_config = LinodeProvisionerConfig(**config[LINODE_CONFIG_NAMESPACE])
    provisioner = LinodeProvisioner(server_config)

    core_config = CoreConfig(**config[CORE_CONFIG_NAMESPACE])

    def upload_server():
        source = core_config.local_server_dir
        destination = f"{core_config.remote_server_user}@{provisioner.get_host()}:{core_config.remote_server_dir}"
        log.info(f"Uploading server from {source} to {destination}")
        rsync(source, destination)

    def backup_server():
        source = f"{core_config.remote_server_user}@{provisioner.get_host()}:{core_config.remote_server_dir}"
        destination = core_config.local_server_dir
        log.info(f"Backing up server from {source} to {destination}")
        rsync(source, destination)

    provisioner.poststart_hooks = [
        upload_server
    ]
    provisioner.prestop_hooks = [
        backup_server
    ]
    return provisioner
