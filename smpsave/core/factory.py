import logging

from smpsave.core.config import CORE_CONFIG_NAMESPACE, CoreConfig, read_config_files
from smpsave.core.filesync import build_backup_closure, build_upload_closure
from smpsave.core.sever_lifecycle import (buid_stop_closure, build_bootstrap_closure, build_clear_host_key_closure,
                                  build_start_closure)
from smpsave.provisioning import (LinodeProvisioner, LinodeProvisionerConfig,
                          Provisioner)
from smpsave.provisioning.linode import LINODE_CONFIG_NAMESPACE

log = logging.getLogger(__name__)


def build_provisioner() -> Provisioner:
    config = read_config_files()
    core_config = CoreConfig(**config[CORE_CONFIG_NAMESPACE])
    if core_config.provisioner == 'linode':
        return build_linode_provisioner()
    raise Exception(f"Unknown provisioner: {core_config.provisioner}")


def build_linode_provisioner() -> LinodeProvisioner:
    config = read_config_files()
    core_config = CoreConfig(**config[CORE_CONFIG_NAMESPACE])
    server_config = LinodeProvisionerConfig(**config[LINODE_CONFIG_NAMESPACE])
    provisioner = LinodeProvisioner(server_config)

    provisioner.set_poststart_hooks([
        build_clear_host_key_closure(provisioner),
        build_bootstrap_closure(core_config, provisioner),
        build_upload_closure(core_config, provisioner),
        build_start_closure(core_config, provisioner),
    ])
    provisioner.set_prestop_hooks([
        buid_stop_closure(core_config, provisioner),
        build_backup_closure(core_config, provisioner),
    ])
    return provisioner
