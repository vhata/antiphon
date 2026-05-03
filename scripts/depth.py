"""Artist-depth helper: which of an artist's canonical albums has the
listener played the LEAST?

Usage:
    uv run python -m scripts.depth "<artist>"
    make depth ARTIST='Pink Floyd'

Pulls the artist's top albums (global popularity) and the listener's
own top-1000 albums, then prints the artist's albums with the
listener's playcount per album. The 'GAP' marker on a high-globally
album with zero user plays is the recommendation surface.
"""

from __future__ import annotations

import sys

from scripts._lastfm import call
from scripts.profile import get_username

DEFAULT_USER_DEPTH = 1000


def artist_top_albums(artist: str, limit: int = 20) -> list[tuple[str, int]]:
    """`[(album, global_playcount)]` for the artist's top N albums."""
    response = call("artist.getTopAlbums", artist=artist, limit=limit)
    albums = response.get("topalbums", {}).get("album", [])
    return [(a["name"], int(a.get("playcount", 0))) for a in albums]


def user_albums_for_artist(
    user: str, artist: str, depth: int = DEFAULT_USER_DEPTH
) -> dict[str, int]:
    """`{album: user_playcount}` for the artist's albums within user's top N."""
    response = call("user.getTopAlbums", user=user, period="overall", limit=depth)
    albums = response.get("topalbums", {}).get("album", [])
    result: dict[str, int] = {}
    for entry in albums:
        if entry.get("artist", {}).get("name", "").lower() == artist.lower():
            result[entry["name"]] = int(entry.get("playcount", 0))
    return result


def main(artist: str) -> int:
    user = get_username()
    print(f"=== {artist} depth check for {user} ===")
    print()

    canonical = artist_top_albums(artist)
    if not canonical:
        print(f"no top albums found for {artist}", file=sys.stderr)
        return 1

    user_plays = user_albums_for_artist(user, artist)

    print(f"{'rank':>4} | {'globally':>10} | {'your plays':>10} | album")
    print("-" * 70)
    for rank, (album, global_plays) in enumerate(canonical, start=1):
        matched = next(
            (v for k, v in user_plays.items() if k.lower() == album.lower()),
            0,
        )
        marker = "  GAP" if matched == 0 else ""
        print(f"{rank:>4} | {global_plays:>10,} | {matched:>10} | {album}{marker}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1]:
        print('usage: uv run python -m scripts.depth "<artist>"', file=sys.stderr)
        sys.exit(64)
    sys.exit(main(sys.argv[1]))
