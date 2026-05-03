"""Append an entry to dislikes.md under a named category.

Usage:
    uv run python -m scripts.reject "<label>" "<reason>" [category]
    make reject LABEL='Author & Punisher' REASON='too noisy'
    make reject LABEL='EDM build-drop' REASON='formulaic' CATEGORY='Vibes'

Categories (the H2 sections in dislikes.md):
    Artists (default), Sub-genres / scenes, Vibes / qualities,
    Specific albums.

Category match is case-insensitive substring; "Vibes" matches the
"Vibes / qualities" heading.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from scripts._dislikes import DISLIKES_MD, find_category

DEFAULT_CATEGORY = "Artists"


def append_rejection(
    label: str,
    reason: str,
    category: str = DEFAULT_CATEGORY,
    path: Path | None = None,
    today: str | None = None,
) -> None:
    """Append a rejection to the named category in dislikes.md.

    Replaces the `*(none yet)*` placeholder if present, otherwise
    appends at the end of the section.
    """
    if path is None:
        path = DISLIKES_MD
    if today is None:
        today = date.today().isoformat()
    if not path.exists():
        raise RuntimeError(
            f"dislikes.md not found at {path}. Copy dislikes.example.md to dislikes.md first."
        )

    text = path.read_text()
    new_line = f"- **{label}** — {reason}. *({today})*"

    info = find_category(text, category)
    if not info:
        raise RuntimeError(f"could not find a category matching '{category}' in dislikes.md")

    heading, body, start, end = info

    if "*(none yet)*" in body:
        new_body = body.replace("*(none yet)*", new_line)
    else:
        new_body = body.rstrip() + "\n" + new_line + "\n\n"

    new_text = text[:start] + heading + "\n" + new_body + text[end:]
    path.write_text(new_text)


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            'usage: uv run python -m scripts.reject "<label>" "<reason>" [category]',
            file=sys.stderr,
        )
        return 64
    label = argv[1]
    reason = argv[2]
    category = argv[3] if len(argv) > 3 and argv[3] else DEFAULT_CATEGORY
    try:
        append_rejection(label, reason, category)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"appended to '{category}': **{label}** — {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
