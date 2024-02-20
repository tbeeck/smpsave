from threading import Lock

import discord
from discord.ext import commands

from discordbot.config import DiscordBotConfig
from servermanager.provisioner import LinodeProvisioner


def discord_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    return intents


class BotState():
    server_lock: Lock

    def __init__(self):
        self.server_lock = Lock()


def build_bot(config: DiscordBotConfig, provisioner: LinodeProvisioner):
    bot = commands.Bot(command_prefix=config.command_prefix,
                       intents=discord_intents())

    state = BotState()

    @bot.command()  # type: ignore
    async def start(ctx: commands.Context):
        await ctx.send(f"Starting server, please wait...")
        provisioner.start()
        await ctx.send(f"Server started, IP address: {provisioner.get_host()}")

    @bot.command()  # type: ignore
    async def stop(ctx: commands.Context):
        await ctx.send(f"Stopping server, please wait...")
        provisioner.stop()
        await ctx.send(f"Server stopped.")

    @bot.command(name="getip")  # type: ignore
    async def get_ip(ctx: commands.Context):
        host = provisioner.get_host()
        if host:
            await ctx.send(f"Server online, IP {host}")
        else:
            await ctx.send("Server offline")

    return bot
