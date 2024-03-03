import logging
import os
from configparser import ConfigParser
from typing import Optional, TypeVar

from smpsave.configuration.baseconfig import BaseConfig

log = logging.getLogger(__name__)

# Configuration files in order of precedence
CONFIG_FILENAMES = [
    "config.ini",
    "user.ini"
]


class LoadConfigurationException(Exception):
    """ 
    Exception for when we fail to initialize application configurations.
    """


CONFIG_PARSER: Optional[ConfigParser] = None


def load_configs() -> ConfigParser:
    """ 
    Load configuration files for the application.
    """
    global CONFIG_PARSER
    if CONFIG_PARSER:
        return CONFIG_PARSER
    real_files: list[str] = []
    for filename in CONFIG_FILENAMES:
        if os.path.exists(os.path.expanduser(filename)):
            real_files.append(filename)
    if len(real_files) == 0:
        msg = f"""
        No configuration files found. 
        Please specify smpsave configurations in one or more of the following files: {CONFIG_FILENAMES}
        """
        log.error(msg)
        raise LoadConfigurationException(msg)

    configs = ConfigParser()
    loaded_files = configs.read(real_files)
    log.info(f"Loaded configurations from: {loaded_files}")
    CONFIG_PARSER = configs
    return CONFIG_PARSER


ConfigType = TypeVar("ConfigType", bound=BaseConfig)


def get_configurations(namespace: str, clazz: type[ConfigType]) -> ConfigType:
    """
    Get configurations for the given namespace and initialize an object
    of the given type using those configuration values.
    """
    configs = load_configs()
    return clazz(**configs[namespace])
