"""Reusable, app-agnostic test doubles and helpers for smpsave."""

import asyncio
import functools
import threading
from typing import Callable, Optional

from smpsave.provisioning.provisioner import Provisioner


def async_test(coro):
    """Run an ``async def`` test body under its own event loop.

    Avoids a pytest-asyncio dependency: driving the coroutine with
    ``asyncio.run`` gives each test a fresh loop.
    """

    @functools.wraps(coro)
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))

    return wrapper


async def wait_until(predicate, timeout: float = 5.0):
    """Yield to the event loop until ``predicate()`` is true or we time out."""
    deadline = asyncio.get_event_loop().time() + timeout
    while not predicate():
        assert asyncio.get_event_loop().time() < deadline, "condition not met in time"
        await asyncio.sleep(0)


class MockProvisioner(Provisioner):
    """In-memory provisioner with hooks to control timing and failures."""

    def __init__(self, host: Optional[str] = None):
        self._host = host
        self.start_calls = 0
        self.stop_calls = 0
        # When set, start()/stop() block on this event, letting a test hold a
        # lock open while it checks concurrent behavior.
        self.start_gate: Optional[threading.Event] = None
        self.stop_gate: Optional[threading.Event] = None
        self.start_error: Optional[Exception] = None
        self.stop_error: Optional[Exception] = None

    def start(self):
        self.start_calls += 1
        if self.start_gate is not None:
            assert self.start_gate.wait(timeout=5), "start_gate never released"
        if self.start_error is not None:
            raise self.start_error
        self._host = "1.2.3.4"

    def stop(self, force: bool = False):
        self.stop_calls += 1
        if self.stop_gate is not None:
            assert self.stop_gate.wait(timeout=5), "stop_gate never released"
        if self.stop_error is not None:
            raise self.stop_error
        self._host = None

    def get_host(self) -> Optional[str]:
        return self._host

    def run_poststart_hooks(self):
        pass

    def run_prestop_hooks(self):
        pass

    def set_poststart_hooks(self, hooks: list[Callable]):
        pass

    def set_prestop_hooks(self, hooks: list[Callable]):
        pass
