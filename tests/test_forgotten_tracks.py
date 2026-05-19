"""Tests for scripts.forgotten_tracks — SQL-backed forgotten-favourite retrieval."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts import forgotten_tracks


def _seed(
    db_path: Path,
    user: str = "tester",
    rows: list[tuple[int, str, str | None, str]] | None = None,
    watermark: tuple[int, int] | None = (1_000_000_000, 1_700_000_000),
) -> None:
    """Create a cache DB with the given scrobble rows and watermarks.

    `rows` are (uts, artist, album, track) tuples.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS scrobbles "
            "(uts INTEGER PRIMARY KEY, artist TEXT NOT NULL, album TEXT, track TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value INTEGER NOT NULL)"
        )
        if rows:
            conn.executemany(
                "INSERT OR IGNORE INTO scrobbles (uts, artist, album, track) VALUES (?, ?, ?, ?)",
                rows,
            )
        if watermark is not None:
            oldest, newest = watermark
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (f"oldest_uts_cached:{user}", oldest),
            )
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (f"newest_uts_cached:{user}", newest),
            )
        conn.commit()
    finally:
        conn.close()


def test_finds_track_played_many_times_long_ago(tmp_path: Path) -> None:
    """A track with 30 plays, last touched 2 years ago, surfaces."""
    db = tmp_path / "antiphon.db"
    today = 1_700_000_000
    long_ago = today - 2 * 365 * 86400  # ~2 years ago
    rows: list[tuple[int, str, str | None, str]] = [
        (long_ago + i, "Heavy Artist", None, "Old Favourite") for i in range(30)
    ]
    _seed(db, rows=rows)

    result = forgotten_tracks.find_forgotten_tracks(
        min_plays=20,
        dormancy_days=365,
        limit=10,
        db_path=db,
        today_uts=today,
    )
    assert len(result) == 1
    artist, track, plays, last = result[0]
    assert (artist, track, plays) == ("Heavy Artist", "Old Favourite", 30)
    assert last < today - 365 * 86400


def test_excludes_recently_played_tracks(tmp_path: Path) -> None:
    db = tmp_path / "antiphon.db"
    today = 1_700_000_000
    rows: list[tuple[int, str, str | None, str]] = [
        (today - i * 1000, "Recent Artist", None, "Still Loved") for i in range(30)
    ]
    _seed(db, rows=rows)
    result = forgotten_tracks.find_forgotten_tracks(
        db_path=db, today_uts=today, min_plays=20, dormancy_days=365
    )
    assert result == []


def test_excludes_tracks_below_min_plays(tmp_path: Path) -> None:
    db = tmp_path / "antiphon.db"
    today = 1_700_000_000
    long_ago = today - 2 * 365 * 86400
    rows: list[tuple[int, str, str | None, str]] = [
        (long_ago + i, "Sometime Artist", None, "Few Plays") for i in range(5)
    ]
    _seed(db, rows=rows)
    result = forgotten_tracks.find_forgotten_tracks(
        db_path=db, today_uts=today, min_plays=20, dormancy_days=365
    )
    assert result == []


def test_orders_by_plays_descending(tmp_path: Path) -> None:
    db = tmp_path / "antiphon.db"
    today = 1_700_000_000
    long_ago = today - 2 * 365 * 86400
    rows: list[tuple[int, str, str | None, str]] = []
    rows.extend((long_ago + i, "A", None, "Low Plays") for i in range(20))
    rows.extend((long_ago + 100 + i, "A", None, "High Plays") for i in range(50))
    _seed(db, rows=rows)
    result = forgotten_tracks.find_forgotten_tracks(
        db_path=db, today_uts=today, min_plays=20, dormancy_days=365
    )
    assert [(r[1], r[2]) for r in result] == [
        ("High Plays", 50),
        ("Low Plays", 20),
    ]


def test_respects_limit(tmp_path: Path) -> None:
    db = tmp_path / "antiphon.db"
    today = 1_700_000_000
    long_ago = today - 2 * 365 * 86400
    rows: list[tuple[int, str, str | None, str]] = []
    for track_idx in range(5):
        rows.extend(
            (long_ago + track_idx * 1000 + i, "A", None, f"Track {track_idx}")
            for i in range(25 - track_idx)
        )
    _seed(db, rows=rows)
    result = forgotten_tracks.find_forgotten_tracks(
        db_path=db, today_uts=today, min_plays=20, dormancy_days=365, limit=3
    )
    assert len(result) == 3


def test_dormancy_days_threshold(tmp_path: Path) -> None:
    """A track whose newest play is *just inside* the dormancy window is excluded."""
    db = tmp_path / "antiphon.db"
    today = 1_700_000_000
    inside_window = today - 30 * 86400  # 30 days ago — well within 365
    rows: list[tuple[int, str, str | None, str]] = [
        (inside_window - i, "A", None, "Recent enough") for i in range(30)
    ]
    _seed(db, rows=rows)
    result = forgotten_tracks.find_forgotten_tracks(
        db_path=db, today_uts=today, min_plays=20, dormancy_days=365
    )
    assert result == []


def test_empty_database_returns_empty(tmp_path: Path) -> None:
    db = tmp_path / "antiphon.db"
    _seed(db, rows=[])
    result = forgotten_tracks.find_forgotten_tracks(
        db_path=db, today_uts=1_700_000_000, min_plays=20, dormancy_days=365
    )
    assert result == []


def test_module_exposes_main_and_constants() -> None:
    assert hasattr(forgotten_tracks, "main")
    assert hasattr(forgotten_tracks, "find_forgotten_tracks")
    assert forgotten_tracks.DEFAULT_N == 25
    assert forgotten_tracks.DEFAULT_MIN_PLAYS == 20
    assert forgotten_tracks.DEFAULT_DORMANCY_DAYS == 365
