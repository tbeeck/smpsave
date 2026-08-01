"""Tests for LinodeProvisioner, the real provisioner behind the bot's
start/stop. The Linode SDK client is replaced with an in-memory mock so the
provision/deprovision branching, host resolution, and hook wrapping can be
exercised without network access.
"""

import pytest

from smpsave.provisioning import linode
from smpsave.provisioning.linode import LinodeProvisioner, LinodeProvisionerConfig
from tests.mocks import MockLinodeClient, MockLinodeInstance


def make_linode_config(**overrides) -> LinodeProvisionerConfig:
    params = {
        "linode_type": "g6-nanode-1",
        "linode_image": "linode/debian13",
        "linode_label": "smpsave-test",
        "linode_region": "us-lax",
        "public_key_path": "~/.ssh/id_ed25519.pub",
        "access_token": "test-token",
    }
    params.update(overrides)
    return LinodeProvisionerConfig(**params)


def make_provisioner(monkeypatch, instances=None, create_result=None, **config_over):
    client = MockLinodeClient(instances=instances, create_result=create_result)
    monkeypatch.setattr(linode, "LinodeClient", lambda token: client)
    provisioner = LinodeProvisioner(make_linode_config(**config_over))
    return provisioner, client


# --------------------------------------------------------------------------- #
# start
# --------------------------------------------------------------------------- #


def test_start_is_idempotent_when_instance_exists(monkeypatch):
    existing = MockLinodeInstance(label="smpsave-test")
    prov, client = make_provisioner(monkeypatch, instances=[existing])
    ran = []
    prov.set_poststart_hooks([lambda: ran.append("hook")])

    prov.start()

    assert client.linode.create_calls == []  # no second instance provisioned
    assert ran == []  # hooks are only for a fresh provision


def test_start_provisions_and_runs_hooks_with_image(monkeypatch):
    created = MockLinodeInstance(status="running")
    # With an image, the SDK returns (instance, root_password).
    prov, client = make_provisioner(
        monkeypatch, create_result=(created, "root-pw")
    )
    ran = []
    prov.set_poststart_hooks([lambda: ran.append("hook")])

    result = prov.start()

    assert len(client.linode.create_calls) == 1
    assert result is created
    assert ran == ["hook"]


def test_start_handles_bare_instance_without_image(monkeypatch):
    created = MockLinodeInstance(status="running")
    # Without an image, the SDK returns a bare Instance (no tuple).
    prov, client = make_provisioner(monkeypatch, create_result=created)

    result = prov.start()

    assert len(client.linode.create_calls) == 1
    assert result is created


# --------------------------------------------------------------------------- #
# stop
# --------------------------------------------------------------------------- #


def test_stop_is_noop_when_no_instance(monkeypatch):
    prov, _ = make_provisioner(monkeypatch, instances=[])
    ran = []
    prov.set_prestop_hooks([lambda: ran.append("hook")])

    prov.stop()

    assert ran == []


def test_stop_runs_prestop_hooks_and_deletes(monkeypatch):
    instance = MockLinodeInstance(label="smpsave-test")
    prov, _ = make_provisioner(monkeypatch, instances=[instance])
    ran = []
    prov.set_prestop_hooks([lambda: ran.append("hook")])

    prov.stop()

    assert ran == ["hook"]
    assert instance.delete_calls == 1


def test_stop_force_skips_prestop_hooks(monkeypatch):
    instance = MockLinodeInstance(label="smpsave-test")
    prov, _ = make_provisioner(monkeypatch, instances=[instance])
    ran = []
    prov.set_prestop_hooks([lambda: ran.append("hook")])

    prov.stop(force=True)

    assert ran == []
    assert instance.delete_calls == 1


def test_stop_raises_when_delete_fails(monkeypatch):
    instance = MockLinodeInstance(label="smpsave-test", delete_result=False)
    prov, _ = make_provisioner(monkeypatch, instances=[instance])
    prov.set_prestop_hooks([])

    with pytest.raises(Exception, match="Failed to delete"):
        prov.stop()


# --------------------------------------------------------------------------- #
# get_host
# --------------------------------------------------------------------------- #


def test_get_host_returns_none_when_no_instance(monkeypatch):
    prov, _ = make_provisioner(monkeypatch, instances=[])
    assert prov.get_host() is None


def test_get_host_returns_first_ipv4(monkeypatch):
    instance = MockLinodeInstance(label="smpsave-test", ipv4=["5.6.7.8"])
    prov, _ = make_provisioner(monkeypatch, instances=[instance])
    assert prov.get_host() == "5.6.7.8"


def test_get_host_raises_when_no_public_ip(monkeypatch):
    instance = MockLinodeInstance(label="smpsave-test", ipv4=[])
    prov, _ = make_provisioner(monkeypatch, instances=[instance])
    with pytest.raises(Exception, match="No public IP"):
        prov.get_host()


# --------------------------------------------------------------------------- #
# _get_instance label matching
# --------------------------------------------------------------------------- #


def test_get_instance_matches_configured_label(monkeypatch):
    wanted = MockLinodeInstance(id=2, label="smpsave-test")
    other = MockLinodeInstance(id=3, label="someone-elses-box")
    prov, _ = make_provisioner(monkeypatch, instances=[other, wanted])
    assert prov._get_instance() is wanted


def test_get_instance_none_when_label_absent(monkeypatch):
    other = MockLinodeInstance(id=3, label="someone-elses-box")
    prov, _ = make_provisioner(monkeypatch, instances=[other])
    assert prov._get_instance() is None


# --------------------------------------------------------------------------- #
# hook execution and error wrapping
# --------------------------------------------------------------------------- #


def test_hooks_run_in_registration_order(monkeypatch):
    prov, _ = make_provisioner(monkeypatch)
    order = []
    prov.set_poststart_hooks([lambda: order.append(1), lambda: order.append(2)])

    prov.run_poststart_hooks()

    assert order == [1, 2]


def test_failing_hook_is_wrapped_with_stage(monkeypatch):
    prov, _ = make_provisioner(monkeypatch)

    def boom():
        raise ValueError("nope")

    prov.set_prestop_hooks([boom])

    with pytest.raises(Exception, match="pre-stop hook failed"):
        prov.run_prestop_hooks()


# --------------------------------------------------------------------------- #
# polling timeouts
# --------------------------------------------------------------------------- #


def test_poll_until_ready_times_out(monkeypatch):
    prov, _ = make_provisioner(monkeypatch)
    instance = MockLinodeInstance(status="provisioning")  # never becomes running
    monkeypatch.setattr(linode.time, "sleep", lambda _s: None)
    clock = iter([0, 1, linode.POLL_TIMEOUT_SECONDS + 1])
    monkeypatch.setattr(linode.time, "time", lambda: next(clock))

    with pytest.raises(Exception, match="Timeout waiting for instance to be ready"):
        prov._poll_until_instance_ready(instance)


def test_poll_until_ready_returns_when_running(monkeypatch):
    prov, _ = make_provisioner(monkeypatch)
    instance = MockLinodeInstance(status="running")
    assert prov._poll_until_instance_ready(instance) is True
