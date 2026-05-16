"""Tests for scripts._cache — SQLite scrobble cache."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from scripts import _cache

# ---------------------------------------------------------------------------
# Pure helpers — no DB, no network.
# ---------------------------------------------------------------------------


def test_compute_gaps_empty_cache() -> None:
    assert _cache.compute_gaps(100, 200, None, None) == [(100, 200)]


def test_compute_gaps_request_inside_cached_range() -> None:
    # Cache covers [50, 500]; request [100, 200] is fully inside — no gaps.
    assert _cache.compute_gaps(100, 200, 50, 500) == []


def test_compute_gaps_request_extends_left_only() -> None:
    # Cache covers [100, 500]; request [50, 200] needs [50, 99].
    assert _cache.compute_gaps(50, 200, 100, 500) == [(50, 99)]


def test_compute_gaps_request_extends_right_only() -> None:
    # Cache covers [100, 500]; request [200, 600] needs [501, 600].
    assert _cache.compute_gaps(200, 600, 100, 500) == [(501, 600)]


def test_compute_gaps_request_extends_both_sides() -> None:
    # Cache covers [100, 500]; request [50, 600] needs both ends.
    assert _cache.compute_gaps(50, 600, 100, 500) == [(50, 99), (501, 600)]


def test_compute_gaps_request_entirely_before_cache() -> None:
    # Cache covers [500, 600]; request [100, 200] needs everything.
    # The watermarks will extend leftwards, but the new gap is [100, 499].
    assert _cache.compute_gaps(100, 200, 500, 600) == [(100, 499)]


def test_compute_gaps_request_entirely_after_cache() -> None:
    # Cache covers [100, 200]; request [500, 600] needs everything.
    assert _cache.compute_gaps(500, 600, 100, 200) == [(201, 600)]


def test_new_watermarks_extends_outward() -> None:
    # Request [50, 600] vs cache [100, 500] → cache grows to [50, 600].
    assert _cache.new_watermarks(50, 600, 100, 500) == (50, 600)


def test_new_watermarks_request_inside_cache() -> None:
    # Request inside cache leaves watermarks unchanged.
    assert _cache.new_watermarks(150, 200, 100, 500) == (100, 500)


def test_new_watermarks_empty_cache() -> None:
    # First fetch ever: the request defines the watermarks.
    assert _cache.new_watermarks(100, 200, None, None) == (100, 200)


def test_parse_tracks_skips_nowplaying() -> None:
    # A now-playing track has @attr.nowplaying and no `date` field.
    response: dict[str, Any] = {
        "recenttracks": {
            "track": [
                {
                    "@attr": {"nowplaying": "true"},
                    "artist": {"#text": "Live Artist"},
                    "name": "Now Playing",
                    "album": {"#text": "Album"},
                },
                {
                    "artist": {"#text": "Past Artist"},
                    "name": "Past Track",
                    "album": {"#text": "Past Album"},
                    "date": {"uts": "1700000000"},
                },
            ]
        }
    }
    rows = _cache.parse_tracks(response)
    assert rows == [(1700000000, "Past Artist", "Past Album", "Past Track")]


def test_parse_tracks_handles_missing_album() -> None:
    response: dict[str, Any] = {
        "recenttracks": {
            "track": [
                {
                    "artist": {"#text": "A"},
                    "name": "T",
                    "date": {"uts": "1700000000"},
                },
            ]
        }
    }
    rows = _cache.parse_tracks(response)
    assert rows == [(1700000000, "A", None, "T")]


def test_parse_tracks_handles_empty_album_string() -> None:
    # Last.fm returns "" for an unknown album. Treat as None for consistency.
    response: dict[str, Any] = {
        "recenttracks": {
            "track": [
                {
                    "artist": {"#text": "A"},
                    "name": "T",
                    "album": {"#text": ""},
                    "date": {"uts": "1700000000"},
                },
            ]
        }
    }
    rows = _cache.parse_tracks(response)
    assert rows == [(1700000000, "A", None, "T")]


def test_parse_tracks_handles_single_dict_track() -> None:
    # When only one track matches, last.fm returns a dict, not a list.
    response: dict[str, Any] = {
        "recenttracks": {
            "track": {
                "artist": {"#text": "Solo"},
                "name": "Only",
                "album": {"#text": "OneAlbum"},
                "date": {"uts": "1700000000"},
            }
        }
    }
    rows = _cache.parse_tracks(response)
    assert rows == [(1700000000, "Solo", "OneAlbum", "Only")]


def test_parse_tracks_empty_response() -> None:
    response: dict[str, Any] = {"recenttracks": {"track": []}}
    assert _cache.parse_tracks(response) == []


# ---------------------------------------------------------------------------
# Schema + watermark helpers — touch a tmp_path SQLite file but no network.
# ---------------------------------------------------------------------------


def test_schema_initialises_empty_db(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    conn = _cache.open_db(db)
    try:
        # Tables exist.
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        names = {row[0] for row in cur}
        assert "scrobbles" in names
        assert "metadata" in names
    finally:
        conn.close()


def test_get_set_watermarks_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    conn = _cache.open_db(db)
    try:
        assert _cache.get_watermarks(conn, "alice") == (None, None)
        _cache.set_watermarks(conn, "alice", 100, 500)
        assert _cache.get_watermarks(conn, "alice") == (100, 500)
        # Independent per user.
        assert _cache.get_watermarks(conn, "bob") == (None, None)
        _cache.set_watermarks(conn, "bob", 50, 300)
        assert _cache.get_watermarks(conn, "alice") == (100, 500)
        assert _cache.get_watermarks(conn, "bob") == (50, 300)
    finally:
        conn.close()


def test_insert_rows_dedupes_on_uts(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    conn = _cache.open_db(db)
    try:
        rows = [
            (1000, "Artist A", "Album A", "Track A"),
            (2000, "Artist B", None, "Track B"),
            (1000, "Artist A", "Album A", "Track A"),  # exact dup
        ]
        _cache.insert_rows(conn, rows)
        cur = conn.execute("SELECT COUNT(*) FROM scrobbles")
        assert cur.fetchone()[0] == 2
    finally:
        conn.close()


def test_query_range_returns_descending_uts(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    conn = _cache.open_db(db)
    try:
        _cache.insert_rows(
            conn,
            [
                (1000, "A", "X", "t1"),
                (3000, "C", None, "t3"),
                (2000, "B", "Y", "t2"),
            ],
        )
        result = _cache.query_range(conn, 1000, 3000)
        assert [r["date"]["uts"] for r in result] == ["3000", "2000", "1000"]
        # Spot-check shape matches user.getRecentTracks.
        assert result[0]["artist"]["#text"] == "C"
        assert result[0]["name"] == "t3"
        assert result[0]["album"]["#text"] == ""  # None album surfaces as empty string
        assert result[1]["album"]["#text"] == "Y"
    finally:
        conn.close()


def test_query_range_filters_by_bounds(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    conn = _cache.open_db(db)
    try:
        _cache.insert_rows(
            conn,
            [
                (1000, "A", "X", "t1"),
                (2000, "B", "Y", "t2"),
                (3000, "C", "Z", "t3"),
            ],
        )
        result = _cache.query_range(conn, 1500, 2500)
        assert [r["date"]["uts"] for r in result] == ["2000"]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# End-to-end get_scrobbles — monkeypatch `call` to avoid HTTP.
# ---------------------------------------------------------------------------


def _fake_response(*scrobbles: tuple[int, str, str | None, str]) -> dict[str, Any]:
    """Build a `user.getRecentTracks`-shaped response from tuples."""
    tracks = []
    for uts, artist, album, name in scrobbles:
        track: dict[str, Any] = {
            "artist": {"#text": artist},
            "name": name,
            "date": {"uts": str(uts)},
        }
        if album is not None:
            track["album"] = {"#text": album}
        tracks.append(track)
    return {
        "recenttracks": {
            "track": tracks,
            "@attr": {"totalPages": "1", "page": "1"},
        }
    }


def test_get_scrobbles_fetches_on_empty_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "test.db"
    monkeypatch.setattr(_cache, "DB_PATH", db)

    calls: list[dict[str, Any]] = []

    def fake_call(method: str, **kw: Any) -> dict[str, Any]:
        calls.append({"method": method, **kw})
        return _fake_response(
            (1500, "Artist A", "Album A", "Track 1"),
            (1700, "Artist B", "Album B", "Track 2"),
        )

    monkeypatch.setattr(_cache, "call", fake_call)

    result = _cache.get_scrobbles("alice", 1000, 2000)
    assert len(result) == 2
    assert result[0]["date"]["uts"] == "1700"
    # One fetch (or more, paginated) was made; method is user.getRecentTracks.
    assert all(c["method"] == "user.getRecentTracks" for c in calls)
    assert len(calls) >= 1


def test_get_scrobbles_no_fetch_when_range_cached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "test.db"
    monkeypatch.setattr(_cache, "DB_PATH", db)

    # Pre-warm the cache.
    conn = _cache.open_db(db)
    try:
        _cache.insert_rows(conn, [(1500, "A", "X", "t1"), (1700, "B", "Y", "t2")])
        _cache.set_watermarks(conn, "alice", 1000, 2000)
    finally:
        conn.close()

    def boom(method: str, **kw: Any) -> dict[str, Any]:
        raise AssertionError(f"unexpected API call: {method} {kw}")

    monkeypatch.setattr(_cache, "call", boom)

    result = _cache.get_scrobbles("alice", 1200, 1800)
    assert len(result) == 2


def test_get_scrobbles_extends_right_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "test.db"
    monkeypatch.setattr(_cache, "DB_PATH", db)

    conn = _cache.open_db(db)
    try:
        _cache.insert_rows(conn, [(1500, "A", "X", "t1")])
        _cache.set_watermarks(conn, "alice", 1000, 2000)
    finally:
        conn.close()

    calls: list[tuple[int, int]] = []

    def fake_call(method: str, **kw: Any) -> dict[str, Any]:
        calls.append((int(kw["from"]), int(kw["to"])))
        return _fake_response((2500, "C", "Z", "t3"))

    monkeypatch.setattr(_cache, "call", fake_call)

    result = _cache.get_scrobbles("alice", 1200, 3000)
    # The gap fetched should be (2001, 3000), not the original 1200-3000.
    assert calls == [(2001, 3000)]
    # Result includes both the cached and the newly-fetched scrobbles.
    assert sorted(r["date"]["uts"] for r in result) == ["1500", "2500"]

    # Watermarks now cover [1000, 3000].
    conn = _cache.open_db(db)
    try:
        assert _cache.get_watermarks(conn, "alice") == (1000, 3000)
    finally:
        conn.close()


def test_get_scrobbles_paginates_when_more_pages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "test.db"
    monkeypatch.setattr(_cache, "DB_PATH", db)

    pages = {
        1: {
            "recenttracks": {
                "track": [
                    {
                        "artist": {"#text": "A"},
                        "name": "t1",
                        "album": {"#text": ""},
                        "date": {"uts": "1500"},
                    }
                ],
                "@attr": {"totalPages": "2", "page": "1"},
            }
        },
        2: {
            "recenttracks": {
                "track": [
                    {
                        "artist": {"#text": "B"},
                        "name": "t2",
                        "album": {"#text": ""},
                        "date": {"uts": "1100"},
                    }
                ],
                "@attr": {"totalPages": "2", "page": "2"},
            }
        },
    }

    def fake_call(method: str, **kw: Any) -> dict[str, Any]:
        page = int(kw.get("page", 1))
        return pages[page]

    monkeypatch.setattr(_cache, "call", fake_call)

    result = _cache.get_scrobbles("alice", 1000, 2000)
    assert sorted(r["date"]["uts"] for r in result) == ["1100", "1500"]


def test_get_scrobbles_validates_from_lt_to(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "test.db"
    monkeypatch.setattr(_cache, "DB_PATH", db)
    with pytest.raises(ValueError):
        _cache.get_scrobbles("alice", 2000, 1000)


def test_get_scrobbles_rejects_empty_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "test.db"
    monkeypatch.setattr(_cache, "DB_PATH", db)
    with pytest.raises(ValueError):
        _cache.get_scrobbles("", 1000, 2000)


def test_cache_survives_reopen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "test.db"
    monkeypatch.setattr(_cache, "DB_PATH", db)

    call_count = {"n": 0}

    def fake_call(method: str, **kw: Any) -> dict[str, Any]:
        call_count["n"] += 1
        return _fake_response((1500, "A", "X", "t1"))

    monkeypatch.setattr(_cache, "call", fake_call)

    # First call fetches.
    _cache.get_scrobbles("alice", 1000, 2000)
    first = call_count["n"]
    # Second call (same range) finds everything in cache.
    _cache.get_scrobbles("alice", 1000, 2000)
    assert call_count["n"] == first


def test_db_file_is_created_at_repo_root() -> None:
    # Just confirm the default path lives at the repo root.
    assert _cache.DB_PATH.name == "antiphon.db"
    assert _cache.DB_PATH.parent == Path(__file__).resolve().parent.parent


def test_sqlite_schema_artist_track_not_null(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    conn = _cache.open_db(db)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO scrobbles (uts, artist, album, track) VALUES (?, ?, ?, ?)",
                (1000, None, "x", "t"),
            )
            conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO scrobbles (uts, artist, album, track) VALUES (?, ?, ?, ?)",
                (1001, "A", "x", None),
            )
            conn.commit()
    finally:
        conn.close()
