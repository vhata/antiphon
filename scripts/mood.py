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


def render(mood_name: str, mood_section: str) -> str:
    lines: list[str] = [f"# {mood_name}", ""]
    desc = re.match(r"\s*\*([^*]+)\*", mood_section)
    if desc:
        lines.extend([f"*{desc.group(1).strip()}*", ""])

    for sub in ("Validated", "Candidates"):
        picks = picks_in(mood_section, sub)
        if not picks:
            continue
        lines.append(f"## {sub}")
        lines.append("")
        for pick in picks:
            artist, album = parse_pick(pick)
            query = f"{artist} {album}" if album else artist
            display = f"{artist} — {album}" if album else artist
            lines.append(f"- [{display}]({spotify_search_url(query)})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(mood_name: str) -> int:
    if not MOODS_MD.exists():
        print(f"moods.md not found at {MOODS_MD}", file=sys.stderr)
        print("Copy moods.example.md to moods.md to get started.", file=sys.stderr)
        return 1
    text = MOODS_MD.read_text()
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
    if len(sys.argv) < 2:
        print('usage: uv run python -m scripts.mood "<mood name>"', file=sys.stderr)
        sys.exit(64)
    sys.exit(main(sys.argv[1]))
