"""Promote a pick from Candidates to Validated under a named mood.

Usage:
    uv run python -m scripts.validate "<mood>" "<pick substring>"
    make validate MOOD='small hours' PICK='Stars of the Lid'

The matching candidate bullet (multi-line entries supported) is
moved into the Validated section with a `*Validated YYYY-MM-DD.*`
note appended. Mood and pick matches are case-insensitive; pick
matches by substring against the bullet text.
"""

from __future__ import annotations

import sys
from datetime import date
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


def promote(
    mood: str,
    pick_substring: str,
    path: Path | None = None,
    today: str | None = None,
) -> str:
    """Move a matching candidate bullet to validated. Returns the bullet text."""
    if path is None:
        path = MOODS_MD
    if today is None:
        today = date.today().isoformat()
    if not path.exists():
        raise RuntimeError(f"moods.md not found at {path}")

    text = path.read_text()

    section = find_mood_section(text, mood)
    if section is None:
        raise RuntimeError(f"mood '{mood}' not found in moods.md")

    cand_info = find_subsection(section, "Candidates")
    if not cand_info:
        raise RuntimeError(f"no '### Candidates' subsection under mood '{mood}'")
    _, cand_body, _, _ = cand_info

    cand_preamble, cand_bullets = split_bullets(cand_body)

    matching_idx = None
    for idx, bullet in enumerate(cand_bullets):
        if pick_substring.lower() in bullet.lower():
            matching_idx = idx
            break
    if matching_idx is None:
        raise RuntimeError(f"pick '{pick_substring}' not found in candidates for '{mood}'")

    promoted = cand_bullets.pop(matching_idx).rstrip()
    promoted_dated = promoted + f" *Validated {today}.*"

    if cand_bullets:
        new_cand_body = (
            cand_preamble.rstrip() + "\n\n" + "\n".join(cand_bullets)
        ).rstrip() + "\n\n"
    else:
        new_cand_body = (cand_preamble.rstrip() + "\n\n*(none yet)*").rstrip() + "\n\n"

    section_after_cand = replace_subsection_body(section, "Candidates", new_cand_body)

    val_info = find_subsection(section_after_cand, "Validated")
    if not val_info:
        raise RuntimeError(f"no '### Validated' subsection under mood '{mood}'")
    _, val_body, _, _ = val_info

    val_body_clean = strip_none_yet(val_body)
    val_preamble, val_bullets = split_bullets(val_body_clean)
    val_bullets.append(promoted_dated)

    joiner = "\n\n" if val_preamble.strip() else "\n"
    new_val_body = (val_preamble.rstrip() + joiner + "\n".join(val_bullets)).rstrip() + "\n\n"

    final_section = replace_subsection_body(section_after_cand, "Validated", new_val_body)

    new_text = replace_mood_section_body(text, mood, final_section)
    path.write_text(new_text)
    return promoted


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            'usage: uv run python -m scripts.validate "<mood>" "<pick substring>"',
            file=sys.stderr,
        )
        return 64
    mood = argv[1]
    pick = argv[2]
    try:
        bullet = promote(mood, pick)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    snippet = bullet[:90].replace("\n", " ")
    print(f"validated under '{mood}': {snippet}...")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
