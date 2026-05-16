"""Daily one-track horoscope. A single pick per day, persisted.

Usage:
    uv run python -m scripts.daily
    make daily

Strategy rotates by day-of-year so the daily ritual stays varied:

    comfort    — random track by an artist in your overall top 50
    forgotten  — random track by an artist in your overall top 100-500
                 who has not appeared in your last 12 months
    gap        — random track by an artist similar to your #1 that you
                 do not yet have in your library
    loved      — random track from your loved-tracks set
    tag-walk   — random track by an artist from a random tag in your
                 user.getTopTags

Picks are persisted to `daily.log.md` (gitignored). Re-running the
same day returns the same pick.
"""

from __future__ import annotations

import random
import sys
import urllib.parse
from datetime import date
from pathlib import Path

from scripts import _spotify
from scripts._lastfm import call
from scripts.profile import get_username

DAILY_LOG = Path(__file__).resolve().parent.parent / "daily.log.md"
SPOTIFY_SEARCH = "https://open.spotify.com/search/"

STRATEGIES = ["comfort", "forgotten", "gap", "loved", "tag-walk"]
HEADER = """\
# Daily picks

One track per day, varied across strategies. Format per entry:
`- YYYY-MM-DD | <artist> — <track> | <strategy>`.

## Entries

"""


def strategy_for_date(today: date) -> str:
    """Stable strategy rotation by day-of-year."""
    return STRATEGIES[today.toordinal() % len(STRATEGIES)]


def existing_pick(today_str: str, path: Path | None = None) -> str | None:
    """Return today's logged entry (without the leading `- `), or None."""
    if path is None:
        path = DAILY_LOG
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        if line.startswith(f"- {today_str} |"):
            return line[2:].strip()
    return None


def append_pick(
    today_str: str,
    artist: str,
    track: str,
    strategy: str,
    path: Path | None = None,
) -> None:
    if path is None:
        path = DAILY_LOG
    if not path.exists():
        path.write_text(HEADER)
    text = path.read_text()
    if not text.endswith("\n"):
        text += "\n"
    line = f"- {today_str} | {artist} — {track} | {strategy}"
    if line not in text:
        path.write_text(text + line + "\n")


def _random_track_by(artist: str) -> tuple[str, str]:
    """Pick a random top-track for an artist (from artist.getTopTracks)."""
    response = call("artist.getTopTracks", artist=artist, limit=20)
    tracks = response.get("toptracks", {}).get("track", [])
    if not tracks:
        return (artist, "")
    track = random.choice(tracks)
    return (artist, track.get("name", ""))


def pick_comfort(user: str) -> tuple[str, str]:
    response = call("user.getTopArtists", user=user, period="overall", limit=50)
    artists = response["topartists"]["artist"]
    if not artists:
        return ("", "")
    return _random_track_by(random.choice(artists)["name"])


def pick_forgotten(user: str) -> tuple[str, str]:
    overall = call("user.getTopArtists", user=user, period="overall", limit=500)["topartists"][
        "artist"
    ]
    recent = call("user.getTopArtists", user=user, period="12month", limit=200)["topartists"][
        "artist"
    ]
    recent_names = {a["name"].lower() for a in recent}
    dormant = [
        a
        for a in overall
        if 100 <= int(a["@attr"]["rank"]) <= 500 and a["name"].lower() not in recent_names
    ]
    if not dormant:
        return pick_comfort(user)
    return _random_track_by(random.choice(dormant)["name"])


def pick_loved(user: str) -> tuple[str, str]:
    response = call("user.getLovedTracks", user=user, limit=200)
    tracks = response.get("lovedtracks", {}).get("track", [])
    if not tracks:
        return pick_comfort(user)
    track = random.choice(tracks)
    return (track["artist"]["name"], track.get("name", ""))


def pick_gap(user: str) -> tuple[str, str]:
    overall = call("user.getTopArtists", user=user, period="overall", limit=500)["topartists"][
        "artist"
    ]
    if not overall:
        return ("", "")
    library_names = {a["name"].lower() for a in overall}
    top1 = overall[0]["name"]
    similar = (
        call("artist.getSimilar", artist=top1, limit=30).get("similarartists", {}).get("artist", [])
    )
    gaps = [s["name"] for s in similar if s["name"].lower() not in library_names]
    if not gaps:
        return pick_comfort(user)
    return _random_track_by(random.choice(gaps))


def pick_tag_walk(user: str) -> tuple[str, str]:
    tags_response = call("user.getTopTags", user=user, limit=20)
    tags = tags_response.get("toptags", {}).get("tag", [])
    if not tags:
        return pick_comfort(user)
    tag = random.choice(tags)["name"]
    artists = call("tag.getTopArtists", tag=tag, limit=30).get("topartists", {}).get("artist", [])
    if not artists:
        return pick_comfort(user)
    return _random_track_by(random.choice(artists)["name"])


PICKERS = {
    "comfort": pick_comfort,
    "forgotten": pick_forgotten,
    "loved": pick_loved,
    "gap": pick_gap,
    "tag-walk": pick_tag_walk,
}


def spotify_url(artist: str, track: str) -> str:
    """Resolve to a direct Spotify track URL if credentials let us; fall back to a search URL.

    The function signature is stable. Callers do not care whether the
    URL is a direct `/track/<id>` or a `/search/<query>` — both open
    the right thing in the Spotify client.
    """
    if _spotify.is_available():
        direct = _spotify.search_track(artist, track)
        if direct:
            return direct
    query = f"{artist} {track}".strip()
    return SPOTIFY_SEARCH + urllib.parse.quote(query)


def _print_pick(today_str: str, artist: str, track: str, strategy: str) -> None:
    print(f"=== today's pick ({today_str}) ===")
    print()
    print(f"  [{artist} — {track}]({spotify_url(artist, track)})")
    print()
    print(f"Strategy: {strategy}")


def main() -> int:
    user = get_username()
    today = date.today()
    today_str = today.isoformat()

    existing = existing_pick(today_str)
    if existing:
        parts = [p.strip() for p in existing.split("|")]
        if len(parts) >= 3:
            pick_text = parts[1]
            strategy_text = parts[2]
            artist, _, track = pick_text.partition(" — ")
            _print_pick(today_str, artist, track, strategy_text)
            return 0

    strategy = strategy_for_date(today)
    artist, track = PICKERS[strategy](user)
    if not track:
        print(f"could not pick for strategy '{strategy}' (no data)", file=sys.stderr)
        return 1

    append_pick(today_str, artist, track, strategy)
    _print_pick(today_str, artist, track, strategy)
    return 0


if __name__ == "__main__":
    sys.exit(main())
