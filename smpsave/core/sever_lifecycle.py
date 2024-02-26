# SSH to linode and run start/stop scripts. Get return code
# Also health check

import logging
import os
import subprocess
from typing import Callable

from smpsave.core.config import CoreConfig
from smpsave.provisioning.provisioner import Provisioner

log = logging.getLogger(__name__)


def run_remote_script(user: str, host: str, script_path: str):
    working_dir, script_name = os.path.split(script_path)
    cmd = f"cd {working_dir} ; ./{script_name}"
    command = ['ssh', f'{user}@{host}', cmd]

    try:
        log.debug(f"Running {command} on {user}@{host}")
        returncode = subprocess.call(command, timeout=100)
        if returncode != 0:
            raise Exception(
                f"Failed to run {command} on host {host}, got exit code {returncode}")
    except subprocess.CalledProcessError as e:
        log.error(
            f"Error executing remote script '{script_path}', exit code {e.returncode}")
        raise e


def run_local_script_remotely(user: str, host: str, script_path: str):
    command = ['ssh', f'{user}@{host}', 'bash -s']

    try:
        with open(script_path, "r") as f:
            script_content = f.read()
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        process.communicate(input=script_content)
    except Exception as e:
        log.error(f"Error executing local script remotely '{script_path}'")
        raise e


def _update_key_for_host(host: str):
    # Shell out to ssh-keygen to clear host key
    clear_host_cmd = ['ssh-keygen', '-R', host]
    update_host_cmd = ['ssh-keyscan', '-H', host]

    try:
        log.info(f"Clearing host key for {host}")
        subprocess.run(clear_host_cmd)

        log.info(f"Updating host key for {host}")
        file_path = os.path.expanduser("~/.ssh/known_hosts")
        # 'a' for append.
        with open(file_path, "a") as known_hosts_file:
            subprocess.run(update_host_cmd,
                           stdout=known_hosts_file)
    except Exception as e:
        log.error(f"Error updating host keys for host {host}", e)
        raise e


def build_clear_host_key_closure(provisioner: Provisioner) -> Callable:
    def clear_host_key():
        host = provisioner.get_host()
        assert host != None, "provisioner must provide host while server started"
        _update_key_for_host(host)
    return clear_host_key


def build_bootstrap_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def bootstrap():
        local_script_path = os.path.join(
            config.local_server_dir, config.server_bootstrap)
        run_local_script_remotely(
            config.remote_server_user, provisioner.get_host(), local_script_path)
    return bootstrap


def build_start_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def start():
        entry_point_script = os.path.join(
            config.remote_server_dir, config.server_entry_point)
        run_remote_script(config.remote_server_user,
                          provisioner.get_host(), entry_point_script)
    return start


def buid_stop_closure(config: CoreConfig, provisioner: Provisioner) -> Callable:
    def stop():
        stop_script = os.path.join(
            config.remote_server_dir, config.server_graceful_stop)
        run_remote_script(config.remote_server_user,
                          provisioner.get_host(), stop_script)
    return stop
