from datetime import timedelta
from typing import Optional

import discord

ONLINE_COLOR = discord.Color.brand_green()
OFFLINE_COLOR = discord.Color.dark_grey()
PENDING_COLOR = discord.Color.gold()
WARNING_COLOR = discord.Color.orange()
ERROR_COLOR = discord.Color.brand_red()


def format_duration(delta: timedelta) -> str:
    """Render a timedelta as a short human readable string, e.g. '1h 30m'."""
    total_seconds = max(int(delta.total_seconds()), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _embed(
    title: str, color: discord.Color, description: Optional[str] = None
) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)


def busy() -> discord.Embed:
    return _embed(
        "⏳ Please wait", PENDING_COLOR, "A start or stop is already in progress."
    )


def starting() -> discord.Embed:
    return _embed(
        "🚀 Starting server",
        PENDING_COLOR,
        "Provisioning the server, this may take a few minutes...",
    )


def started(host: str, time_remaining: timedelta, command_prefix: str) -> discord.Embed:
    embed = _embed("🟢 Server online", ONLINE_COLOR)
    embed.add_field(name="Address", value=f"`{host}`", inline=False)
    embed.add_field(
        name="Time remaining", value=format_duration(time_remaining), inline=True
    )
    embed.set_footer(text=f"Use {command_prefix}extend to keep the server up.")
    return embed


def stopping() -> discord.Embed:
    return _embed(
        "🛑 Stopping server",
        PENDING_COLOR,
        "Shutting down and deprovisioning, please wait...",
    )


def stopped() -> discord.Embed:
    return _embed(
        "⚫ Server stopped", OFFLINE_COLOR, "The server has been deprovisioned."
    )


def status_starting() -> discord.Embed:
    return _embed(
        "⏳ Server is starting",
        PENDING_COLOR,
        "Hang tight, provisioning is in progress.",
    )


def status_online(
    host: str, time_remaining: timedelta, command_prefix: str
) -> discord.Embed:
    return started(host, time_remaining, command_prefix)


def status_offline(command_prefix: str) -> discord.Embed:
    embed = _embed("⚫ Server offline", OFFLINE_COLOR)
    embed.set_footer(text=f"Use {command_prefix}start to bring it online.")
    return embed


def lease_extended(time_remaining: timedelta) -> discord.Embed:
    embed = _embed("⏱️ Lease extended", ONLINE_COLOR)
    embed.add_field(
        name="Time remaining", value=format_duration(time_remaining), inline=True
    )
    return embed


def lease_warning(time_remaining: timedelta, command_prefix: str) -> discord.Embed:
    embed = _embed(
        "⚠️ Lease expiring soon",
        WARNING_COLOR,
        f"The server will shut down in **{format_duration(time_remaining)}**.",
    )
    embed.set_footer(text=f"Use {command_prefix}extend to keep the server up.")
    return embed


def lease_expired() -> discord.Embed:
    return _embed("⌛ Lease expired", WARNING_COLOR, "Shutting down the server!")


def error(action: str, detail: Optional[str] = None) -> discord.Embed:
    embed = _embed(f"❌ Error {action}", ERROR_COLOR)
    if detail:
        embed.add_field(name="Details", value=f"```{detail[:1000]}```", inline=False)
    return embed
