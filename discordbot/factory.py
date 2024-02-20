
from discord.ext.commands import Bot

from core.config import get_all_configurations
from core.factory import build_linode_provisioner
from discordbot.bot import build_bot
from discordbot.config import DISCORD_CONFIG_NAMESPACE, DiscordBotConfig


def get_bot_and_token() -> tuple[Bot, str]:
    config = get_all_configurations()
    discord_config = DiscordBotConfig(**config[DISCORD_CONFIG_NAMESPACE])
    discord_config.populate_from_env()
    provisioner = build_linode_provisioner()
    bot = build_bot(provisioner)
    return bot, discord_config.token
