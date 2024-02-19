# SSH to linode and run start/stop scripts. Get return code
# Also health check

import logging
import os
import subprocess
from typing import Callable

from core.config import CoreConfig
from servermanager.provisioner import LinodeProvisioner

log = logging.getLogger(__name__)


def run_remote_script(user: str, host: str, script_path: str):
    working_dir, script_name = os.path.split(script_path)
    cmd = f"cd {working_dir} ; ./{script_name}"
    command = ['ssh', '-o', 'StrictHostKeyChecking=no',
               f'{user}@{host}', cmd]

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
    command = ['ssh', '-o', 'StrictHostKeyChecking=no',
               f'{user}@{host}', 'bash -s']

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


def build_bootstrap_closure(config: CoreConfig, provisioner: LinodeProvisioner) -> Callable:
    def bootstrap():
        local_script_path = os.path.join(
            config.local_server_dir, config.server_bootstrap)
        run_local_script_remotely(
            config.remote_server_user, provisioner.get_host(), local_script_path)
    return bootstrap


def build_start_closure(config: CoreConfig, provisioner: LinodeProvisioner) -> Callable:
    def start():
        entry_point_script = os.path.join(
            config.remote_server_dir, config.server_entry_point)
        run_remote_script(config.remote_server_user,
                          provisioner.get_host(), entry_point_script)
    return start


def buid_stop_closure(config: CoreConfig, provisioner: LinodeProvisioner) -> Callable:
    def stop():
        stop_script = os.path.join(
            config.remote_server_dir, config.server_graceful_stop)
        run_remote_script(config.remote_server_user,
                          provisioner.get_host(), stop_script)
    return stop
