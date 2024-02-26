
from discord.ext.commands import Bot

from smpsave.core.config import read_config_files
from smpsave.core.factory import build_provisioner
from smpsave.discordbot.bot import build_bot
from smpsave.discordbot.config import DISCORD_CONFIG_NAMESPACE, DiscordBotConfig


def get_bot_and_token() -> tuple[Bot, str]:
    config = read_config_files()
    discord_config = DiscordBotConfig(**config[DISCORD_CONFIG_NAMESPACE])
    provisioner = build_provisioner()
    bot = build_bot(discord_config, provisioner)
    return bot, discord_config.token
