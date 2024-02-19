# SSH to linode and run start/stop scripts. Get return code
# Also health check

import logging
import os
from typing import Callable

from core.config import CoreConfig
from servermanager.provisioner import LinodeProvisioner

log = logging.getLogger(__name__)


def build_start_closure(config: CoreConfig, provisioner: LinodeProvisioner) -> Callable:
    def start():
        entry_point_script = os.path.join(
            config.remote_server_dir, config.server_entry_point)
        log.info(f"Would normally run {entry_point_script} now")
    return start


def buid_stop_closure(config: CoreConfig, provisioner: LinodeProvisioner) -> Callable:
    def stop():
        stop_script = os.path.join(
            config.remote_server_dir, config.server_graceful_stop)
        log.info(f"Would normally run {stop_script} now")
    return stop
