"""Forgotten-gem retrieval.

Finds dormant artists in the listener's overall top 100-500 who do
not appear in their 12-month top 200 — once well-loved but not played
in the last year. Output is suitable for input into the recommendation
flow in CLAUDE.md § Forgotten-gem mode. Pure retrieval, not discovery.

Usage:
    set -a; source .env; set +a
    uv run python -m scripts.forgotten_gems [N]

N is the number of top-by-plays dormant artists to surface. Default 15.
"""

from __future__ import annotations

import sys

from scripts._lastfm import call
from scripts.profile import get_username

DEFAULT_N = 15


def find_dormant(user: str) -> list[tuple[int, int, str]]:
    """Return (rank, playcount, name) tuples for dormant artists.

    Dormant = ranked 100-500 in overall plays AND not in the 12-month
    top 200.
    """
    overall = call("user.getTopArtists", user=user, period="overall", limit=500)
    recent = call("user.getTopArtists", user=user, period="12month", limit=200)
    recent_names = {a["name"].lower() for a in recent["topartists"]["artist"]}

    dormant: list[tuple[int, int, str]] = []
    for artist in overall["topartists"]["artist"]:
        rank = int(artist["@attr"]["rank"])
        if 100 <= rank <= 500 and artist["name"].lower() not in recent_names:
            dormant.append((rank, int(artist["playcount"]), artist["name"]))
    return dormant


def main(n: int = DEFAULT_N) -> None:
    user = get_username()
    dormant = find_dormant(user)
    print(f"{len(dormant)} dormant artists in rank-100-500 band.")
    print(f"Top {n} by overall plays:")
    print()
    for rank, plays, name in sorted(dormant, key=lambda row: -row[1])[:n]:
        print(f"  rank {rank:>3} | {plays:>5} plays | {name}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    main(n)
