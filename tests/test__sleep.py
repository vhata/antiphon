"""Tests for scripts._sleep — the shared sleep_albums.md parser."""

from __future__ import annotations

from pathlib import Path

from scripts import _sleep

SAMPLE = """\
# Sleep albums

Records the listener falls asleep to. Scrobbles matching any of
these (by artist + album, case-insensitive) are filtered out of
behavioural views such as the heat-map.

## Filter list

- **Brian Eno — *Music for Airports***
- **Stars of the Lid — *And Their Refinement of the Decline***
- **Max Richter — *From Sleep***
"""

NO_BULLETS = """\
# Sleep albums

This file is empty.

## Filter list

*(none yet)*
"""


def test_parse_returns_empty_list_for_empty_text() -> None:
    assert _sleep.parse("") == []


def test_parse_returns_empty_list_when_only_placeholder() -> None:
    assert _sleep.parse(NO_BULLETS) == []


def test_parse_extracts_artist_album_tuples() -> None:
    pairs = _sleep.parse(SAMPLE)
    assert ("brian eno", "music for airports") in pairs
    assert ("stars of the lid", "and their refinement of the decline") in pairs
    assert ("max richter", "from sleep") in pairs
    assert len(pairs) == 3


def test_parse_lowercases_both_artist_and_album() -> None:
    pairs = _sleep.parse("- **BRIAN ENO — *Music for Airports***")
    assert pairs == [("brian eno", "music for airports")]


def test_parse_skips_bullets_without_album() -> None:
    pairs = _sleep.parse("- **Just an artist**\n- **Brian Eno — *Music for Airports***")
    assert pairs == [("brian eno", "music for airports")]


def test_load_returns_empty_list_when_file_missing(tmp_path: Path) -> None:
    missing = tmp_path / "no_such_file.md"
    assert _sleep.load(missing) == []


def test_load_reads_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "sleep_albums.md"
    path.write_text(SAMPLE)
    pairs = _sleep.load(path)
    assert ("brian eno", "music for airports") in pairs
    assert len(pairs) == 3


def test_matches_handles_case_insensitive_compare() -> None:
    pairs = [("brian eno", "music for airports")]
    assert _sleep.matches("Brian Eno", "Music for Airports", pairs) is True
    assert _sleep.matches("BRIAN ENO", "MUSIC FOR AIRPORTS", pairs) is True
    assert _sleep.matches("brian eno", "thursday afternoon", pairs) is False
    assert _sleep.matches("aphex twin", "music for airports", pairs) is False


def test_matches_returns_false_when_filter_empty() -> None:
    assert _sleep.matches("Anyone", "Anything", []) is False
