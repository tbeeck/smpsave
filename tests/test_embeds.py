"""Tests for embeds.format_duration, the one piece of embed logic with
branching worth pinning down.
"""

from datetime import timedelta

from smpsave.discordbot.embeds import format_duration


def test_format_duration_hours_and_minutes():
    assert format_duration(timedelta(hours=1, minutes=30)) == "1h 30m"


def test_format_duration_drops_seconds_when_hours_present():
    assert format_duration(timedelta(hours=2, minutes=5, seconds=45)) == "2h 5m"


def test_format_duration_minutes_and_seconds():
    assert format_duration(timedelta(minutes=5, seconds=9)) == "5m 9s"


def test_format_duration_seconds_only():
    assert format_duration(timedelta(seconds=42)) == "42s"


def test_format_duration_zero():
    assert format_duration(timedelta(0)) == "0s"


def test_format_duration_clamps_negative_to_zero():
    assert format_duration(timedelta(seconds=-30)) == "0s"
