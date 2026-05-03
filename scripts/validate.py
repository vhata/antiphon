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

import re
import sys
from datetime import date
from pathlib import Path

MOODS_MD = Path(__file__).resolve().parent.parent / "moods.md"


def _split_bullets(body: str) -> tuple[str, list[str]]:
    """Return (preamble, bullets) for a section body.

    Bullets begin with `- ` at column 0; continuation lines (indented
    or blank-followed-by-indent) are kept attached to their bullet.
    """
    parts = re.split(r"\n(?=- )", body.rstrip("\n"))
    if not parts:
        return ("", [])
    return (parts[0], parts[1:])


def _strip_none_yet(body: str) -> str:
    return re.sub(r"^\s*\*\(none yet\)\*\s*$", "", body, flags=re.MULTILINE)


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

    mood_re = re.compile(
        rf"(^## {re.escape(mood)}\s*$)(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    mood_match = mood_re.search(text)
    if not mood_match:
        raise RuntimeError(f"mood '{mood}' not found in moods.md")

    mood_heading = mood_match.group(1)
    mood_body = mood_match.group(2)

    cand_re = re.compile(r"(^### Candidates\s*$)(.*?)(?=^###\s|\Z)", re.MULTILINE | re.DOTALL)
    cand_match = cand_re.search(mood_body)
    if not cand_match:
        raise RuntimeError(f"no '### Candidates' subsection under mood '{mood}'")

    cand_preamble, cand_bullets = _split_bullets(cand_match.group(2))

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

    new_cand_section = cand_match.group(1) + "\n" + new_cand_body
    mood_body_after_cand = (
        mood_body[: cand_match.start()] + new_cand_section + mood_body[cand_match.end() :]
    )

    val_re = re.compile(r"(^### Validated\s*$)(.*?)(?=^###\s|\Z)", re.MULTILINE | re.DOTALL)
    val_match = val_re.search(mood_body_after_cand)
    if not val_match:
        raise RuntimeError(f"no '### Validated' subsection under mood '{mood}'")

    val_body_clean = _strip_none_yet(val_match.group(2))
    val_preamble, val_bullets = _split_bullets(val_body_clean)
    val_bullets.append(promoted_dated)

    joiner = "\n\n" if val_preamble.strip() else "\n"
    new_val_body = (val_preamble.rstrip() + joiner + "\n".join(val_bullets)).rstrip() + "\n\n"

    new_val_section = val_match.group(1) + "\n" + new_val_body
    final_mood_body = (
        mood_body_after_cand[: val_match.start()]
        + new_val_section
        + mood_body_after_cand[val_match.end() :]
    )

    new_text = (
        text[: mood_match.start()] + mood_heading + final_mood_body + text[mood_match.end() :]
    )
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
