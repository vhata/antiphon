"""Append a candidate pick to a mood's `### Candidates` section.

Usage:
    uv run python -m scripts.add_candidate "<mood>" "<artist>" "<album>" [year] [why]
    make add-candidate MOOD='feisty' ARTIST='Charli XCX' ALBUM='brat' YEAR=2024 WHY='namesake'

Appends a bullet of the form:

    - **Artist — *Album* (year)** — why.

Year and why are optional. Replaces the `*(none yet)*` placeholder
in Candidates if present; otherwise appends at the end.
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts._moods import (
    MOODS_MD,
    find_mood_section,
    find_subsection,
    replace_mood_section_body,
    replace_subsection_body,
    split_bullets,
    strip_none_yet,
)


def format_bullet(artist: str, album: str, year: str = "", why: str = "") -> str:
    """Build a properly-formatted candidate bullet."""
    head = f"- **{artist} — *{album}*"
    if year:
        head += f" ({year})"
    head += "**"
    if why:
        head += f" — {why.rstrip('.')}."
    return head


def add_candidate(
    mood: str,
    artist: str,
    album: str,
    year: str = "",
    why: str = "",
    path: Path | None = None,
) -> str:
    """Append a candidate to a mood. Returns the bullet text."""
    if path is None:
        path = MOODS_MD
    if not path.exists():
        raise RuntimeError(f"moods.md not found at {path}")

    text = path.read_text()
    section = find_mood_section(text, mood)
    if section is None:
        raise RuntimeError(f"mood '{mood}' not found in moods.md")

    cand_info = find_subsection(section, "Candidates")
    if not cand_info:
        raise RuntimeError(f"no Candidates subsection under '{mood}'")
    _, cand_body, _, _ = cand_info

    bullet = format_bullet(artist, album, year, why)

    cand_body_clean = strip_none_yet(cand_body)
    cand_preamble, cand_bullets = split_bullets(cand_body_clean)
    cand_bullets.append(bullet)

    joiner = "\n\n" if cand_preamble.strip() else "\n"
    new_cand_body = (cand_preamble.rstrip() + joiner + "\n".join(cand_bullets)).rstrip() + "\n\n"

    new_section = replace_subsection_body(section, "Candidates", new_cand_body)
    new_text = replace_mood_section_body(text, mood, new_section)
    path.write_text(new_text)
    return bullet


def main(argv: list[str]) -> int:
    if len(argv) < 4 or not argv[1] or not argv[2] or not argv[3]:
        print(
            "usage: uv run python -m scripts.add_candidate "
            '"<mood>" "<artist>" "<album>" [year] [why]',
            file=sys.stderr,
        )
        return 64
    mood = argv[1]
    artist = argv[2]
    album = argv[3]
    year = argv[4] if len(argv) > 4 else ""
    why = argv[5] if len(argv) > 5 else ""
    try:
        bullet = add_candidate(mood, artist, album, year, why)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"added to '{mood}': {bullet}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
