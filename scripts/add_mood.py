"""Add a new mood section to moods.md.

Usage:
    uv run python -m scripts.add_mood "<name>" ["<description>"]
    make add-mood NAME='deep work' DESC='Focused coding.'
    make add-mood NAME='deep work'   # description left as a placeholder

Inserts the new section above the meta `## Adding a new mood`
section. Refuses if a mood with the same name already exists. The
candidate list starts empty — populate by hand or via Claude, then
use `make validate` to promote picks as you confirm them.
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts._moods import MOODS_MD, append_mood_section, mood_exists

SCAFFOLD_TEMPLATE = """\
## {name}

*{desc}*

<!-- describe what picks should be: shape, vocal-density, energy, etc. -->

### Validated

*(none yet)*

### Candidates

*(none yet)*
"""

DEFAULT_DESC = "describe this mood in one sentence"


def add(name: str, desc: str = "", path: Path | None = None) -> None:
    """Add a new mood section to moods.md.

    Raises if the file is missing or if a mood with the same name
    already exists (case-insensitive).
    """
    if path is None:
        path = MOODS_MD
    if not path.exists():
        raise RuntimeError(
            f"moods.md not found at {path}. Copy moods.example.md to moods.md first."
        )
    text = path.read_text()
    if mood_exists(text, name):
        raise RuntimeError(f"mood '{name}' already exists in moods.md")
    scaffold = SCAFFOLD_TEMPLATE.format(name=name, desc=desc or DEFAULT_DESC)
    new_text = append_mood_section(text, scaffold)
    path.write_text(new_text)


def main(argv: list[str]) -> int:
    if len(argv) < 2 or not argv[1]:
        print(
            'usage: uv run python -m scripts.add_mood "<name>" ["<description>"]',
            file=sys.stderr,
        )
        return 64
    name = argv[1]
    desc = argv[2] if len(argv) > 2 else ""
    try:
        add(name, desc)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"added mood '{name}' to moods.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
