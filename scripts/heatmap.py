"""Listening heat-map: day-of-week × hour-of-day density.

Usage:
    uv run python -m scripts.heatmap [DAYS]
    make heatmap [DAYS=90]

Pulls the listener's recent scrobbles in the chosen window (default
90 days), buckets them into a 7×24 grid by day-of-week and hour-of-day
in *local* time, and renders the result as block characters scaled to
the peak cell.

The local-time choice matters: scrobbles are stored in UTC, but
"when do I listen" is only meaningful in the listener's timezone.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta, tzinfo
from typing import Any

from scripts._lastfm import call
from scripts.profile import get_username

DEFAULT_DAYS = 90
PAGE_LIMIT = 200
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
    """Paginate user.getRecentTracks back `days` days."""
    cutoff_ts = int((datetime.now(UTC) - timedelta(days=days)).timestamp())
    tracks: list[dict[str, Any]] = []
    page = 1
    while True:
        response = call(
            "user.getRecentTracks",
            user=user,
            limit=PAGE_LIMIT,
            page=page,
            **{"from": cutoff_ts},
        )
        page_tracks = response.get("recenttracks", {}).get("track", [])
        if isinstance(page_tracks, dict):
            page_tracks = [page_tracks]
        if not page_tracks:
            break
        tracks.extend(page_tracks)
        attrs = response.get("recenttracks", {}).get("@attr", {})
        total_pages = int(attrs.get("totalPages", 1))
        if page >= total_pages:
            break
        page += 1
    return tracks


def main(days: int = DEFAULT_DAYS) -> int:
    user = get_username()
    tracks = _fetch_window(user, days)
    grid = bucket_by_hour_dow(tracks)
    total = sum(sum(row) for row in grid)

    print(f"=== {user} — listening heat-map ===")
    print(f"({total:,} scrobbles over the last {days} days, local time)")
    print()
    print(render_grid(grid))
    return 0


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else DEFAULT_DAYS
    sys.exit(main(n))
