
from discord.ext.commands import Bot

from core.config import read_config_files
from core.factory import build_linode_provisioner
from discordbot.bot import build_bot
from discordbot.config import DISCORD_CONFIG_NAMESPACE, DiscordBotConfig


def get_bot_and_token() -> tuple[Bot, str]:
    config = read_config_files()
    discord_config = DiscordBotConfig(**config[DISCORD_CONFIG_NAMESPACE])
    provisioner = build_linode_provisioner()
    bot = build_bot(discord_config, provisioner)
    return bot, discord_config.token
