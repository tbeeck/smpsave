"""Tests for BotBrain, the stateful core of the Discord bot.

These tests avoid a pytest-asyncio dependency: each async test body is run
through a small ``@async_test`` wrapper that drives it with ``asyncio.run``.
Shared mocks and helpers live in ``tests.mocks``.
"""

import asyncio
import contextlib
import threading
from dataclasses import replace
from datetime import datetime, timedelta
from typing import Optional

from smpsave.discordbot import embeds
from smpsave.discordbot.bot import BotBrain
from smpsave.discordbot.config import DiscordBotConfig
from tests.mocks import MockProvisioner, async_test, wait_until


class MockContext:
    """Stand-in for discord.py's commands.Context.

    Records the embeds sent so tests can assert on them by title.
    """

    def __init__(self, author: str = "tester", channel: str = "general"):
        self.author = author
        self.channel = channel
        self.embeds: list = []

    async def send(self, *args, embed=None, **kwargs):
        self.embeds.append(embed)

    @property
    def titles(self) -> list:
        return [e.title for e in self.embeds if e is not None]


def make_config(**overrides) -> DiscordBotConfig:
    base = DiscordBotConfig(
        allowed_role=1,
        command_prefix="!",
        lease_increment_minutes=30,
        lease_warning_threshold_minutes=30,
        lease_max_remaining_minutes=120,
        token="test-token",
    )
    return replace(base, **overrides) if overrides else base


def make_brain(provisioner: Optional[MockProvisioner] = None, **config_overrides):
    provisioner = provisioner or MockProvisioner()
    brain = BotBrain(make_config(**config_overrides), provisioner)
    return brain, provisioner


async def cancel_polling(brain: BotBrain):
    """Tear down any background lease-polling task started by do_start."""
    task = getattr(brain, "poll_task", None)
    if task is not None:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


# --------------------------------------------------------------------------- #
# start: happy path and lock contract
# --------------------------------------------------------------------------- #


@async_test
async def test_start_when_idle_provisions_and_reports_online():
    brain, prov = make_brain()
    ctx = MockContext()

    await brain.do_start(ctx)

    assert prov.start_calls == 1
    assert embeds.starting().title in ctx.titles
    assert embeds.started("h", timedelta(), "!").title in ctx.titles
    # Lock must be released once the command finishes.
    assert not brain.server_lock.locked()
    await cancel_polling(brain)


@async_test
async def test_start_releases_lock_on_provisioner_error():
    # The most important regression guard: a failing start must not leave the
    # lock held, which would wedge the bot into a permanent "busy" state.
    prov = MockProvisioner()
    prov.start_error = RuntimeError("linode is down")
    brain, _ = make_brain(prov)
    ctx = MockContext()

    await brain.do_start(ctx)

    assert embeds.error("starting server").title in ctx.titles
    assert not brain.server_lock.locked()

    # A follow-up start should now succeed rather than be rejected as busy.
    prov.start_error = None
    ctx2 = MockContext()
    await brain.do_start(ctx2)
    assert embeds.busy().title not in ctx2.titles
    assert prov.start_calls == 2
    await cancel_polling(brain)


@async_test
async def test_start_rejected_while_start_in_progress():
    gate = threading.Event()
    prov = MockProvisioner()
    prov.start_gate = gate
    brain, _ = make_brain(prov)

    ctx_a = MockContext(author="a")
    task = asyncio.create_task(brain.do_start(ctx_a))
    try:
        # Let A acquire the lock and block inside the provisioning thread.
        await wait_until(lambda: brain.server_lock.locked())

        ctx_b = MockContext(author="b")
        await brain.do_start(ctx_b)
        assert ctx_b.titles == [embeds.busy().title]
        assert prov.start_calls == 1  # B did not trigger a second start
    finally:
        gate.set()
        await task
        await cancel_polling(brain)


@async_test
async def test_stop_rejected_while_start_in_progress():
    # A stop arriving mid-start must also be rejected, not queued behind the
    # blocking lock (which would stall the event loop).
    gate = threading.Event()
    prov = MockProvisioner()
    prov.start_gate = gate
    brain, _ = make_brain(prov)

    ctx_a = MockContext(author="a")
    task = asyncio.create_task(brain.do_start(ctx_a))
    try:
        await wait_until(lambda: brain.server_lock.locked())

        ctx_b = MockContext(author="b")
        await brain.do_stop(ctx_b)
        assert ctx_b.titles == [embeds.busy().title]
        assert prov.stop_calls == 0
    finally:
        gate.set()
        await task
        await cancel_polling(brain)


# --------------------------------------------------------------------------- #
# stop: happy path and lock contract
# --------------------------------------------------------------------------- #


@async_test
async def test_stop_when_running_deprovisions_and_cancels_polling():
    prov = MockProvisioner(host="1.2.3.4")
    brain, _ = make_brain(prov)
    # Simulate an active lease/poll loop.
    brain.start_lifecycle_polling(MockContext())
    assert not brain.cancel_polling_event.is_set()

    ctx = MockContext()
    await brain.do_stop(ctx)

    assert prov.stop_calls == 1
    assert embeds.stopping().title in ctx.titles
    assert embeds.stopped().title in ctx.titles
    assert brain.cancel_polling_event.is_set()  # polling told to cancel
    assert not brain.server_lock.locked()
    await cancel_polling(brain)


