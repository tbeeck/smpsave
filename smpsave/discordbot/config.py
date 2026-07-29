import os
from dataclasses import dataclass

from smpsave.configuration import BaseConfig
from smpsave.configuration.baseconfig import ConfigurationInitializationException

DISCORD_CONFIG_NAMESPACE = "discord"


@dataclass
class DiscordBotConfig(BaseConfig):
    allowed_role: int
    """
    Snowflake ID of the role required to use server management commands.
    """

    command_prefix: str = "!"
    """
    Prefix symbol used for commands (e.g., in '!start', '!' is the prefix)
    """

    lease_increment_minutes: int = 30
    """
    Time in minutes to extend the lease by when the extend command is used.
    """

    lease_warning_threshold_minutes: int = 30
    """
    Remaining time threshold, in minutes, after which to provide a warning
    message that the server will shut off soon.
    """

    lease_max_remaining_minutes: int = 120
    """
    Maximum duration of a server lease in minutes. The lease may not be
    extended beyond this time.
    """

    token: str = ""
    """
    Discord oauth2 token. May be provided via the '[discord] token' config value
    or the DISCORD_TOKEN environment variable; the environment variable takes
    precedence. At least one of the two must be set.
    """

    def populate_from_env(self):
        token = os.getenv("DISCORD_TOKEN")
        if token:
            self.token = token
        if not self.token:
            raise ConfigurationInitializationException(
                "Discord token must be set via the '[discord] token' config "
                "value or the DISCORD_TOKEN environment variable"
            )

    def __str__(self):
        return self._redact(self.token)
