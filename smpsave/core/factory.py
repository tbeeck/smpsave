from smpsave.configuration import get_configurations
from smpsave.core.config import CORE_CONFIG_NAMESPACE, CoreConfig
from smpsave.core.filesync import build_backup_closure, build_upload_closure
from smpsave.core.server_lifecycle import (build_bootstrap_closure,
                                           build_clear_host_key_closure,
                                           build_start_closure,
                                           build_stop_closure)
from smpsave.provisioning import (LinodeProvisioner, LinodeProvisionerConfig,
                                  Provisioner)
from smpsave.provisioning.linode import LINODE_CONFIG_NAMESPACE


def build_provisioner() -> Provisioner:
    config = get_configurations(CORE_CONFIG_NAMESPACE, CoreConfig)
    if config.provisioner == 'linode':
        return build_linode_provisioner()
    raise Exception(f"Unknown provisioner: {config.provisioner}")


def build_linode_provisioner() -> LinodeProvisioner:
    core_config = get_configurations(CORE_CONFIG_NAMESPACE, CoreConfig)
    server_config = get_configurations(LINODE_CONFIG_NAMESPACE, LinodeProvisionerConfig)
    provisioner = LinodeProvisioner(server_config)

    provisioner.set_poststart_hooks([
        build_clear_host_key_closure(provisioner),
        build_bootstrap_closure(core_config, provisioner),
        build_upload_closure(core_config, provisioner),
        build_start_closure(core_config, provisioner),
    ])
    provisioner.set_prestop_hooks([
        build_stop_closure(core_config, provisioner),
        build_backup_closure(core_config, provisioner),
    ])
    return provisioner
