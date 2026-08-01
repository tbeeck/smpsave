from unittest.mock import patch

from smpsave.core import filesync
from smpsave.core.config import CoreConfig
from smpsave.core.filesync import (
    _as_sync_source,
    build_backup_closure,
    build_upload_closure,
    ensure_remote_dir,
    rsync,
)
from tests.mocks import MockProvisioner


def make_core_config(**overrides) -> CoreConfig:
    params = {
        "provisioner": "linode",
        "local_server_dir": "./server",
        "remote_server_dir": "~/server",
    }
    params.update(overrides)
    return CoreConfig(**params)


def test_as_sync_source_appends_trailing_slash():
    assert _as_sync_source("./server") == "./server/"
    assert _as_sync_source("root@host:~/server") == "root@host:~/server/"


def test_as_sync_source_preserves_existing_trailing_slash():
    assert _as_sync_source("./server/") == "./server/"
    assert _as_sync_source("root@host:~/server/") == "root@host:~/server/"


def test_rsync_normalizes_source_without_trailing_slash():
    config = make_core_config()
    with patch("smpsave.core.filesync.subprocess.run") as run:
        run.return_value.returncode = 0
        rsync(config, "./server", "root@host:~/server")

    command = run.call_args.args[0]
    src = command[-2]
    assert src == "./server/"


def test_ensure_remote_dir_runs_mkdir_over_ssh():
    config = make_core_config()
    with patch("smpsave.core.filesync.subprocess.call") as call:
        call.return_value = 0
        ensure_remote_dir(config, "root", "host", "~/server")

    command = call.call_args.args[0]
    assert command[0] == "ssh"
    assert command[-2] == "root@host"
    assert command[-1] == "mkdir -p ~/server"


def test_ensure_remote_dir_raises_on_failure():
    config = make_core_config()
    with patch("smpsave.core.filesync.subprocess.call") as call:
        call.return_value = 1
        raised = False
        try:
            ensure_remote_dir(config, "root", "host", "~/server")
        except Exception:
            raised = True
    assert raised


def test_upload_closure_ensures_dir_then_syncs_local_to_remote():
    config = make_core_config(
        local_server_dir="./server",
        remote_server_dir="~/server",
        remote_server_user="root",
    )
    prov = MockProvisioner(host="1.2.3.4")
    with (
        patch.object(filesync, "ensure_remote_dir") as ensure,
        patch.object(filesync, "rsync") as sync,
    ):
        build_upload_closure(config, prov)()

    ensure.assert_called_once_with(config, "root", "1.2.3.4", "~/server")
    src, dst = sync.call_args.args[1], sync.call_args.args[2]
    assert src == "./server"
    assert dst == "root@1.2.3.4:~/server"


def test_backup_closure_syncs_remote_to_local():
    config = make_core_config(
        local_server_dir="./server",
        remote_server_dir="~/server",
        remote_server_user="root",
    )
    prov = MockProvisioner(host="1.2.3.4")
    with patch.object(filesync, "rsync") as sync:
        build_backup_closure(config, prov)()

    src, dst = sync.call_args.args[1], sync.call_args.args[2]
    assert src == "root@1.2.3.4:~/server"
    assert dst == "./server"
