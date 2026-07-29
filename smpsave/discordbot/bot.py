import asyncio
import logging
import time
from datetime import datetime, timedelta
from threading import Event, Lock, Thread

import discord
from discord.ext import commands

from smpsave.discordbot import embeds
from smpsave.discordbot.config import DiscordBotConfig
from smpsave.provisioning.provisioner import Provisioner

log = logging.getLogger(__name__)


def discord_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    return intents


class BotBrain:
    """
    Handles bot commands and maintains the bot's state.
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
        log.debug(f"start requested by {ctx.author} in #{ctx.channel}")
        if self.server_lock.locked():
            log.debug("start rejected: server lock is held")
            await ctx.send(embed=embeds.busy())
            return
        await ctx.send(embed=embeds.starting())
        with self.server_lock:
            try:
                self.provisioner.start()
                self.start_lifecycle_polling(ctx)
                await ctx.send(
                    embed=embeds.started(
                        str(self.provisioner.get_host()),
                        self.lease_time_remaining(),
                        self.config.command_prefix,
                    )
                )
            except Exception as e:
                log.exception(f"Error starting server: {e}")
                await ctx.send(embed=embeds.error("starting server"))

    async def do_stop(self, ctx: commands.Context):
        log.debug(f"stop requested by {ctx.author} in #{ctx.channel}")
        if self.server_lock.locked():
            log.debug("stop rejected: server lock is held")
            await ctx.send(embed=embeds.busy())
            return
        await ctx.send(embed=embeds.stopping())
        with self.server_lock:
            try:
                self.provisioner.stop()
                self.cancel_lifecycle_polling()
                await ctx.send(embed=embeds.stopped())
            except Exception as e:
                log.exception(f"Error stopping server: {e}")
                await ctx.send(embed=embeds.error("stopping server"))

    async def do_status(self, ctx: commands.Context):
        log.debug(f"status requested by {ctx.author} in #{ctx.channel}")
        ip = self.provisioner.get_host()
        if not ip and self.server_lock.locked():
            await ctx.send(embed=embeds.status_starting())
        elif ip:
            await ctx.send(
                embed=embeds.status_online(
                    ip, self.lease_time_remaining(), self.config.command_prefix
                )
            )
        else:
            await ctx.send(embed=embeds.status_offline(self.config.command_prefix))

    async def do_extend(self, ctx: commands.Context):
        log.debug(
            f"extend requested by {ctx.author} in #{ctx.channel}, "
            f"lease currently expires at {self.lease_expires}"
        )
        max_expire_time = datetime.now() + timedelta(
            minutes=self.config.lease_max_remaining_minutes
        )
        delta = timedelta(minutes=self.config.lease_increment_minutes)
        target = self.lease_expires + delta
        if target < max_expire_time:
            self.lease_expires = target
        else:
            self.lease_expires = max_expire_time
        await ctx.send(embed=embeds.lease_extended(self.lease_time_remaining()))
        # Also reset the warning flag
        self.lease_expire_warning_sent = False

    def start_lifecycle_polling(self, ctx: commands.Context):
        self.lease_expires = datetime.now() + timedelta(
            minutes=self.config.lease_max_remaining_minutes
        )
        self.cancel_polling_event.clear()
        self.lease_expire_warning_sent = False
        log.debug(f"Starting lifecycle polling, lease expires at {self.lease_expires}")
        self.poll_task = asyncio.create_task(self._shutdown_polling(ctx))

    def cancel_lifecycle_polling(self):
        log.debug("Cancelling lifecycle polling")
        self.cancel_polling_event.set()

    def lease_time_remaining(self) -> timedelta:
        remaining = self.lease_expires - datetime.now()
        zero = timedelta(seconds=0)
        if remaining < zero:
            remaining = zero
        rounded = remaining - timedelta(microseconds=remaining.microseconds)
        return rounded

    async def _shutdown_polling(self, ctx: commands.Context):
        while not self.cancel_polling_event.is_set():
            if datetime.now() >= self.lease_expires:
                log.info("Lease expired, stopping server")
                await ctx.send(embed=embeds.lease_expired())
                with self.server_lock:
                    self.provisioner.stop()
                break
            elif self._should_warn_about_expiration():
                await ctx.send(
                    embed=embeds.lease_warning(
                        self.lease_time_remaining(), self.config.command_prefix
                    )
                )
                self.lease_expire_warning_sent = True
            await asyncio.sleep(1)

    def _should_warn_about_expiration(self):
        warning_threshold = self.lease_expires - timedelta(
            minutes=self.config.lease_warning_threshold_minutes
        )
        return (
            not self.lease_expire_warning_sent and warning_threshold <= datetime.now()
        )


def build_bot(config: DiscordBotConfig, provisioner: Provisioner) -> commands.Bot:
    log.debug(f"Building bot with config: {config}")
    bot = commands.Bot(command_prefix=config.command_prefix, intents=discord_intents())

    brain = BotBrain(config, provisioner)

    @bot.event
    async def on_ready():
        log.info(f"Logged in as {bot.user}")
        log.debug(f"Connected to guilds: {[g.name for g in bot.guilds]}")

    @bot.event
    async def on_command_error(ctx: commands.Context, error: Exception):
        # Missing roles and unknown commands are routine, so they are only
        # interesting at debug level. Anything else is a real failure.
        if isinstance(error, (commands.CheckFailure, commands.CommandNotFound)):
            log.debug(
                f"Command '{ctx.invoked_with}' from {ctx.author} "
                f"rejected: {type(error).__name__}: {error}"
            )
        else:
            log.exception(
                f"Command '{ctx.invoked_with}' from {ctx.author} failed", exc_info=error
            )

    @bot.command(help="Provision and start the server")  # type: ignore
    @commands.has_role(config.allowed_role)
    async def start(ctx: commands.Context):
        await brain.do_start(ctx)

    @bot.command(help="Shut down and deprovision the server")  # type: ignore
    @commands.has_role(config.allowed_role)
    async def stop(ctx: commands.Context):
        await brain.do_stop(ctx)

    @bot.command(
        name="extend",  # type: ignore
        help=f"Extend the lease by {config.lease_increment_minutes} minutes.",
    )
    @commands.has_role(config.allowed_role)
    async def extend_lease(ctx: commands.Context):
        await brain.do_extend(ctx)

    @bot.command(
        name="status",  # type: ignore
        help="Get status of the server, and its IP if it is online.",
    )
    async def status(ctx: commands.Context):
        await brain.do_status(ctx)

    return bot
