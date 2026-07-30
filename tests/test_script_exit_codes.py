from unittest.mock import MagicMock, patch

import pytest

from smpsave.core.config import CoreConfig
from smpsave.core.server_lifecycle import (
    run_local_script_remotely,
    run_remote_script,
)


def make_core_config(**overrides) -> CoreConfig:
    params = {
        "provisioner": "linode",
        "local_server_dir": "./server/",
        "remote_server_dir": "~/server/",
    }
    params.update(overrides)
    return CoreConfig(**params)


def test_run_remote_script_raises_on_nonzero_exit():
    config = make_core_config()
    with patch("smpsave.core.server_lifecycle.subprocess.call") as call:
        call.return_value = 1
        with pytest.raises(Exception, match="exit code"):
            run_remote_script(config, "root", "host", "~/server/start.sh")


def test_run_remote_script_succeeds_on_zero_exit():
    config = make_core_config()
    with patch("smpsave.core.server_lifecycle.subprocess.call") as call:
        call.return_value = 0
        run_remote_script(config, "root", "host", "~/server/start.sh")


def test_run_local_script_remotely_raises_on_nonzero_exit(tmp_path):
    config = make_core_config()
    script = tmp_path / "bootstrap.sh"
    script.write_text("echo hi\n")

    proc = MagicMock()
    proc.returncode = 1
    with patch("smpsave.core.server_lifecycle.subprocess.Popen", return_value=proc):
        with pytest.raises(Exception, match="exited with code"):
            run_local_script_remotely(config, "root", "host", str(script))


def test_run_local_script_remotely_succeeds_on_zero_exit(tmp_path):
    config = make_core_config()
    script = tmp_path / "bootstrap.sh"
    script.write_text("echo hi\n")

    proc = MagicMock()
    proc.returncode = 0
    with patch("smpsave.core.server_lifecycle.subprocess.Popen", return_value=proc):
        run_local_script_remotely(config, "root", "host", str(script))
