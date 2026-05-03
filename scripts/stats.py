"""Library-coverage diagnostic — top-N concentration, long-tail size.

Usage:
    uv run python -m scripts.stats
    make stats
"""

from __future__ import annotations

from scripts._lastfm import call
from scripts.profile import get_username

SAMPLE_LIMIT = 1000


def pct(numerator: int, denominator: int) -> float:
    return 100.0 * numerator / denominator if denominator else 0.0


def main() -> None:
    user = get_username()

    info = call("user.getInfo", user=user)["user"]
    total_playcount = int(info.get("playcount", 0))

    response = call("user.getTopArtists", user=user, period="overall", limit=SAMPLE_LIMIT)
    artists = response["topartists"]["artist"]
    plays = [int(a["playcount"]) for a in artists]
    sum_sample = sum(plays)

    def pct_of_total(n: int) -> float:
        return pct(sum(plays[:n]), total_playcount)

    print(f"=== {user} — library stats ===")
    print()
    print(f"Total scrobbles:                  {total_playcount:>10,}")
    print(f"Unique artists (top {SAMPLE_LIMIT} sample): {len(artists):>10,}")
    print(f"Sample covers:                    {pct(sum_sample, total_playcount):>9.1f}% of plays")
    print()
    print("Concentration (% of all plays):")
    for cutoff in (5, 25, 100, 500, 1000):
        if cutoff > len(artists):
            break
        print(f"  Top {cutoff:>4} artists: {pct_of_total(cutoff):>5.1f}%")
    print()
    print(
        f"Long-tail check: anything below rank {len(artists)} accounts for "
        f"{pct(total_playcount - sum_sample, total_playcount):.1f}% of plays."
    )


if __name__ == "__main__":
    main()
