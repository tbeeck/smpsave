from abc import abstractmethod
from dataclasses import Field, dataclass, fields
from typing import Any


class ConfigurationInitializationException(Exception):
    """
    Exception for when we fail to initialize a configuration object.
    """


class ConfigurationParsingException(ConfigurationInitializationException):
    """ 
    ConfigurationInitializationException due to failure to parse 
    a configuration value to the given type.
    """

    @staticmethod
    def fromField(f: Field, underlyingException: Exception):
        return ConfigurationParsingException(
            f"Failed to parse '{f.name}' as '{f.type}' for configuration class '{f.__class__.__name__}'",
            underlyingException)


@dataclass
class BaseConfig():
    """
    This class serves as the base class for any smpsave configuration classes.

    ConfigParser loads configuration values only as strings, so we try to parse
    any fields on the dataclass into the given type hint.
    """

    def populate_from_env(self):
        """
        Abstract: Will be called in postinit. Used to map environment variable overrides to their values.
        """
        pass

    def __post_init__(self) -> None:
        self.populate_from_env()
        class_fields: tuple[Field[Any], ...] = fields(self)
        for field in class_fields:
            if field.type == int:
                try:
                    setattr(self, field.name, int(getattr(self, field.name)))
                except ValueError as e:
                    raise ConfigurationParsingException.fromField(field, e)
            elif field.type == list[str]:
                try:
                    separated_list: list[str] = getattr(
                        self, field.name).split(',')
                    setattr(self, field.name, separated_list)
                except Exception as e:
                    raise ConfigurationParsingException.fromField(field, e)
