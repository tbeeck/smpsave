import os
from attr import dataclass

DISCORD_CONFIG_NAMESPACE = "discord"


@dataclass
class DiscordBotConfig():
    command_prefix: str
    token: str
    lease_increment_minutes: int
    lease_max_remaining_minutes: int

    def populate_from_env(self):
        token = os.getenv("DISCORD_TOKEN")
        if token:
            self.token = token
