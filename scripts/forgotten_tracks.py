"""Forgotten-tracks retrieval.

Finds individual tracks the listener played heavily in the past but
hasn't touched recently. Reads the local SQLite scrobble cache —
requires a backfilled cache (`make timeline` is the easiest way to
seed it). Sibling to `forgotten_gems`, which works at the artist
level. Pure retrieval, not discovery.

Usage:
    uv run python -m scripts.forgotten_tracks [N] [MIN_PLAYS] [DORMANCY_DAYS]
    make gems TYPE=tracks [N=25] [MIN_PLAYS=20] [DORMANCY_DAYS=365]

Defaults: top 25 results, minimum 20 plays per track, dormant for at
least 365 days. The minimum-plays filter is what makes this "favourites
you forgot" rather than "anything you ever played once."
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

from scripts._cache import DB_PATH, is_cold, now_uts, open_db
from scripts.profile import get_username

DEFAULT_N = 25
DEFAULT_MIN_PLAYS = 20
DEFAULT_DORMANCY_DAYS = 365


def find_forgotten_tracks(
    *,
    min_plays: int = DEFAULT_MIN_PLAYS,
    dormancy_days: int = DEFAULT_DORMANCY_DAYS,
    limit: int = DEFAULT_N,
    db_path: Path | None = None,
    today_uts: int | None = None,
) -> list[tuple[str, str, int, int]]:
    """Return (artist, track, plays, last_played_uts) for dormant favourites.

    A row qualifies when total plays >= `min_plays` and the most
    recent play is older than `dormancy_days` days. Results are
    sorted by play count descending, capped at `limit`.
    """
    if today_uts is None:
        today_uts = now_uts()
    cutoff = today_uts - dormancy_days * 86400
    conn = open_db(db_path or DB_PATH)
    try:
        cursor = conn.execute(
            """
            SELECT artist, track, COUNT(*) AS plays, MAX(uts) AS last_played
            FROM scrobbles
            GROUP BY artist, track
            HAVING plays >= ? AND last_played < ?
            ORDER BY plays DESC, last_played ASC
            LIMIT ?
            """,
            (min_plays, cutoff, limit),
        )
        return [(str(row[0]), str(row[1]), int(row[2]), int(row[3])) for row in cursor.fetchall()]
    finally:
        conn.close()


def _fmt_date(uts: int) -> str:
    return datetime.fromtimestamp(uts, tz=UTC).strftime("%Y-%m-%d")


def main(
    n: int = DEFAULT_N,
    min_plays: int = DEFAULT_MIN_PLAYS,
    dormancy_days: int = DEFAULT_DORMANCY_DAYS,
) -> int:
    user = get_username()

    if is_cold(user):
        print("The scrobble cache is cold for this user.")
        print("Run `make timeline` first to backfill — that populates the cache")
        print("with your full history. Subsequent forgotten-tracks runs are instant.")
        return 1

    try:
        rows = find_forgotten_tracks(
            min_plays=min_plays,
            dormancy_days=dormancy_days,
            limit=n,
        )
    except sqlite3.OperationalError as exc:
        print(f"cache error: {exc}", file=sys.stderr)
        return 1

    print(f"=== {user} — forgotten tracks ===")
    print(f"(≥{min_plays} plays, last touched >{dormancy_days} days ago; top {n} by play count)")
    print()

    if not rows:
        print("No tracks matched. Try lowering MIN_PLAYS or DORMANCY_DAYS.")
        return 0

    for artist, track, plays, last_played in rows:
        print(f"  {plays:>4} plays | last {_fmt_date(last_played)} | {artist} — {track}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a]
    n_arg = int(args[0]) if len(args) > 0 else DEFAULT_N
    min_plays_arg = int(args[1]) if len(args) > 1 else DEFAULT_MIN_PLAYS
    dormancy_arg = int(args[2]) if len(args) > 2 else DEFAULT_DORMANCY_DAYS
    sys.exit(main(n_arg, min_plays_arg, dormancy_arg))
