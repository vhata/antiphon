"""Now-playing chaser: pull the latest scrobble, suggest sonically
compatible follow-ups.

Usage:
    uv run python -m scripts.chase [N]
    make chase [N=5]

Calls `user.getRecentTracks` for the latest scrobble, then
`track.getSimilar` for tracks that segue from it. Falls back to
`artist.getSimilar` if track-level similarity returns nothing.
Filters against the cool-down log (`make cooldown`).
"""

from __future__ import annotations

import sys
import urllib.parse

from scripts._lastfm import call
from scripts.cooldown import recent_recs
from scripts.profile import get_username

DEFAULT_N = 5
SPOTIFY_SEARCH = "https://open.spotify.com/search/"


def latest_track(user: str) -> tuple[str, str] | None:
    response = call("user.getRecentTracks", user=user, limit=1)
    tracks = response["recenttracks"]["track"]
    if not tracks:
        return None
    track = tracks[0]
    artist = track.get("artist", {}).get("#text", "")
    name = track.get("name", "")
    if not artist or not name:
        return None
    return (artist, name)


def similar_tracks(artist: str, track: str, limit: int = 20) -> list[tuple[str, str, float]]:
    response = call("track.getSimilar", artist=artist, track=track, limit=limit)
    similar = response.get("similartracks", {}).get("track", [])
    result: list[tuple[str, str, float]] = []
    for entry in similar:
        a = entry.get("artist", {}).get("name", "")
        n = entry.get("name", "")
        match = float(entry.get("match", 0))
        if a and n:
            result.append((a, n, match))
    return result


def similar_artists(artist: str, limit: int = 10) -> list[tuple[str, float]]:
    response = call("artist.getSimilar", artist=artist, limit=limit)
    similar = response.get("similarartists", {}).get("artist", [])
    return [(entry["name"], float(entry.get("match", 0))) for entry in similar if entry.get("name")]


def spotify_url(artist: str, track: str = "") -> str:
    query = f"{artist} {track}".strip()
    return SPOTIFY_SEARCH + urllib.parse.quote(query)


def _cool_down_keys() -> set[str]:
    """Lowercased pick strings from the cool-down log, for membership checks."""
    return {pick.lower() for _, pick, _ in recent_recs()}


def main(n: int = DEFAULT_N) -> int:
    user = get_username()
    latest = latest_track(user)
    if not latest:
        print("no recent scrobbles found", file=sys.stderr)
        return 1

    artist, track = latest
    print(f"=== chasing: {artist} — {track} ===")
    print()

    cooled = _cool_down_keys()

    track_picks = [
        (a, t, m) for a, t, m in similar_tracks(artist, track) if f"{a} — {t}".lower() not in cooled
    ]

    if track_picks:
        print("Sonically compatible tracks:")
        for a, t, match in track_picks[:n]:
            print(f"- [{a} — {t}]({spotify_url(a, t)})  ({match * 100:.0f}% match)")
        return 0

    artist_picks = [(a, m) for a, m in similar_artists(artist) if a.lower() not in cooled]
    if not artist_picks:
        print("no similar tracks or artists available")
        return 1

    print(f"No close-track matches; showing similar artists to {artist}:")
    for a, match in artist_picks[:n]:
        print(f"- [{a}]({spotify_url(a)})  ({match * 100:.0f}% match)")
    return 0


if __name__ == "__main__":
    arg_n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else DEFAULT_N
    sys.exit(main(arg_n))
