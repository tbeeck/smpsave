import os

from smpsave.core.config import CoreConfig
from smpsave.core.server_lifecycle import ssh_options


def make_core_config(**overrides) -> CoreConfig:
    params = {
        "provisioner": "linode",
        "local_server_dir": "./server/",
        "remote_server_dir": "~/server/",
    }
    params.update(overrides)
    return CoreConfig(**params)


def test_ssh_options_build_expected_flags():
    config = make_core_config(
        ssh_private_key_path="/keys/id_ed25519",
        ssh_known_hosts_path="/dev/null",
        ssh_strict_host_key_checking="accept-new",
    )
    assert ssh_options(config) == [
        "-i",
        "/keys/id_ed25519",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "UserKnownHostsFile=/dev/null",
    ]


def test_ssh_options_expands_user_home_in_paths():
    config = make_core_config(
        ssh_private_key_path="~/mykey",
        ssh_known_hosts_path="~/known_hosts",
    )
    opts = ssh_options(config)

    key_path = opts[opts.index("-i") + 1]
    assert key_path == os.path.expanduser("~/mykey")
    assert "~" not in key_path

    known_hosts_opt = next(o for o in opts if o.startswith("UserKnownHostsFile="))
    expected_known_hosts = os.path.expanduser("~/known_hosts")
    assert known_hosts_opt == f"UserKnownHostsFile={expected_known_hosts}"


def test_ssh_options_reflect_strict_host_key_checking_setting():
    config = make_core_config(ssh_strict_host_key_checking="yes")
    assert "StrictHostKeyChecking=yes" in ssh_options(config)
