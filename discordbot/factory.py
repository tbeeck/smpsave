
import discord

from core.config import get_all_configurations
from discordbot.bot import DiscordClient
from discordbot.config import DISCORD_CONFIG_NAMESPACE, DiscordBotConfig


def discord_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    return intents


def build_bot() -> tuple[DiscordClient, str]:
    config = get_all_configurations()
    discord_config = DiscordBotConfig(**config[DISCORD_CONFIG_NAMESPACE])
    discord_config.populate_from_env()

    bot = DiscordClient(intents=discord_intents())
    return bot, discord_config.token
