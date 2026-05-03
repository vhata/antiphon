"""Shared parser and mutator for moods.md.

The moods.md format: one or more `## <mood name>` sections, each
containing optional prose, a `### Validated` subsection, and a
`### Candidates` subsection. Each subsection contains bullet entries
of the form `- **Artist — *Album***  ...`.

This module is the single source of truth for parsing and modifying
that structure. Scripts that touch moods.md import from here rather
than reimplementing.
"""

from __future__ import annotations

import re
from pathlib import Path

MOODS_MD = Path(__file__).resolve().parent.parent / "moods.md"
META_MOODS = {"adding a new mood"}


def _mood_re(name: str) -> re.Pattern[str]:
    return re.compile(
        rf"(^## {re.escape(name)}\s*$)(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )


def find_mood_section(text: str, name: str) -> str | None:
    """Return the body of `## <name>` (heading excluded), or None."""
    match = _mood_re(name).search(text)
    return match.group(2).strip() if match else None


def find_subsection(body: str, name: str) -> tuple[str, str, int, int] | None:
    """Return `(heading_line, body_text, start, end)` for `### <name>`.

    Offsets are positions within `body`. Returns None if not found.
    """
    pattern = re.compile(
        rf"(^### {re.escape(name)}\s*$)(.*?)(?=^###\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return None
    return match.group(1).rstrip(), match.group(2), match.start(), match.end()


def split_bullets(body: str) -> tuple[str, list[str]]:
    """Split a body into `(preamble, bullets)`.

    Each bullet starts with `- ` and may include continuation lines.
    """
    parts = re.split(r"\n(?=- )", body.rstrip("\n"))
    if not parts:
        return ("", [])
    return (parts[0], parts[1:])


def strip_none_yet(text: str) -> str:
    """Remove `*(none yet)*` placeholder lines from a body."""
    return re.sub(r"^\s*\*\(none yet\)\*\s*$", "", text, flags=re.MULTILINE)


def parse_pick(pick: str) -> tuple[str, str | None]:
    """Extract `(artist, album-or-None)` from a bullet entry.

    Tolerates `**Artist — *Album* (year)**`, `**Artist — Album**`, and
    multi-album `**Artist — *A1* / *A2***` forms (returns the first).
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


def list_moods(text: str) -> list[str]:
    """List `## <name>` mood sections, excluding meta sections."""
    headings = re.findall(r"^##\s+([^#\n]+)$", text, re.MULTILINE)
    return [h.strip() for h in headings if h.strip().lower() not in META_MOODS]


def picks_in(section: str, subheading: str) -> list[str]:
    """Bullet entries under a subsection of a mood section.

    Each returned string is the bullet's *content* — the leading `- `
    stripped, continuation lines joined. Filters out `*(none yet)*`
    placeholders. Returns `[]` if the subsection is missing or empty.
    """
    sub = find_subsection(section, subheading)
    if not sub:
        return []
    _, body, _, _ = sub
    _, bullets = split_bullets(body)
    result: list[str] = []
    for raw in bullets:
        content = raw[2:].strip() if raw.startswith("- ") else raw.strip()
        if content and not content.startswith("*("):
            result.append(content)
    return result


def replace_mood_section_body(text: str, name: str, new_body: str) -> str:
    """Replace `## <name>`'s body in `text`. Heading preserved."""
    match = _mood_re(name).search(text)
    if not match:
        raise RuntimeError(f"mood '{name}' not found")
    return text[: match.start()] + match.group(1).rstrip() + "\n" + new_body + text[match.end() :]


def replace_subsection_body(section: str, sub: str, new_body: str) -> str:
    """Replace `### sub`'s body within a single mood section."""
    info = find_subsection(section, sub)
    if not info:
        raise RuntimeError(f"subsection '### {sub}' not found")
    heading, _, start, end = info
    return section[:start] + heading + "\n" + new_body + section[end:]


def append_mood_section(text: str, scaffold: str) -> str:
    """Append a new mood section, before the meta `## Adding a new mood`.

    If the meta section isn't found, append at the end of the file.
    The caller is responsible for making `scaffold` a complete section
    (heading + body) with no trailing meta heading of its own.
    """
    meta_re = re.compile(r"^##\s+Adding a new mood\s*$", re.MULTILINE | re.IGNORECASE)
    match = meta_re.search(text)
    if match:
        before = text[: match.start()].rstrip()
        return before + "\n\n" + scaffold.strip() + "\n\n---\n\n" + text[match.start() :]
    return text.rstrip() + "\n\n" + scaffold.strip() + "\n"


def mood_exists(text: str, name: str) -> bool:
    """True if a `## <name>` section exists (case-insensitive)."""
    return _mood_re(name).search(text) is not None
