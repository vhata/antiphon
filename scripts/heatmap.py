"""Listening heat-map: day-of-week × hour-of-day density.

Usage:
    uv run python -m scripts.heatmap [DAYS] [--include-sleep]
    make heatmap [DAYS=90]

Pulls the listener's recent scrobbles in the chosen window (default
90 days) via the on-demand SQLite scrobble cache (`scripts/_cache.py`),
buckets them into a 7×24 grid by day-of-week and hour-of-day in *local*
time, and renders the result as block characters scaled to the peak
cell.

The local-time choice matters: scrobbles are stored in UTC, but
"when do I listen" is only meaningful in the listener's timezone.

Repeat runs hit the cache: the first invocation populates it from the
live API; subsequent runs over the same window do no network work. A
widened window fetches only the gap.

If `sleep_albums.md` exists at the repo root, scrobbles matching any
of its (artist, album) entries are filtered out before bucketing so
that overnight-tail records do not skew the early-morning cells.
Pass `--include-sleep` to disable the filter and see the raw view.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta, tzinfo
from typing import Any

from scripts import _cache, _sleep
from scripts.profile import get_username

DEFAULT_DAYS = 90
BLOCKS = " ▁▂▃▄▅▆▇█"  # leading space = empty cell; eight density steps after
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def bucket_by_hour_dow(
    tracks: list[dict[str, Any]],
    tz: tzinfo | None = None,
) -> list[list[int]]:
    """Return a 7×24 grid: grid[day_of_week][hour] = scrobble count.

    `day_of_week` follows Python's convention: 0=Monday … 6=Sunday.
    Timestamps are interpreted in `tz` (default: system local time).
    Now-playing entries and tracks lacking a `date` field are skipped.
    """
    grid = [[0] * 24 for _ in range(7)]
    for track in tracks:
        attrs = track.get("@attr") or {}
        if attrs.get("nowplaying") == "true":
            continue
        date_field = track.get("date")
        if not date_field:
            continue
        ts = int(date_field["uts"])
        dt = datetime.fromtimestamp(ts, tz=tz)
        grid[dt.weekday()][dt.hour] += 1
    return grid


def filter_sleep_albums(
    tracks: list[dict[str, Any]],
    pairs: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    """Drop tracks whose (artist, album) matches any entry in `pairs`.

    Matching is case-insensitive. Tracks missing an album field are
    kept (a sleep-album entry without an album cannot match). If
    `pairs` is empty the input list is returned unchanged.
    """
    if not pairs:
        return tracks
    kept: list[dict[str, Any]] = []
    for track in tracks:
        artist = (track.get("artist") or {}).get("#text", "")
        album = (track.get("album") or {}).get("#text", "")
        if album and _sleep.matches(artist, album, pairs):
            continue
        kept.append(track)
    return kept


def render_grid(grid: list[list[int]]) -> str:
    """Render the 7×24 grid as a fixed-width text block."""
    peak = max((max(row) for row in grid), default=0)
    steps = len(BLOCKS) - 1

    def cell(value: int) -> str:
        if peak == 0:
            return BLOCKS[0]
        return BLOCKS[min(steps, round(value / peak * steps))]

    # Each cell is 3 chars wide: block + 2 spaces. Header marks every
    # 3rd hour with a left-aligned label (so "12" doesn't drift right
    # of the column it labels) and blanks elsewhere.
    header_cells = [f"{h:<2} " if h % 3 == 0 else "   " for h in range(24)]
    header = "     " + "".join(header_cells)

    lines = [header]
    for day_idx, row in enumerate(grid):
        cells = "".join(f"{cell(v)}  " for v in row)
        lines.append(f"{DAY_NAMES[day_idx]}  {cells}")
    return "\n".join(lines)


def _fetch_window(user: str, days: int) -> list[dict[str, Any]]:
    """Return scrobbles for the last `days` days, via the on-demand cache."""
    now = datetime.now(UTC)
    from_uts = int((now - timedelta(days=days)).timestamp())
    to_uts = int(now.timestamp())
    return _cache.get_scrobbles(user, from_uts, to_uts)


def main(days: int = DEFAULT_DAYS, include_sleep: bool = False) -> int:
    user = get_username()
    tracks = _fetch_window(user, days)
    raw_count = len(tracks)

    pairs = [] if include_sleep else _sleep.load()
    filtered_tracks = filter_sleep_albums(tracks, pairs)
    removed = raw_count - len(filtered_tracks)

    grid = bucket_by_hour_dow(filtered_tracks)
    total = sum(sum(row) for row in grid)

    print(f"=== {user} — listening heat-map ===")
    if pairs and removed > 0:
        print(
            f"({total:,} scrobbles over the last {days} days, local time; "
            f"{removed:,} sleep-album scrobbles filtered)"
        )
    else:
        print(f"({total:,} scrobbles over the last {days} days, local time)")
    print()
    print(render_grid(grid))
    return 0


def _parse_args(argv: list[str]) -> tuple[int, bool]:
    """Split argv into (days, include_sleep). Order-agnostic."""
    days = DEFAULT_DAYS
    include_sleep = False
    for arg in argv:
        if arg == "--include-sleep":
            include_sleep = True
        elif arg:
            days = int(arg)
    return days, include_sleep


if __name__ == "__main__":
    n, inc = _parse_args(sys.argv[1:])
    sys.exit(main(n, inc))
