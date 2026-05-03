"""Shared parser and mutator for dislikes.md.

The dislikes.md format: one or more `## <category>` sections, each a
bullet list of `- **<label>** — <reason>. *(YYYY-MM-DD)*` entries
or the placeholder `*(none yet)*`.
"""

from __future__ import annotations

import re
from pathlib import Path

DISLIKES_MD = Path(__file__).resolve().parent.parent / "dislikes.md"


def find_category(text: str, name: str) -> tuple[str, str, int, int] | None:
    """Return `(heading_line, body_text, start, end)` for the matching category.

    Match is case-insensitive substring against the heading text;
    `"Vibes"` matches `"## Vibes / qualities"`. Returns the first match.
    """
    section_re = re.compile(
        r"(^## ([^\n]+)\s*$)(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for match in section_re.finditer(text):
        heading_text = match.group(2).strip()
        if name.lower() in heading_text.lower():
            return match.group(1).rstrip(), match.group(3), match.start(), match.end()
    return None


def list_categories(text: str) -> list[str]:
    """Return all `## <category>` headings in dislikes.md."""
    return [h.strip() for h in re.findall(r"^##\s+([^#\n]+)$", text, re.MULTILINE)]
