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
from pathlib import Path

MOODS_MD = Path(__file__).resolve().parent.parent / "moods.md"
SPOTIFY_SEARCH = "https://open.spotify.com/search/"


def find_section(text: str, name: str) -> str | None:
    """Return the body of the `## <name>` mood section, or None if missing.

    Matching is case-insensitive. The body runs from after the `##` line
    through to the next `## ` heading (or end of file).
    """
    pattern = re.compile(
        rf"^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def extract_picks(section: str, subheading: str) -> list[str]:
    """Return the bullet entries under a `### subheading` block.

    Continuation lines on the next line(s) get joined into a single pick.
    Placeholder bullets like `*(none yet)*` are filtered out.
    """
    pattern = re.compile(
        rf"^###\s+{re.escape(subheading)}\s*$(.*?)(?=^###\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(section)
    if not match:
        return []
    body = match.group(1)

    picks: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if line.startswith("- "):
            if current:
                picks.append(" ".join(current))
                current = []
            current.append(line[2:].strip())
        elif current and stripped and (line.startswith("  ") or line.startswith("\t")):
            current.append(stripped)
    if current:
        picks.append(" ".join(current))

    return [p for p in picks if p and not p.startswith("*(")]


def parse_pick(pick: str) -> tuple[str, str | None]:
    """Extract (artist, album-or-None) from a bullet entry.

    Tolerates `**Artist — *Album* (year)**`, `**Artist — Album**`, and the
    multi-album form `**Artist — *A1* / *A2*** ` (returns the first album).
    """
    bold = re.match(r"\*\*(.+?)\*\*", pick)
    if not bold:
        return (pick.strip(), None)
    bold_text = bold.group(1)
    if " — " not in bold_text:
        return (bold_text.strip(), None)
    artist, rest = bold_text.split(" — ", 1)
    italic = re.search(r"\*([^*]+)\*", rest)
    if italic:
        return (artist.strip(), italic.group(1).strip())
    first = re.split(r"\s+[/(]", rest, maxsplit=1)[0]
    first = first.strip(" *_,;:.")
    return (artist.strip(), first or None)


def spotify_search_url(query: str) -> str:
    return SPOTIFY_SEARCH + urllib.parse.quote(query)


def render(mood_name: str, mood_section: str) -> str:
    lines: list[str] = [f"# {mood_name}", ""]
    desc = re.match(r"\s*\*([^*]+)\*", mood_section)
    if desc:
        lines.extend([f"*{desc.group(1).strip()}*", ""])

    for sub in ("Validated", "Candidates"):
        picks = extract_picks(mood_section, sub)
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


def list_moods(text: str) -> list[str]:
    """List the mood section names in moods.md, excluding meta sections."""
    headings = re.findall(r"^##\s+([^#\n]+)$", text, re.MULTILINE)
    ignore = {"adding a new mood"}
    return [h.strip() for h in headings if h.strip().lower() not in ignore]


def main(mood_name: str) -> int:
    if not MOODS_MD.exists():
        print(f"moods.md not found at {MOODS_MD}", file=sys.stderr)
        print("Copy moods.example.md to moods.md to get started.", file=sys.stderr)
        return 1
    text = MOODS_MD.read_text()
    section = find_section(text, mood_name)
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
