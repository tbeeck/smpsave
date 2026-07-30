import logging
import shlex
import subprocess
from typing import Callable

from smpsave.core.config import CoreConfig
from smpsave.core.server_lifecycle import ssh_options
from smpsave.provisioning import Provisioner

log = logging.getLogger(__name__)


def _as_sync_source(path: str) -> str:
    """
    Normalize a directory path for use as an rsync source. rsync only copies a
    directory's *contents* into the destination when the source ends with a
    trailing slash; without it the directory itself is nested one level deeper.
    Appending the slash here means users don't have to remember to configure
    trailing slashes on their local/remote server paths.
    """
    return path if path.endswith("/") else path + "/"


def ensure_remote_dir(config: CoreConfig, user: str, host: str, remote_dir: str):
    """
    Guarantee the remote destination directory exists before rsync runs. rsync
    creates the final path component but not missing parent directories, so a
    fresh instance whose remote_server_dir hasn't been created yet would
    otherwise fail the upload.
    """
    # Left unquoted so the remote shell expands '~' in configured paths.
    command = [
        "ssh",
        *ssh_options(config),
        f"{user}@{host}",
        f"mkdir -p {remote_dir}",
    ]
    log.debug(f"Ensuring remote directory exists: {command}")
    returncode = subprocess.call(command, timeout=100)
    if returncode != 0:
        raise Exception(
            f"Failed to create remote directory '{remote_dir}' on {host}, "
            f"got exit code {returncode}"
        )


def rsync(config: CoreConfig, src: str, dst: str) -> int:
    ssh_command = shlex.join(["ssh", *ssh_options(config)])
    command = ["rsync", "-avz", "-P", "-e", ssh_command, _as_sync_source(src), dst]
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
        host = provisioner.get_host()
        destination = (
            f"{config.remote_server_user}@{host}"
            f":{config.remote_server_dir}"
        )
        ensure_remote_dir(
            config, config.remote_server_user, host, config.remote_server_dir
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
