"""On-demand SQLite cache of last.fm scrobble events.

A deliberate graduation toward the "becomes software" line documented in
`WISHLIST.md` § 4. Caches only raw scrobble events; aggregations and
metadata endpoints stay live.

Schema
------
- `scrobbles(uts INTEGER PRIMARY KEY, artist TEXT NOT NULL,
            album TEXT, track TEXT NOT NULL)`
- `metadata(key TEXT PRIMARY KEY, value INTEGER NOT NULL)`

`metadata` holds per-user watermarks. For user `<user>`, the keys are:

- `oldest_uts_cached:<user>` — the earliest timestamp the cache claims to
  cover for that user
- `newest_uts_cached:<user>` — the latest timestamp the cache claims to
  cover for that user

The watermarks track the *requested* range, not the timestamps of any
actual scrobble that came back. A quiet day with zero plays must still
count as "cached" so the next call does not refetch.

Public surface
--------------
`get_scrobbles(user, from_uts, to_uts)` is the only call most code needs.
It returns a list of dicts shaped like a single `user.getRecentTracks`
track entry, sorted by `date.uts` descending — drop-in compatible with
the existing scripts.

Pure helpers (`compute_gaps`, `new_watermarks`, `parse_tracks`) are split
out so they can be tested without touching the DB or the network.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

from scripts._lastfm import call

DB_PATH = Path(__file__).resolve().parent.parent / "antiphon.db"

# The API caps `limit` at 200 per page for `user.getRecentTracks`. Keep
# this wide so a single page covers most realistic gaps.
PAGE_LIMIT = 200

# A row as it lives in the `scrobbles` table.
ScrobbleRow = tuple[int, str, str | None, str]


# ---------------------------------------------------------------------------
# Pure helpers — no DB, no network.
# ---------------------------------------------------------------------------


def compute_gaps(
    from_uts: int,
    to_uts: int,
    oldest_cached: int | None,
    newest_cached: int | None,
) -> list[tuple[int, int]]:
    """Return the sub-ranges of `[from_uts, to_uts]` not yet covered by cache.

    The cache is assumed to be a single contiguous interval (we never
    split it). Gaps are therefore at most two: one extension to the
    left of `oldest_cached` and one to the right of `newest_cached`.
    """
    if oldest_cached is None or newest_cached is None:
        return [(from_uts, to_uts)]
    gaps: list[tuple[int, int]] = []
    if from_uts < oldest_cached:
        gaps.append((from_uts, oldest_cached - 1))
    if to_uts > newest_cached:
        gaps.append((newest_cached + 1, to_uts))
    return gaps


def new_watermarks(
    requested_from: int,
    requested_to: int,
    current_oldest: int | None,
    current_newest: int | None,
) -> tuple[int, int]:
    """Return the watermarks after merging a successful fetch.

    Always widens — once a range is cached, it stays cached.
    """
    if current_oldest is None or current_newest is None:
        return (requested_from, requested_to)
    return (min(current_oldest, requested_from), max(current_newest, requested_to))


def parse_tracks(response: dict[str, Any]) -> list[ScrobbleRow]:
    """Extract scrobble rows from a `user.getRecentTracks` response.

    Skips the now-playing entry (no `date` field), normalises a missing
    or empty album to `None`, and handles the single-track-as-dict shape
    the API uses when only one result matches.
    """
    recent = response.get("recenttracks", {})
    raw = recent.get("track", [])
    if isinstance(raw, dict):
        raw = [raw]
    rows: list[ScrobbleRow] = []
    for track in raw:
        date = track.get("date")
        if not date:
            # Now-playing entries have no `date`; skip them.
            continue
        try:
            uts = int(date["uts"])
        except (KeyError, ValueError, TypeError):
            continue
        artist = (track.get("artist") or {}).get("#text") or ""
        name = track.get("name") or ""
        if not artist or not name:
            continue
        album_raw = (track.get("album") or {}).get("#text") or ""
        album: str | None = album_raw if album_raw else None
        rows.append((uts, artist, album, name))
    return rows


def total_pages(response: dict[str, Any]) -> int:
    """Read the `@attr.totalPages` field from a paginated response.

    Defaults to 1 if absent or malformed.
    """
    attr = response.get("recenttracks", {}).get("@attr", {})
    try:
        return max(1, int(attr.get("totalPages", 1)))
    except (TypeError, ValueError):
        return 1


# ---------------------------------------------------------------------------
# Schema + DB access.
# ---------------------------------------------------------------------------


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS scrobbles (
    uts    INTEGER PRIMARY KEY,
    artist TEXT NOT NULL,
    album  TEXT,
    track  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_scrobbles_artist ON scrobbles(artist);

CREATE TABLE IF NOT EXISTS metadata (
    key   TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);
"""


