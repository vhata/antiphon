"""Period-in-music report.

Usage:
    uv run python -m scripts.review [PERIOD]
    make review PERIOD=month

PERIOD ∈ {week, month, quarter, year}; default month.

Snapshots the listener's top artists in the chosen period and
categorises each against their overall taste:

- *newcomers* — in this period's top but not in the overall top 100;
  fresh appreciation
- *comfort returners* — also in the overall top 25; the deep familiar
- *mid-tier* — somewhere in the overall top 26-100; warm but not core

Plus a one-line volume note.
"""

from __future__ import annotations

import sys
from typing import Any

from scripts._lastfm import call
from scripts.profile import get_username

PERIOD_MAP = {
    "week": "7day",
    "month": "1month",
    "quarter": "3month",
    "year": "12month",
}
DEFAULT_PERIOD = "month"
TOP_N = 15
OVERALL_LIMIT = 100
OVERALL_CORE = 25


def review(user: str, period: str = DEFAULT_PERIOD) -> dict[str, Any]:
    if period not in PERIOD_MAP:
        raise ValueError(f"unknown period: {period}; use one of {list(PERIOD_MAP)}")

    api_period = PERIOD_MAP[period]
    current = call("user.getTopArtists", user=user, period=api_period, limit=TOP_N)["topartists"][
        "artist"
    ]
    overall = call("user.getTopArtists", user=user, period="overall", limit=OVERALL_LIMIT)[
        "topartists"
    ]["artist"]

    overall_names = {a["name"].lower() for a in overall}
    overall_core = {a["name"].lower() for a in overall[:OVERALL_CORE]}

    newcomers: list[dict[str, Any]] = []
    returners: list[dict[str, Any]] = []
    mid_tier: list[dict[str, Any]] = []

    for artist in current:
        name_lc = artist["name"].lower()
        if name_lc not in overall_names:
            newcomers.append(artist)
        elif name_lc in overall_core:
            returners.append(artist)
        else:
            mid_tier.append(artist)

    period_volume = sum(int(a["playcount"]) for a in current)

    return {
        "period": period,
        "api_period": api_period,
        "current": current,
        "newcomers": newcomers,
        "returners": returners,
        "mid_tier": mid_tier,
        "period_volume": period_volume,
    }


def main(period: str = DEFAULT_PERIOD) -> int:
    user = get_username()
    try:
        result = review(user, period)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 64

    print(f"=== {user} — {result['period']} review ({result['api_period']}) ===")
    print()
    print(f"Top {len(result['current'])} artists, {result['period_volume']} plays in window:")
    for artist in result["current"]:
        print(f"  {int(artist['playcount']):>4}  {artist['name']}")
    print()

    def _emit(label: str, group: list[dict[str, Any]]) -> None:
        if not group:
            return
        print(f"{label}:")
        for a in group:
            print(f"  - {a['name']} ({int(a['playcount'])} plays)")
        print()

    _emit(f"Newcomers (not in your overall top {OVERALL_LIMIT})", result["newcomers"])
    _emit(f"Comfort returners (also in your overall top {OVERALL_CORE})", result["returners"])
    _emit(
        f"Mid-tier (overall rank {OVERALL_CORE + 1}-{OVERALL_LIMIT})",
        result["mid_tier"],
    )
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else DEFAULT_PERIOD
    sys.exit(main(arg))
