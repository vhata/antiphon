"""Last N days of scrobbles in compact form.

Usage:
    uv run python -m scripts.recent [N]
    make recent N=7

Default N is 7. Reads scrobbles through `scripts._cache` so repeat
runs over the same window do no API work.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

from scripts._cache import get_scrobbles, now_uts
from scripts.profile import get_username

DEFAULT_DAYS = 7


def main(days: int = DEFAULT_DAYS) -> None:
    user = get_username()
    cutoff_ts = int((datetime.now(UTC) - timedelta(days=days)).timestamp())

    print(f"=== {user} — last {days} days of scrobbles ===")
    print()

    tracks = get_scrobbles(user, cutoff_ts, now_uts())

    for track in tracks:
        artist = track.get("artist", {}).get("#text", "?")
        name = track.get("name", "?")
        print(f"  {artist} — {name}")

    counts: dict[str, int] = {}
    for track in tracks:
        artist = track.get("artist", {}).get("#text", "?")
        counts[artist] = counts.get(artist, 0) + 1

    print()
    print(f"Tally ({len(tracks)} scrobbles, {len(counts)} unique artists):")
    for artist, count in sorted(counts.items(), key=lambda kv: -kv[1])[:20]:
        print(f"  {count:>3}  {artist}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else DEFAULT_DAYS
    main(n)
