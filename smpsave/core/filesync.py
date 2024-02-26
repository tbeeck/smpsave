import logging
import subprocess
from typing import Callable

from smpsave.core.config import CoreConfig
from smpsave.provisioning import Provisioner

log = logging.getLogger(__name__)


def rsync(src: str, dst: str) -> int:
    command = ['rsync', '-avz', '-P', '-e',
               'ssh', src, dst]
    try:
        process = subprocess.run(command, check=False)
        return process.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error executing rsync command: {e}")
        return e.returncode


def build_upload_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def upload_server():
        source = config.local_server_dir
        destination = f"{config.remote_server_user}@{provisioner.get_host()}:{config.remote_server_dir}"
        log.info(f"Uploading server from {source} to {destination}")
        rsync(source, destination)
    return upload_server


def build_backup_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def backup_server():
        source = f"{config.remote_server_user}@{provisioner.get_host()}:{config.remote_server_dir}"
        destination = config.local_server_dir
        log.info(f"Backing up server from {source} to {destination}")
        rsync(source, destination)
    return backup_server
