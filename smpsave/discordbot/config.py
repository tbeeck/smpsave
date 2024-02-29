import os
from dataclasses import dataclass

from smpsave.configuration import BaseConfig

DISCORD_CONFIG_NAMESPACE = "discord"


@dataclass
class DiscordBotConfig(BaseConfig):
    token: str
    """ 
    Discord oauth2 token. May be overridden at runtime by the DISCORD_TOKEN
    environment variable.
    """

    allowed_role: int
    """
    Snowflake ID of the role required to use server management commands.
    """

    command_prefix: str = "!"
    """
    Prefix symbol used for commands (i.e., in !start, '~' is the prefix)
    """

    lease_increment_minutes: int = 30
    """
    Time in minutes to extend the lease by when the extend command is used.
    """

    lease_warning_threshold_minutes: int = 30
    """
    Remaning time threshold, in minutes, after which to provide a warning message that the 
    server will shut off soon.
    """

    lease_max_remaining_minutes: int = 120
    """
    Maximum duration of a server lease in minutes. The lease may not be extended beyond this time.
    """

    def populate_from_env(self):
        token = os.getenv("DISCORD_TOKEN")
        if token:
            self.token = token
