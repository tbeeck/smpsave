"""
Regression tests for token resolution: a token must be usable from the
environment alone, without a placeholder value in the INI file, and its absence
from both sources must fail loudly.
"""

import pytest

from smpsave.configuration.baseconfig import ConfigurationInitializationException
from smpsave.discordbot.config import DiscordBotConfig
from smpsave.provisioning.linode import LinodeProvisionerConfig


def make_linode_config(**overrides) -> LinodeProvisionerConfig:
    params = {
        "linode_type": "g6-nanode-1",
        "linode_image": "linode/debian13",
        "linode_label": "smpsave-test",
        "linode_region": "us-lax",
        "public_key_path": "~/.ssh/id_ed25519.pub",
    }
    params.update(overrides)
    return LinodeProvisionerConfig(**params)


@pytest.fixture(autouse=True)
def clear_token_env(monkeypatch):
    # The developer shell may export these; isolate every test from it.
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("LINODE_TOKEN", raising=False)


def test_discord_token_from_env_only(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "env-token")
    config = DiscordBotConfig(allowed_role="0")
    assert config.token == "env-token"


def test_discord_token_from_ini_only():
    config = DiscordBotConfig(allowed_role="0", token="ini-token")
    assert config.token == "ini-token"


def test_discord_env_overrides_ini(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "env-token")
    config = DiscordBotConfig(allowed_role="0", token="ini-token")
    assert config.token == "env-token"


def test_discord_missing_token_raises():
    with pytest.raises(ConfigurationInitializationException):
        DiscordBotConfig(allowed_role="0")


def test_discord_token_is_redacted_in_str():
    config = DiscordBotConfig(allowed_role="0", token="super-secret")
    rendered = str(config)
    assert "super-secret" not in rendered
    assert "******" in rendered


def test_linode_token_from_env_only(monkeypatch):
    monkeypatch.setenv("LINODE_TOKEN", "env-token")
    config = make_linode_config()
    assert config.access_token == "env-token"


def test_linode_token_from_ini_only():
    config = make_linode_config(access_token="ini-token")
    assert config.access_token == "ini-token"


def test_linode_env_overrides_ini(monkeypatch):
    monkeypatch.setenv("LINODE_TOKEN", "env-token")
    config = make_linode_config(access_token="ini-token")
    assert config.access_token == "env-token"


def test_linode_missing_token_raises():
    with pytest.raises(ConfigurationInitializationException):
        make_linode_config()
