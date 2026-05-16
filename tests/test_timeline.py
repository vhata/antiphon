"""Tests for scripts.timeline — pure year-grouping and first-scrobble logic."""

from __future__ import annotations

from typing import Any

import pytest

from scripts import timeline


def _scrobble(
    uts: int, artist: str, track: str = "track", album: str | None = None
) -> dict[str, Any]:
    """Build a scrobble dict in the shape `user.getRecentTracks` returns."""
    return {
        "date": {"uts": str(uts), "#text": ""},
        "artist": {"#text": artist, "mbid": ""},
        "album": {"#text": album or ""},
        "name": track,
    }


def test_module_exposes_main_and_helpers() -> None:
    assert hasattr(timeline, "main")
    assert hasattr(timeline, "earliest_uts_by_artist")
    assert hasattr(timeline, "group_by_year")
    assert hasattr(timeline, "build_timeline")


def test_earliest_uts_by_artist_finds_earliest() -> None:
    scrobbles = [
        _scrobble(2_000, "Pink Floyd"),
        _scrobble(1_500, "Pink Floyd"),
        _scrobble(1_800, "Pink Floyd"),
        _scrobble(3_000, "Massive Attack"),
    ]
    artists = ["Pink Floyd", "Massive Attack"]
    result = timeline.earliest_uts_by_artist(scrobbles, artists)
    assert result == {"Pink Floyd": 1_500, "Massive Attack": 3_000}


def test_earliest_uts_by_artist_is_case_insensitive() -> None:
    scrobbles = [
        _scrobble(1_000, "massive attack"),
        _scrobble(2_000, "MASSIVE ATTACK"),
    ]
    result = timeline.earliest_uts_by_artist(scrobbles, ["Massive Attack"])
    assert result == {"Massive Attack": 1_000}


def test_earliest_uts_by_artist_skips_unmatched() -> None:
    scrobbles = [_scrobble(1_000, "Pink Floyd")]
    result = timeline.earliest_uts_by_artist(scrobbles, ["Pink Floyd", "Unknown"])
    assert result == {"Pink Floyd": 1_000}
    assert "Unknown" not in result


def test_earliest_uts_by_artist_empty_inputs() -> None:
    assert timeline.earliest_uts_by_artist([], []) == {}
    assert timeline.earliest_uts_by_artist([], ["X"]) == {}
    assert timeline.earliest_uts_by_artist([_scrobble(1, "X")], []) == {}


def test_earliest_uts_by_artist_skips_tracks_without_date() -> None:
    """Now-playing entries without a `date` field must be ignored."""
    scrobbles: list[dict[str, Any]] = [
        {"@attr": {"nowplaying": "true"}, "artist": {"#text": "Pink Floyd"}, "name": "X"},
        _scrobble(1_000, "Pink Floyd"),
    ]
    result = timeline.earliest_uts_by_artist(scrobbles, ["Pink Floyd"])
    assert result == {"Pink Floyd": 1_000}


def test_group_by_year_buckets_correctly() -> None:
    # 2008-01-01 = 1199145600; 2009-06-15 = 1244995200
    earliest = {
        "Massive Attack": 1_199_145_600,
        "Pink Floyd": 1_199_145_700,
        "Portishead": 1_244_995_200,
    }
    ranks = {"Massive Attack": 1, "Pink Floyd": 5, "Portishead": 3}
    grouped = timeline.group_by_year(earliest, ranks)
    assert list(grouped.keys()) == [2008, 2009]
    assert grouped[2008] == ["Massive Attack", "Pink Floyd"]
    assert grouped[2009] == ["Portishead"]


def test_group_by_year_sorts_within_year_by_rank() -> None:
    earliest = {"A": 1_000_000_000, "B": 1_000_000_100, "C": 1_000_000_200}
    ranks = {"A": 10, "B": 1, "C": 5}
    grouped = timeline.group_by_year(earliest, ranks)
    only_year = next(iter(grouped))
    assert grouped[only_year] == ["B", "C", "A"]


def test_group_by_year_falls_back_to_alpha_without_rank() -> None:
    earliest = {"Alpha": 1_000_000_000, "Beta": 1_000_000_100}
    grouped = timeline.group_by_year(earliest, {})
    only_year = next(iter(grouped))
    assert grouped[only_year] == ["Alpha", "Beta"]


def test_group_by_year_empty() -> None:
    assert timeline.group_by_year({}, {}) == {}


def test_build_timeline_integrates_calls_and_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_top = [
        {"@attr": {"rank": "1"}, "name": "Pink Floyd"},
        {"@attr": {"rank": "2"}, "name": "Massive Attack"},
    ]

    def fake_call(method: str, **params: object) -> dict[str, Any]:
        assert method == "user.getTopArtists"
        return {"topartists": {"artist": fake_top}}

    fake_scrobbles = [
        _scrobble(1_199_145_600, "Pink Floyd"),  # 2008
        _scrobble(1_244_995_200, "Massive Attack"),  # 2009
        _scrobble(1_500_000_000, "Pink Floyd"),  # later play, ignored
    ]

    def fake_get_scrobbles(user: str, from_uts: int, to_uts: int) -> list[dict[str, Any]]:
        assert user == "tester"
        assert from_uts == 0
        return fake_scrobbles

    monkeypatch.setattr(timeline, "call", fake_call)
    monkeypatch.setattr(timeline, "get_scrobbles", fake_get_scrobbles)
    monkeypatch.setattr(timeline, "now_uts", lambda: 1_600_000_000)

    result = timeline.build_timeline("tester")
    assert result["years"] == {2008: ["Pink Floyd"], 2009: ["Massive Attack"]}
    assert result["scrobble_count"] == 3
    assert result["range"] == (1_199_145_600, 1_500_000_000)


def test_build_timeline_handles_no_scrobbles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        timeline,
        "call",
        lambda method, **kw: {"topartists": {"artist": [{"@attr": {"rank": "1"}, "name": "X"}]}},
    )
    monkeypatch.setattr(timeline, "get_scrobbles", lambda *a, **kw: [])
    monkeypatch.setattr(timeline, "now_uts", lambda: 1_600_000_000)
    result = timeline.build_timeline("tester")
    assert result["years"] == {}
    assert result["scrobble_count"] == 0
    assert result["range"] is None


def test_year_for_uts_uses_utc() -> None:
    assert timeline.year_for_uts(1_199_145_600) == 2008  # 2008-01-01 00:00:00 UTC
    assert timeline.year_for_uts(1_199_145_599) == 2007  # one second earlier


def test_default_top_n_is_50() -> None:
    assert timeline.DEFAULT_TOP_N == 50
