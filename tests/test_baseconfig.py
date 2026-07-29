from dataclasses import dataclass

import pytest

from smpsave.configuration.baseconfig import BaseConfig, ConfigurationParsingException


@dataclass
class SampleConfig(BaseConfig):
    """A minimal config used to exercise BaseConfig's parsing behavior."""

    count: int
    items: list[str]
    name: str = "default"


def test_int_field_is_parsed_from_string():
    # ConfigParser only ever yields strings, so BaseConfig must coerce them.
    config = SampleConfig(count="5", items="a")
    assert config.count == 5
    assert isinstance(config.count, int)


def test_list_field_is_split_on_commas():
    config = SampleConfig(count="0", items="a,b,c")
    assert config.items == ["a", "b", "c"]


def test_single_item_list_is_a_one_element_list():
    config = SampleConfig(count="0", items="only")
    assert config.items == ["only"]


def test_unparseable_int_raises_configuration_parsing_exception():
    with pytest.raises(ConfigurationParsingException):
        SampleConfig(count="not-a-number", items="a")


def test_string_field_is_left_untouched():
    config = SampleConfig(count="1", items="a", name="keep me")
    assert config.name == "keep me"


def test_redact_masks_secret_in_repr():
    config = SampleConfig(count="1", items="a", name="s3cr3t")
    redacted = config._redact("s3cr3t")
    assert "s3cr3t" not in redacted
    assert "******" in redacted


def test_redact_leaves_repr_unchanged_for_empty_secret():
    config = SampleConfig(count="1", items="a")
    assert config._redact("") == repr(config)
