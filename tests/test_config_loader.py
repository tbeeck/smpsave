"""Tests for config_loader: file discovery, caching, and namespace resolution."""

from configparser import ConfigParser

import pytest

from smpsave.configuration import config_loader
from smpsave.core.config import CoreConfig


@pytest.fixture(autouse=True)
def reset_parser_cache(monkeypatch):
    # load_configs memoizes into a module global; isolate each test from it.
    monkeypatch.setattr(config_loader, "CONFIG_PARSER", None)


def test_load_configs_raises_when_no_files(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # empty dir, no config.ini / user.ini
    with pytest.raises(config_loader.LoadConfigurationException):
        config_loader.load_configs()


def test_load_configs_reads_present_file_and_caches(monkeypatch, tmp_path):
    (tmp_path / "config.ini").write_text("[core]\nprovisioner = linode\n")
    monkeypatch.chdir(tmp_path)

    first = config_loader.load_configs()
    assert first.has_section("core")
    # Second call returns the cached parser instance, not a fresh read.
    assert config_loader.load_configs() is first


def test_get_configurations_raises_on_missing_namespace(monkeypatch):
    monkeypatch.setattr(config_loader, "load_configs", lambda: ConfigParser())
    with pytest.raises(config_loader.LoadConfigurationException, match="nope"):
        config_loader.get_configurations("nope", CoreConfig)


def test_get_configurations_builds_config_from_section(monkeypatch):
    parser = ConfigParser()
    parser["core"] = {
        "provisioner": "linode",
        "local_server_dir": "./server",
        "remote_server_dir": "~/server",
    }
    monkeypatch.setattr(config_loader, "load_configs", lambda: parser)

    config = config_loader.get_configurations("core", CoreConfig)

    assert isinstance(config, CoreConfig)
    assert config.provisioner == "linode"
    assert config.remote_server_dir == "~/server"
