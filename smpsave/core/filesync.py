import logging
import shlex
import subprocess
from typing import Callable

from smpsave.core.config import CoreConfig
from smpsave.core.server_lifecycle import ssh_options
from smpsave.provisioning import Provisioner

log = logging.getLogger(__name__)


def rsync(config: CoreConfig, src: str, dst: str) -> int:
    ssh_command = shlex.join(["ssh", *ssh_options(config)])
    command = ["rsync", "-avz", "-P", "-e", ssh_command, src, dst]
    try:
        log.debug(f"Running {command}")
        process = subprocess.run(command, check=False)
        log.debug(f"rsync exited with code {process.returncode}")
        if process.returncode != 0:
            log.warning(
                f"rsync from '{src}' to '{dst}' exited with code {process.returncode}"
            )
        return process.returncode
    except subprocess.CalledProcessError as e:
        log.exception(f"Error executing rsync command {command}")
        return e.returncode


def build_upload_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def upload_server():
        source = config.local_server_dir
        destination = (
            f"{config.remote_server_user}@{provisioner.get_host()}"
            f":{config.remote_server_dir}"
        )
        log.info(f"Uploading server from {source} to {destination}")
        rsync(config, source, destination)

    return upload_server


def build_backup_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def backup_server():
        source = (
            f"{config.remote_server_user}@{provisioner.get_host()}"
            f":{config.remote_server_dir}"
        )
        destination = config.local_server_dir
        log.info(f"Backing up server from {source} to {destination}")
        rsync(config, source, destination)

    return backup_server
