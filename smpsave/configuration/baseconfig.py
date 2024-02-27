from dataclasses import Field, dataclass, fields
from typing import Any


@dataclass
class BaseConfig():
    def populate_from_env(self):
        """ 
        Will be called in postinit. Used to map environment variable overrides to their values.
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
                    raise Exception(
                        f"Failed to parse int for '{field.name}' in '{self.__class__.__name__}'", e)
