# SSH to linode and run start/stop scripts. Get return code
# Also health check

import logging
import os
import subprocess
import time
from typing import Callable

from smpsave.core.config import CoreConfig
from smpsave.provisioning.provisioner import Provisioner

log = logging.getLogger(__name__)

# A freshly provisioned instance reports "running" before its SSH daemon is
# accepting connections, so we poll before running any remote hooks.
SSH_READY_RETRIES = 24
SSH_READY_INTERVAL_SECONDS = 5


def ssh_options(config: CoreConfig) -> list[str]:
    """
    Build the common 'ssh' option flags from configuration, so every SSH-based
    command uses an explicit identity file and consistent host-key handling
    without relying on defaults or a writable '~/.ssh'.
    """
    return [
        "-i",
        os.path.expanduser(config.ssh_private_key_path),
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        f"StrictHostKeyChecking={config.ssh_strict_host_key_checking}",
        "-o",
        f"UserKnownHostsFile={os.path.expanduser(config.ssh_known_hosts_path)}",
    ]


def run_remote_script(config: CoreConfig, user: str, host: str, script_path: str):
    working_dir, script_name = os.path.split(script_path)
    cmd = f"cd {working_dir} ; ./{script_name}"
    command = ["ssh", *ssh_options(config), f"{user}@{host}", cmd]

    try:
        log.debug(f"Running {command} on {user}@{host}")
        returncode = subprocess.call(command, timeout=100)
        log.debug(f"Remote script '{script_path}' exited with code {returncode}")
        if returncode != 0:
            raise Exception(
                f"Failed to run {command} on host {host}, got exit code {returncode}"
            )
    except subprocess.CalledProcessError as e:
        log.error(
            f"Error executing remote script '{script_path}', exit code {e.returncode}"
        )
        raise e


def run_local_script_remotely(
    config: CoreConfig, user: str, host: str, script_path: str
):
    command = ["ssh", *ssh_options(config), f"{user}@{host}", "bash -s"]

    try:
        with open(script_path) as f:
            script_content = f.read()
        log.debug(
            f"Piping local script '{script_path}' "
            f"({len(script_content)} bytes) to {user}@{host}"
        )
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, universal_newlines=True
        )
        process.communicate(input=script_content)
        log.debug(
            f"Local script '{script_path}' ran remotely, exit code {process.returncode}"
        )
        if process.returncode != 0:
            raise Exception(
                f"Local script '{script_path}' run remotely on {user}@{host} "
                f"exited with code {process.returncode}"
            )
    except Exception as e:
        log.exception(f"Error executing local script remotely '{script_path}'")
        raise e


def wait_for_ssh(config: CoreConfig, user: str, host: str):
    """
    Poll until the host accepts an SSH connection. A freshly provisioned instance
    reports "running" before its SSH daemon is up, so this must succeed before any
    remote lifecycle hook runs. Replaces the readiness wait that the old
    ssh-keyscan host-key step provided.
    """
    command = [
        "ssh",
        *ssh_options(config),
        "-o",
        "ConnectTimeout=10",
        f"{user}@{host}",
        "true",
    ]
    log.info(f"Waiting for SSH on {user}@{host} to become available")
    for attempt in range(1, SSH_READY_RETRIES + 1):
        log.debug(f"SSH readiness check attempt {attempt}: {command}")
        returncode = subprocess.call(command)
        if returncode == 0:
            log.info(f"SSH on {host} is available")
            return
        log.debug(
            f"SSH not ready (exit {returncode}), "
            f"{SSH_READY_RETRIES - attempt} attempt(s) remaining"
        )
        time.sleep(SSH_READY_INTERVAL_SECONDS)
    raise Exception(
        f"Timed out waiting for SSH on {user}@{host} after "
        f"{SSH_READY_RETRIES * SSH_READY_INTERVAL_SECONDS}s"
    )


def build_wait_for_ssh_closure(
    config: CoreConfig, provisioner: Provisioner
) -> Callable:
    def wait_for_ssh_ready():
        host = provisioner.get_host()
        assert host is not None, "provisioner must provide host while server started"
        wait_for_ssh(config, config.remote_server_user, host)

    return wait_for_ssh_ready


def build_bootstrap_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def bootstrap():
        local_script_path = os.path.join(
            config.local_server_dir, config.server_bootstrap
        )
        log.debug(f"Bootstrap script resolved to '{local_script_path}'")
        run_local_script_remotely(
            config, config.remote_server_user, provisioner.get_host(), local_script_path
        )

    return bootstrap


def build_start_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def start():
        entry_point_script = os.path.join(
            config.remote_server_dir, config.server_entry_point
        )
        log.debug(f"Entry point script resolved to '{entry_point_script}'")
        run_remote_script(
            config,
            config.remote_server_user,
            provisioner.get_host(),
            entry_point_script,
        )

    return start


def build_stop_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def stop():
        stop_script = os.path.join(
            config.remote_server_dir, config.server_graceful_stop
        )
        log.debug(f"Stop script resolved to '{stop_script}'")
        run_remote_script(
            config, config.remote_server_user, provisioner.get_host(), stop_script
        )

    return stop
