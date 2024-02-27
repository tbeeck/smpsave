import asyncio
import logging
import time
from datetime import datetime, timedelta
from threading import Event, Lock, Thread

import discord
from discord.ext import commands

from smpsave.discordbot.config import DiscordBotConfig
from smpsave.provisioning.provisioner import Provisioner

log = logging.getLogger(__name__)


def discord_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    return intents


class BotBrain():
    """
    Handle bot commands given the current state.
    """
    config: DiscordBotConfig
    provisioner: Provisioner
    server_lock: Lock

    lease_expires: datetime
    poll_task: asyncio.Task
    cancel_polling_event: Event = Event()
    lease_expire_warning_sent: bool = False

    def __init__(self, config: DiscordBotConfig, provisioner: Provisioner):
        self.config = config
        self.provisioner = provisioner
        self.server_lock = Lock()
        self.lease_expires = datetime.now()

    async def do_start(self, ctx: commands.Context):
        if self.server_lock.locked():
            await ctx.send("Start or stop already in progress.")
            return
        await ctx.send(f"Starting server, please wait...")
        with self.server_lock:
            try:
                self.provisioner.start()
                await ctx.send(f"Server started, IP address: {self.provisioner.get_host()}")
                self.start_lifecycle_polling(ctx)
            except Exception as e:
                log.error(f"Error starting server: {e}")
                await ctx.send("Error starting server :(")

    async def do_stop(self, ctx: commands.Context):
        if self.server_lock.locked():
            await ctx.send("Start or stop already in progress.")
            return
        await ctx.send(f"Stopping server, please wait...")
        with self.server_lock:
            try:
                self.provisioner.stop()
                self.cancel_lifecycle_polling()
                await ctx.send(f"Server stopped.")
            except Exception as e:
                log.error(f"Error stopping server: {e}")
                await ctx.send("Error stopping server :(")

    async def do_status(self, ctx: commands.Context):
        ip = self.provisioner.get_host()
        if ip:
            await ctx.send(f"Server is online, ip `{ip}`")
        elif self.server_lock.locked():
            # no ip and server is locked, server probably starting.
            await ctx.send(f"Server is starting.")
        else:
            await ctx.send(f"Server is offline.")

    async def do_extend(self, ctx: commands.Context):
        max_expire_time = \
            datetime.now() + timedelta(minutes=self.config.lease_max_remaining_minutes)
        delta = timedelta(minutes=self.config.lease_increment_minutes)
        target = self.lease_expires + delta
        if target < max_expire_time:
            self.lease_expires = target
        else:
            self.lease_expires = max_expire_time
        await ctx.send(f"Lease will now expire at: {self.lease_expires.isoformat()}")

    def start_lifecycle_polling(self, ctx: commands.Context):
        self.lease_expires = datetime.now() \
            + timedelta(minutes=self.config.lease_max_remaining_minutes)
        self.cancel_polling_event.clear()
        self.lease_expire_warning_sent = False
        self.poll_task = asyncio.create_task(self._shutdown_polling(ctx))

    def cancel_lifecycle_polling(self):
        self.cancel_polling_event.set()

    async def _shutdown_polling(self, ctx: commands.Context):
        while not self.cancel_polling_event.is_set():
            if datetime.now() >= self.lease_expires:
                await ctx.send("Lease has expired, shutting down the server!")
                self.provisioner.stop()
                break
            elif self._should_warn_about_expiration():
                await ctx.send("Lease will expire soon!")
                self.lease_expire_warning_sent = True
            await asyncio.sleep(1)

    def _should_warn_about_expiration(self):
        warning_threshold = self.lease_expires - \
            timedelta(minutes=self.config.lease_warning_threshold_minutes)
        return not self.lease_expire_warning_sent and \
            warning_threshold >= datetime.now()


def build_bot(config: DiscordBotConfig, provisioner: Provisioner) -> commands.Bot:
    bot = commands.Bot(command_prefix=config.command_prefix,
                       intents=discord_intents())

    brain = BotBrain(config, provisioner)

    @bot.command(help="Provision and start the server")  # type: ignore
    async def start(ctx: commands.Context):
        await brain.do_start(ctx)

    @bot.command(help="Shut down and deprovision the server")  # type: ignore
    async def stop(ctx: commands.Context):
        await brain.do_stop(ctx)

    @bot.command(name="extend",  # type: ignore
                 help=f"Extend the lease by {config.lease_increment_minutes} minutes.")
    async def extend_lease(ctx: commands.Context):
        await brain.do_extend(ctx)

    @bot.command(name="timeremaining",  # type: ignore
                 help="Get remaining time for the server.")
    async def time_remaining(ctx: commands.Context):
        remaining = brain.lease_expires.strftime("%H:%M")
        delta = brain.lease_expires - datetime.now()
        await ctx.send(f"Lease will expire at: {remaining} ({delta.min} minutes)")

    @bot.command(name="status",  # type: ignore
                 help="Get status of the server, and its IP if it is online.")
    async def status(ctx: commands.Context):
        await brain.do_status(ctx)

    return bot
