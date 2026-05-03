"""artist.getSimilar wrapper with library-overlap pre-computed.

Usage:
    uv run python -m scripts.similar "<artist>" [N]
    make similar ARTIST='Massive Attack' N=20

Highlights gaps — artists similar to <artist> that the user has not
scrobbled (or has scrobbled lightly).
"""

from __future__ import annotations

import sys
from typing import Any

from scripts._lastfm import call
from scripts.profile import get_username

DEFAULT_N = 20
LIBRARY_DEPTH = 500


def build_library_index(top_artists: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """Map lowercased artist name → (rank, playcount) from a top-artists response."""
    return {a["name"].lower(): (int(a["@attr"]["rank"]), int(a["playcount"])) for a in top_artists}


def annotate(
    similar: list[dict[str, Any]], library: dict[str, tuple[int, int]]
) -> list[tuple[str, float, tuple[int, int] | None]]:
    """Return [(name, match_pct, (rank, plays) or None)] for each similar artist."""
    result: list[tuple[str, float, tuple[int, int] | None]] = []
    for entry in similar:
        name = entry["name"]
        match_pct = float(entry.get("match", 0)) * 100
        in_library = library.get(name.lower())
        result.append((name, match_pct, in_library))
    return result


def main(artist: str, n: int = DEFAULT_N) -> None:
    user = get_username()

    similar_response = call("artist.getSimilar", artist=artist, limit=n)
    similar_artists = similar_response.get("similarartists", {}).get("artist", [])

    if not similar_artists:
        print(f"no similar artists found for '{artist}'")
        return

    overall = call("user.getTopArtists", user=user, period="overall", limit=LIBRARY_DEPTH)
    library = build_library_index(overall["topartists"]["artist"])

    print(f"=== Artists similar to {artist} (top {n}) ===")
    print()

    for name, match_pct, in_library in annotate(similar_artists, library):
        if in_library is None:
            tag = "GAP"
        else:
            rank, plays = in_library
            tag = f"#{rank} ({plays} plays)"
        print(f"  {match_pct:5.1f}%  {name:<32}  {tag}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1]:
        print('usage: uv run python -m scripts.similar "<artist>" [N]', file=sys.stderr)
        sys.exit(64)
    artist_arg = sys.argv[1]
    n_arg = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else DEFAULT_N
    main(artist_arg, n_arg)