@async_test
async def test_stop_releases_lock_on_provisioner_error():
    prov = MockProvisioner(host="1.2.3.4")
    prov.stop_error = RuntimeError("could not deprovision")
    brain, _ = make_brain(prov)
    ctx = MockContext()

    await brain.do_stop(ctx)

    assert embeds.error("stopping server").title in ctx.titles
    assert not brain.server_lock.locked()


@async_test
async def test_stop_rejected_while_stop_in_progress():
    gate = threading.Event()
    prov = MockProvisioner(host="1.2.3.4")
    prov.stop_gate = gate
    brain, _ = make_brain(prov)

    ctx_a = MockContext(author="a")
    task = asyncio.create_task(brain.do_stop(ctx_a))
    try:
        await wait_until(lambda: brain.server_lock.locked())

        ctx_b = MockContext(author="b")
        await brain.do_start(ctx_b)
        assert ctx_b.titles == [embeds.busy().title]
        assert prov.start_calls == 0
    finally:
        gate.set()
        await task
        await cancel_polling(brain)


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #


@async_test
async def test_status_offline_when_no_host_and_idle():
    brain, _ = make_brain()
    ctx = MockContext()
    await brain.do_status(ctx)
    assert ctx.titles == [embeds.status_offline("!").title]


@async_test
async def test_status_starting_when_locked_without_host():
    gate = threading.Event()
    prov = MockProvisioner()  # no host yet
    prov.start_gate = gate
    brain, _ = make_brain(prov)

    task = asyncio.create_task(brain.do_start(MockContext()))
    try:
        await wait_until(lambda: brain.server_lock.locked())
        ctx = MockContext()
        await brain.do_status(ctx)
        assert ctx.titles == [embeds.status_starting().title]
    finally:
        gate.set()
        await task
        await cancel_polling(brain)


@async_test
async def test_status_online_when_host_present():
    prov = MockProvisioner(host="1.2.3.4")
    brain, _ = make_brain(prov)
    ctx = MockContext()
    await brain.do_status(ctx)
    assert ctx.titles == [
        embeds.status_online("1.2.3.4", brain.lease_time_remaining(), "!").title
    ]


# --------------------------------------------------------------------------- #
# lease management
# --------------------------------------------------------------------------- #


@async_test
async def test_extend_adds_increment():
    brain, _ = make_brain(lease_increment_minutes=30, lease_max_remaining_minutes=120)
    brain.lease_expires = datetime.now() + timedelta(minutes=10)
    await brain.do_extend(MockContext())
    remaining = brain.lease_time_remaining()
    assert timedelta(minutes=39) <= remaining <= timedelta(minutes=40)


@async_test
async def test_extend_caps_at_max():
    brain, _ = make_brain(lease_increment_minutes=30, lease_max_remaining_minutes=120)
    brain.lease_expires = datetime.now() + timedelta(minutes=119)
    await brain.do_extend(MockContext())
    # Would be 149m uncapped; must clamp to the 120m maximum.
    assert brain.lease_time_remaining() <= timedelta(minutes=120)
    assert brain.lease_time_remaining() > timedelta(minutes=119)


@async_test
async def test_extend_resets_warning_flag():
    brain, _ = make_brain()
    brain.lease_expire_warning_sent = True
    await brain.do_extend(MockContext())
    assert brain.lease_expire_warning_sent is False


def test_lease_time_remaining_clamps_to_zero():
    brain, _ = make_brain()
    brain.lease_expires = datetime.now() - timedelta(minutes=5)
    assert brain.lease_time_remaining() == timedelta(0)


def test_should_warn_true_within_threshold():
    brain, _ = make_brain(lease_warning_threshold_minutes=30)
    brain.lease_expires = datetime.now() + timedelta(minutes=10)
    brain.lease_expire_warning_sent = False
    assert brain._should_warn_about_expiration() is True


def test_should_warn_false_once_sent():
    brain, _ = make_brain(lease_warning_threshold_minutes=30)
    brain.lease_expires = datetime.now() + timedelta(minutes=10)
    brain.lease_expire_warning_sent = True
    assert brain._should_warn_about_expiration() is False


def test_should_warn_false_before_threshold():
    brain, _ = make_brain(lease_warning_threshold_minutes=30)
    brain.lease_expires = datetime.now() + timedelta(minutes=90)
    brain.lease_expire_warning_sent = False
    assert brain._should_warn_about_expiration() is False


# --------------------------------------------------------------------------- #
# lease polling loop
# --------------------------------------------------------------------------- #


@async_test
async def test_shutdown_polling_stops_server_when_lease_expired():
    prov = MockProvisioner(host="1.2.3.4")
    brain, _ = make_brain(prov)
    brain.cancel_polling_event.clear()
    brain.lease_expires = datetime.now() - timedelta(seconds=1)  # already expired

    ctx = MockContext()
    await brain._shutdown_polling(ctx)

    assert prov.stop_calls == 1
    assert embeds.lease_expired().title in ctx.titles
    assert not brain.server_lock.locked()


@async_test
async def test_shutdown_polling_returns_immediately_when_cancelled():
    prov = MockProvisioner(host="1.2.3.4")
    brain, _ = make_brain(prov)
    brain.cancel_polling_event.set()  # already cancelled
    brain.lease_expires = datetime.now() - timedelta(seconds=1)

    ctx = MockContext()
    await brain._shutdown_polling(ctx)

    assert prov.stop_calls == 0
    assert ctx.titles == []
