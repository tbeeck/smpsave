import os
from configparser import ConfigParser
from dataclasses import dataclass

from smpsave.configuration import BaseConfig

CORE_CONFIG_NAMESPACE = "core"


def read_config_files() -> ConfigParser:
    config = ConfigParser()
    files = ["config.ini", "user.ini"]
    files = [f for f in files if os.path.exists(f)]
    config.read(files)
    return config


@dataclass
class CoreConfig(BaseConfig):
    provisioner: str
    local_server_dir: str
    remote_server_dir: str
    remote_server_user: str
    server_bootstrap: str
    server_entry_point: str
    server_graceful_stop: str
