"""Rut detector: flag when 1–2 artists dominate the listener's recent plays.

Usage:
    uv run python -m scripts.rut [DAYS]
    make rut [DAYS=14]

Reads recent scrobbles in the last DAYS days, computes top-artist
concentration, and emits a 'lean in / lean out' suggestion when the
top-1 share exceeds 40% or top-2 share exceeds 60%. Useful at
session start.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from typing import Any

from scripts._lastfm import call
from scripts.profile import get_username

DEFAULT_DAYS = 14
TOP_1_THRESHOLD = 0.40
TOP_2_THRESHOLD = 0.60
MIN_SCROBBLES = 30


def detect_rut(user: str, days: int = DEFAULT_DAYS) -> dict[str, Any]:
    cutoff = datetime.now(UTC) - timedelta(days=days)
    cutoff_ts = int(cutoff.timestamp())

    response = call(
        "user.getRecentTracks",
        user=user,
        limit=200,
        **{"from": cutoff_ts},
    )
    tracks = response["recenttracks"]["track"]

    counts: dict[str, int] = {}
    for track in tracks:
        artist = track.get("artist", {}).get("#text", "")
        if not artist:
            continue
        counts[artist] = counts.get(artist, 0) + 1

    total = sum(counts.values())
    sorted_artists = sorted(counts.items(), key=lambda kv: -kv[1])

    top1_share = sorted_artists[0][1] / total if sorted_artists and total else 0.0
    top2_share = (
        sum(c for _, c in sorted_artists[:2]) / total if len(sorted_artists) >= 2 and total else 0.0
    )

    in_rut = False
    reasons: list[str] = []
    if total < MIN_SCROBBLES:
        reasons.append(f"sample too small ({total} scrobbles in {days} days)")
    else:
        if top1_share >= TOP_1_THRESHOLD:
            in_rut = True
            reasons.append(f"{sorted_artists[0][0]} is {top1_share * 100:.0f}% of recent plays")
        if len(sorted_artists) >= 2 and top2_share >= TOP_2_THRESHOLD:
            in_rut = True
            top2_names = " + ".join(a for a, _ in sorted_artists[:2])
            reasons.append(f"top 2 ({top2_names}) are {top2_share * 100:.0f}% of recent plays")

    return {
        "in_rut": in_rut,
        "total_scrobbles": total,
        "top_artists": sorted_artists[:5],
        "reason": "; ".join(reasons) if reasons else "no rut detected",
    }


def main(days: int = DEFAULT_DAYS) -> int:
    user = get_username()
    result = detect_rut(user, days)

    print(f"=== rut check for {user} (last {days} days) ===")
    print()

    if result["total_scrobbles"] == 0:
        print("No scrobbles in this window.")
        return 0

    print(f"Recent listening ({result['total_scrobbles']} scrobbles):")
    for artist, count in result["top_artists"]:
        share = count / result["total_scrobbles"] * 100
        print(f"  {count:>4}  {share:>4.0f}%  {artist}")
    print()

    if result["in_rut"]:
        print(f"⚠  Rut detected: {result['reason']}")
        print()
        top_artist = result["top_artists"][0][0]
        print("Options:")
        print(f"  - Lean in:  make depth ARTIST='{top_artist}'")
        print("  - Lean out: make gems")
    else:
        print(f"✓ No rut: {result['reason']}")
    return 0


if __name__ == "__main__":
    arg_days = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else DEFAULT_DAYS
    sys.exit(main(arg_days))
