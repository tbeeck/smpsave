import logging
from datetime import datetime, timedelta
from threading import Lock

import discord
from discord.ext import commands

from smpsave.discordbot.config import DiscordBotConfig
from smpsave.provisioning.provisioner import Provisioner

log = logging.getLogger(__name__)


def discord_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    return intents


class BotState():
    server_lock: Lock
    lease_expires: datetime

    def __init__(self):
        self.server_lock = Lock()
        self.lease_expires = datetime.now()


def build_bot(config: DiscordBotConfig, provisioner: Provisioner) -> commands.Bot:
    config.populate_from_env()
    bot = commands.Bot(command_prefix=config.command_prefix,
                       intents=discord_intents())

    state = BotState()

    @bot.command(help="Provision and start the server")  # type: ignore
    async def start(ctx: commands.Context):
        if state.server_lock.locked():
            await ctx.send("Start or stop already in progress.")
            return
        await ctx.send(f"Starting server, please wait...")
        with state.server_lock:
            try:
                provisioner.start()
                await ctx.send(f"Server started, IP address: {provisioner.get_host()}")
            except Exception as e:
                log.error(f"Error starting server: {e}")
                await ctx.send("Error starting server :(")

    @bot.command(help="Shut down and deprovision the server")  # type: ignore
    async def stop(ctx: commands.Context):
        if state.server_lock.locked():
            await ctx.send("Start or stop already in progress.")
            return
        await ctx.send(f"Stopping server, please wait...")
        with state.server_lock:
            try:
                provisioner.stop()
                await ctx.send(f"Server stopped.")
            except Exception as e:
                log.error(f"Error stopping server: {e}")
                await ctx.send("Error stopping server :(")

    @bot.command(name="extend",  # type: ignore
                 help=f"Extend the lease by {config.lease_increment_minutes} minutes.")
    async def extend_lease(ctx: commands.Context):
        max_expire_time = datetime.now() + timedelta(minutes=config.lease_max_remaining_minutes)
        delta = timedelta(minutes=config.lease_increment_minutes)
        target = state.lease_expires + delta
        if target < max_expire_time:
            state.lease_expires = target
        else:
            state.lease_expires = max_expire_time
        await ctx.send(f"Lease will now expire at: {state.lease_expires.isoformat()}")

    @bot.command(name="timeremaining",  # type: ignore
                 help="Get remaining time for the server.")
    async def time_remaining(ctx: commands.Context):
        await ctx.send(f"Lease will expire at: {state.lease_expires.isoformat()}")

    @bot.command(name="getip",  # type: ignore
                 help="Get the IP of the server, if it is online")
    async def get_ip(ctx: commands.Context):
        host = provisioner.get_host()
        if host:
            await ctx.send(f"Server online, IP `{host}`")
        else:
            await ctx.send("Server offline")

    return bot
