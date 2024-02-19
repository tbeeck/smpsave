import logging
from configparser import ConfigParser

from core.config import CORE_CONFIG_NAMESPACE, CoreConfig, get_all_configurations
from core.filesync import build_backup_closure, build_upload_closure
from core.sever_lifecycle import (buid_stop_closure, build_bootstrap_closure,
                                  build_start_closure)
from servermanager import LinodeProvisioner, LinodeProvisionerConfig
from servermanager.config import LINODE_CONFIG_NAMESPACE

log = logging.getLogger(__name__)


def build_linode_provisioner() -> LinodeProvisioner:
    config = get_all_configurations()
    core_config = CoreConfig(**config[CORE_CONFIG_NAMESPACE])
    server_config = LinodeProvisionerConfig(**config[LINODE_CONFIG_NAMESPACE])
    provisioner = LinodeProvisioner(server_config)

    provisioner.poststart_hooks = [
        build_bootstrap_closure(core_config, provisioner),
        build_upload_closure(core_config, provisioner),
        build_start_closure(core_config, provisioner),
    ]
    provisioner.prestop_hooks = [
        buid_stop_closure(core_config, provisioner),
        build_backup_closure(core_config, provisioner),
    ]
    return provisioner
