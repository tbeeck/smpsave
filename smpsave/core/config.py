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
    """
    CoreConfig contains central configuration values for the application. 
    """

    provisioner: str
    """ User's choice of provisioner backend. """

    local_server_dir: str
    """ 
    Path to the local directory containing the game server files. 
    This must also be the root directory for the server lifecycle scripts. 
    """

    remote_server_dir: str
    """
    The directory in the game server's filesystem that should 
    """

    remote_server_user: str = "root"
    """
    Username to use when connecting to the game server.
    """

    server_bootstrap: str = "bootstrap.sh"
    """
    Path to the 'bootstrap' server lifecycle script.
    Must be relative to local_server_dir.
    """

    server_entry_point: str = "start.sh"
    """
    Path to the 'start' server lifecycle script.
    Must be relative to local_server_dir.
    """

    server_graceful_stop: str = "stop.sh"
    """
    Path to the 'stop' server lifecycle script.
    Must be relative to local_server_dir.
    """
