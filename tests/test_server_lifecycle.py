"""Tests for the SSH readiness poll and the lifecycle closures that resolve
remote script paths and dispatch to the right runner.
"""

import os

import pytest

from smpsave.core import server_lifecycle as sl
from smpsave.core.config import CoreConfig
from tests.mocks import MockProvisioner


def make_core_config(**overrides) -> CoreConfig:
    params = {
        "provisioner": "linode",
        "local_server_dir": "./server",
        "remote_server_dir": "~/server",
    }
    params.update(overrides)
    return CoreConfig(**params)


# --------------------------------------------------------------------------- #
# wait_for_ssh
# --------------------------------------------------------------------------- #


def test_wait_for_ssh_returns_on_first_success(monkeypatch):
    calls = []
    monkeypatch.setattr(sl.subprocess, "call", lambda cmd: calls.append(cmd) or 0)
    slept = []
    monkeypatch.setattr(sl.time, "sleep", lambda s: slept.append(s))

    sl.wait_for_ssh(make_core_config(), "root", "host")

    assert len(calls) == 1
    assert slept == []  # succeeded immediately, no backoff


def test_wait_for_ssh_retries_until_ready(monkeypatch):
    results = iter([255, 255, 0])
    call_count = {"n": 0}

    def fake_call(cmd):
        call_count["n"] += 1
        return next(results)

    monkeypatch.setattr(sl.subprocess, "call", fake_call)
    monkeypatch.setattr(sl.time, "sleep", lambda _s: None)

    sl.wait_for_ssh(make_core_config(), "root", "host")

    assert call_count["n"] == 3


def test_wait_for_ssh_times_out(monkeypatch):
    monkeypatch.setattr(sl.subprocess, "call", lambda _cmd: 255)
    monkeypatch.setattr(sl.time, "sleep", lambda _s: None)

    with pytest.raises(Exception, match="Timed out waiting for SSH"):
        sl.wait_for_ssh(make_core_config(), "root", "host")


# --------------------------------------------------------------------------- #
# lifecycle closures: script path resolution + runner dispatch
# --------------------------------------------------------------------------- #


def test_start_closure_runs_entry_point_script(monkeypatch):
    config = make_core_config(remote_server_dir="~/server", server_entry_point="go.sh")
    prov = MockProvisioner(host="1.2.3.4")
    captured = {}
    monkeypatch.setattr(
        sl,
        "run_remote_script",
        lambda cfg, user, host, path: captured.update(
            user=user, host=host, path=path
        ),
    )

    sl.build_start_closure(config, prov)()

    assert captured["host"] == "1.2.3.4"
    assert captured["user"] == config.remote_server_user
    assert captured["path"] == os.path.join("~/server", "go.sh")


def test_stop_closure_runs_graceful_stop_script(monkeypatch):
    config = make_core_config(remote_server_dir="~/server", server_graceful_stop="x.sh")
    prov = MockProvisioner(host="1.2.3.4")
    captured = {}
    monkeypatch.setattr(
        sl,
        "run_remote_script",
        lambda cfg, user, host, path: captured.update(path=path),
    )

    sl.build_stop_closure(config, prov)()

    assert captured["path"] == os.path.join("~/server", "x.sh")


def test_bootstrap_closure_pipes_local_script(monkeypatch):
    config = make_core_config(local_server_dir="./server", server_bootstrap="boot.sh")
    prov = MockProvisioner(host="1.2.3.4")
    captured = {}
    monkeypatch.setattr(
        sl,
        "run_local_script_remotely",
        lambda cfg, user, host, path: captured.update(host=host, path=path),
    )

    sl.build_bootstrap_closure(config, prov)()

    assert captured["host"] == "1.2.3.4"
    assert captured["path"] == os.path.join("./server", "boot.sh")


def test_wait_for_ssh_closure_passes_host(monkeypatch):
    config = make_core_config()
    prov = MockProvisioner(host="1.2.3.4")
    captured = {}
    monkeypatch.setattr(
        sl,
        "wait_for_ssh",
        lambda cfg, user, host: captured.update(user=user, host=host),
    )

    sl.build_wait_for_ssh_closure(config, prov)()

    assert captured == {"user": config.remote_server_user, "host": "1.2.3.4"}


def test_wait_for_ssh_closure_requires_host(monkeypatch):
    config = make_core_config()
    prov = MockProvisioner(host=None)  # server not provisioned
    monkeypatch.setattr(sl, "wait_for_ssh", lambda *a, **k: None)

    with pytest.raises(AssertionError):
        sl.build_wait_for_ssh_closure(config, prov)()