def open_db(path: Path) -> sqlite3.Connection:
    """Open (creating if needed) the cache database at `path`.

    Enables foreign keys for future-proofing and applies the schema
    idempotently.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def get_watermarks(conn: sqlite3.Connection, user: str) -> tuple[int | None, int | None]:
    """Return `(oldest, newest)` for a user, or `(None, None)` if unset."""
    oldest_key = f"oldest_uts_cached:{user}"
    newest_key = f"newest_uts_cached:{user}"
    cur = conn.execute(
        "SELECT key, value FROM metadata WHERE key IN (?, ?)",
        (oldest_key, newest_key),
    )
    values: dict[str, int] = {row[0]: int(row[1]) for row in cur}
    return (values.get(oldest_key), values.get(newest_key))


def set_watermarks(conn: sqlite3.Connection, user: str, oldest: int, newest: int) -> None:
    """Upsert both watermarks for `user`."""
    conn.executemany(
        "INSERT INTO metadata(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        [
            (f"oldest_uts_cached:{user}", oldest),
            (f"newest_uts_cached:{user}", newest),
        ],
    )
    conn.commit()


def insert_rows(conn: sqlite3.Connection, rows: list[ScrobbleRow]) -> int:
    """Insert scrobble rows, ignoring rows whose `uts` already exists.

    Returns the number of rows actually inserted.
    """
    if not rows:
        return 0
    before_cur = conn.execute("SELECT COUNT(*) FROM scrobbles")
    before = int(before_cur.fetchone()[0])
    conn.executemany(
        "INSERT OR IGNORE INTO scrobbles (uts, artist, album, track) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    after_cur = conn.execute("SELECT COUNT(*) FROM scrobbles")
    after = int(after_cur.fetchone()[0])
    return after - before


def query_range(conn: sqlite3.Connection, from_uts: int, to_uts: int) -> list[dict[str, Any]]:
    """Return cached scrobbles in `[from_uts, to_uts]` newest-first.

    The dict shape matches a single `user.getRecentTracks` track entry,
    so callers can swap this in for an API response without changing
    their downstream code.
    """
    cur = conn.execute(
        "SELECT uts, artist, album, track FROM scrobbles "
        "WHERE uts BETWEEN ? AND ? ORDER BY uts DESC",
        (from_uts, to_uts),
    )
    result: list[dict[str, Any]] = []
    for uts, artist, album, track in cur:
        result.append(
            {
                "artist": {"#text": artist},
                "name": track,
                "album": {"#text": album or ""},
                "date": {"uts": str(uts)},
            }
        )
    return result


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def _fetch_gap(user: str, from_uts: int, to_uts: int) -> list[ScrobbleRow]:
    """Fetch every scrobble in `[from_uts, to_uts]` via paginated API calls."""
    all_rows: list[ScrobbleRow] = []
    page = 1
    while True:
        response = call(
            "user.getRecentTracks",
            user=user,
            limit=PAGE_LIMIT,
            page=page,
            **{"from": from_uts, "to": to_uts},
        )
        all_rows.extend(parse_tracks(response))
        pages = total_pages(response)
        if page >= pages:
            break
        page += 1
    return all_rows


def now_uts() -> int:
    """Current UNIX timestamp, seconds since epoch."""
    return int(time.time())


def is_cold(user: str, db_path: Path | None = None) -> bool:
    """True if no watermarks exist yet for `user` (cache will need to backfill)."""
    conn = open_db(db_path or DB_PATH)
    try:
        oldest, newest = get_watermarks(conn, user)
        return oldest is None or newest is None
    finally:
        conn.close()


def scrobble_count(db_path: Path | None = None) -> int:
    """Total rows in the local `scrobbles` table.

    Per-user counting is not exposed because the table is per-DB (one
    `antiphon.db` per listener), so the row total is the listener's
    cached-scrobble total.
    """
    conn = open_db(db_path or DB_PATH)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM scrobbles")
        row = cursor.fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def get_scrobbles(user: str, from_uts: int, to_uts: int) -> list[dict[str, Any]]:
    """Return scrobbles in `[from_uts, to_uts]` for `user`, extending the cache.

    The returned dicts mirror a single track entry from
    `user.getRecentTracks` (same field names, same nested shape) so a
    caller can pass each one through code that already handles the
    live API response.

    Side effect: any uncovered sub-range of `[from_uts, to_uts]` is
    fetched and inserted, and the per-user watermarks are widened so
    a subsequent call covering the same range hits the cache only.
    """
    if not user:
        raise ValueError("user must be a non-empty string")
    if from_uts > to_uts:
        raise ValueError(f"from_uts ({from_uts}) must be <= to_uts ({to_uts})")

    conn = open_db(DB_PATH)
    try:
        oldest, newest = get_watermarks(conn, user)
        gaps = compute_gaps(from_uts, to_uts, oldest, newest)
        for gap_from, gap_to in gaps:
            rows = _fetch_gap(user, gap_from, gap_to)
            insert_rows(conn, rows)
        if gaps:
            new_oldest, new_newest = new_watermarks(from_uts, to_uts, oldest, newest)
            set_watermarks(conn, user, new_oldest, new_newest)
        return query_range(conn, from_uts, to_uts)
    finally:
        conn.close()
