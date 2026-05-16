"""Look up a mood in moods.md and print its picks as Spotify search links.

Usage:
    uv run python -m scripts.mood "<mood name>"

Or via the Makefile:
    make mood NAME="<mood name>"

Examples:
    uv run python -m scripts.mood "small hours"
    make mood NAME="deep work"

Reads `moods.md` in the repo root. Mood names match case-insensitively.
"""

from __future__ import annotations

import re
import sys
import urllib.parse

from scripts import _spotify
from scripts._moods import (
    MOODS_MD,
    find_mood_section,
    list_moods,
    parse_pick,
    picks_in,
)

SPOTIFY_SEARCH = "https://open.spotify.com/search/"


def spotify_search_url(query: str) -> str:
    return SPOTIFY_SEARCH + urllib.parse.quote(query)


def spotify_url(artist: str, album: str | None = None) -> str:
    """Resolve to a direct Spotify album/artist URL when credentials allow; else search URL.

    Picks in `moods.md` are usually albums (`artist — album`) but can
    be artist-only. Falls back silently to the search URL when
    credentials are missing or the API returns no hit.
    """
    if _spotify.is_available():
        direct = _spotify.search_album(artist, album) if album else _spotify.search_artist(artist)
        if direct:
            return direct
    query = f"{artist} {album}".strip() if album else artist
    return spotify_search_url(query)


def render(mood_name: str, mood_section: str) -> str:
    lines: list[str] = [f"# {mood_name}", ""]
    desc = re.match(r"\s*\*([^*]+)\*", mood_section)
    if desc:
        lines.extend([f"*{desc.group(1).strip()}*", ""])

    any_picks = False
    for sub in ("Validated", "Candidates"):
        picks = picks_in(mood_section, sub)
        if not picks:
            continue
        any_picks = True
        lines.append(f"## {sub}")
        lines.append("")
        for pick in picks:
            artist, album = parse_pick(pick)
            display = f"{artist} — {album}" if album else artist
            lines.append(f"- [{display}]({spotify_url(artist, album)})")
        lines.append("")

    if not any_picks:
        lines.append("*(no picks yet — ask Claude for some, or hand-edit `moods.md`)*")

    return "\n".join(lines).rstrip() + "\n"


def main(mood_name: str | None = None) -> int:
    if not MOODS_MD.exists():
        print(f"moods.md not found at {MOODS_MD}", file=sys.stderr)
        print("Copy moods.example.md to moods.md to get started.", file=sys.stderr)
        return 1
    text = MOODS_MD.read_text()

    if not mood_name:
        moods = list_moods(text)
        if not moods:
            print("no moods defined yet — try `make add-mood NAME='<name>'` first")
            return 0
        print("Available moods:")
        for m in moods:
            print(f"  - {m}")
        print()
        print("Print picks for a mood: `make mood NAME='<mood>'`  or  `make mood <mood>`")
        return 0

    section = find_mood_section(text, mood_name)
    if section is None:
        print(f"mood '{mood_name}' not found in moods.md", file=sys.stderr)
        moods = list_moods(text)
        if moods:
            print("Available moods:", file=sys.stderr)
            for m in moods:
                print(f"  - {m}", file=sys.stderr)
        return 2
    print(render(mood_name, section), end="")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(main(arg))
