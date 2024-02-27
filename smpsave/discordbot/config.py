import os
from dataclasses import dataclass

from smpsave.configuration import BaseConfig

DISCORD_CONFIG_NAMESPACE = "discord"


@dataclass
class DiscordBotConfig(BaseConfig):
    token: str
    allowed_role: str
    command_prefix: str = "!"
    lease_increment_minutes: int = 30
    lease_warning_threshold_minutes: int = 30
    lease_max_remaining_minutes: int = 120

    def populate_from_env(self):
        token = os.getenv("DISCORD_TOKEN")
        if token:
            self.token = token
