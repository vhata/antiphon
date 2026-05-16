"""Year-by-year discovery timeline.

For each of the listener's overall top-N artists, finds the date of
the *first* scrobble and emits a year-by-year narrative — "in {year}
you discovered {artist}". Reads scrobble history through the SQLite
cache in `scripts._cache`, which makes deep-history queries cheap
after the first run.

The first run with a cold cache triggers a full-history backfill —
the one-time API cost; subsequent runs are instant.

Usage:
    uv run python -m scripts.timeline [N]
    make timeline

N is the top-N artist count to walk; default 50.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import Any

from scripts._cache import get_scrobbles, is_cold, now_uts, scrobble_count
from scripts._lastfm import call
from scripts.profile import get_username

DEFAULT_TOP_N = 50


def year_for_uts(uts: int) -> int:
    """Return the calendar year (UTC) of a UTS."""
    return datetime.fromtimestamp(uts, tz=UTC).year


def earliest_uts_by_artist(
    scrobbles: list[dict[str, Any]],
    artists: list[str],
) -> dict[str, int]:
    """For each artist in `artists`, find the earliest scrobble UTS.

    `scrobbles` entries are expected to mirror `user.getRecentTracks`
    track entries — `track["date"]["uts"]` and `track["artist"]["#text"]`.
    Matching is case-insensitive against the scrobble's artist field;
    the canonical name from `artists` is preserved in the returned keys.
    Artists with no matching scrobble are omitted.
    """
    if not artists or not scrobbles:
        return {}
    canonical: dict[str, str] = {name.lower(): name for name in artists}
    earliest: dict[str, int] = {}
    for track in scrobbles:
        artist_field = track.get("artist") or {}
        artist_raw = artist_field.get("#text", "") if isinstance(artist_field, dict) else ""
        key = canonical.get(artist_raw.lower())
        if key is None:
            continue
        date_field = track.get("date") or {}
        uts_raw = date_field.get("uts") if isinstance(date_field, dict) else None
        if uts_raw is None:
            continue
        uts = int(uts_raw)
        existing = earliest.get(key)
        if existing is None or uts < existing:
            earliest[key] = uts
    return earliest


def group_by_year(
    earliest: dict[str, int],
    ranks: dict[str, int],
) -> dict[int, list[str]]:
    """Bucket artists by year-of-first-scrobble.

    Years are returned in ascending order. Within each year, artists
    are sorted by `ranks` ascending (rank 1 = most-played overall);
    artists missing from `ranks` are slotted last with an alphabetic
    tie-break.
    """
    by_year: dict[int, list[str]] = {}
    for artist, uts in earliest.items():
        by_year.setdefault(year_for_uts(uts), []).append(artist)

    def _sort_key(name: str) -> tuple[int, str]:
        rank = ranks.get(name)
        return (rank if rank is not None else sys.maxsize, name.lower())

    for year in by_year:
        by_year[year].sort(key=_sort_key)
    return dict(sorted(by_year.items()))


def _top_artists(user: str, n: int) -> list[dict[str, Any]]:
    response = call("user.getTopArtists", user=user, period="overall", limit=n)
    artists = response.get("topartists", {}).get("artist", [])
    return list(artists)


def build_timeline(user: str, n: int = DEFAULT_TOP_N) -> dict[str, Any]:
    """Assemble the timeline dataset for `user`.

    Returns:
        top: raw top-artists payload
        ranks: {artist_name: rank}
        years: {year: [artist_name, ...]} ordered ascending
        scrobble_count: total scrobbles examined in this run
        range: (oldest_uts, newest_uts) of examined scrobbles, or None
    """
    top = _top_artists(user, n)
    names = [a["name"] for a in top]
    ranks: dict[str, int] = {}
    for entry in top:
        try:
            ranks[entry["name"]] = int(entry["@attr"]["rank"])
        except (KeyError, ValueError, TypeError):
            continue

    scrobbles = get_scrobbles(user, 0, now_uts())
    earliest = earliest_uts_by_artist(scrobbles, names)
    years = group_by_year(earliest, ranks)

    if scrobbles:
        utses = [int(t["date"]["uts"]) for t in scrobbles if t.get("date")]
        scrobble_range: tuple[int, int] | None = (min(utses), max(utses)) if utses else None
    else:
        scrobble_range = None

    return {
        "top": top,
        "ranks": ranks,
        "years": years,
        "scrobble_count": len(scrobbles),
        "range": scrobble_range,
    }


def _fmt_date(uts: int) -> str:
    return datetime.fromtimestamp(uts, tz=UTC).strftime("%Y-%m-%d")


def main(n: int = DEFAULT_TOP_N) -> int:
    user = get_username()
    cold = is_cold(user)

    print(f"=== {user} — discovery timeline (top {n}) ===")
    print()
    if cold:
        print("Cache is cold. The first run paginates your full last.fm history")
        print("via user.getRecentTracks. For a heavy listener this takes a few")
        print("minutes and several hundred API calls; subsequent runs are instant.")
        print()
    else:
        print(f"Cache: {scrobble_count()} scrobbles already on disk.")
        print()

    result = build_timeline(user, n)

    rng = result["range"]
    if rng is None:
        print("No scrobbles returned from the cache. Nothing to time-line.")
        return 0

    oldest, newest = rng
    print(
        f"Scanned {result['scrobble_count']} scrobbles ({_fmt_date(oldest)} → {_fmt_date(newest)})."
    )
    print()

    years = result["years"]
    if not years:
        print(f"None of your top-{n} artists matched any cached scrobble.")
        return 0

    for year, artists in years.items():
        print(f"{year}: {', '.join(artists)}")

    matched = sum(len(v) for v in years.values())
    missing = n - matched
    if missing > 0:
        print()
        print(
            f"({missing} of your top {n} artists had no first-scrobble match — "
            "likely renames or unicode mismatches.)"
        )
    return 0


if __name__ == "__main__":
    arg_n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else DEFAULT_TOP_N
    sys.exit(main(arg_n))
