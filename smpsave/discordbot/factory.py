
from discord.ext.commands import Bot

from smpsave.configuration import get_configurations
from smpsave.core.factory import build_provisioner
from smpsave.discordbot.bot import build_bot
from smpsave.discordbot.config import (DISCORD_CONFIG_NAMESPACE,
                                       DiscordBotConfig)


def get_bot_and_token() -> tuple[Bot, str]:
    config = get_configurations(DISCORD_CONFIG_NAMESPACE, DiscordBotConfig)
    provisioner = build_provisioner()
    bot = build_bot(config, provisioner)
    return bot, config.token
