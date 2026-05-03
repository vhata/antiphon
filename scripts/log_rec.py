"""Append a recommendation to session.log.md.

Usage:
    uv run python -m scripts.log_rec "<pick>" [source]
    make log-rec PICK='Artist — Album' SOURCE='small hours'

Appends to `session.log.md` (gitignored). Claude calls this after
each recommendation so the cool-down filter can pick it up next
session.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

SESSION_LOG = Path(__file__).resolve().parent.parent / "session.log.md"

HEADER = """\
# Session log

Append-only log of recommendations made. Used by the cool-down filter
to avoid re-recommending the same picks within ~7 days. Format per
entry: `- YYYY-MM-DD | <pick> | <source>`.

## Entries

"""


def append_rec(
    pick: str,
    source: str = "",
    path: Path | None = None,
    today: str | None = None,
) -> bool:
    """Append a rec entry. Returns True if appended, False if duplicate."""
    if path is None:
        path = SESSION_LOG
    if today is None:
        today = date.today().isoformat()

    if not path.exists():
        path.write_text(HEADER)

    text = path.read_text()
    if not text.endswith("\n"):
        text += "\n"

    line = f"- {today} | {pick} | {source}"
    if line in text:
        return False

    path.write_text(text + line + "\n")
    return True


def main(argv: list[str]) -> int:
    if len(argv) < 2 or not argv[1]:
        print('usage: uv run python -m scripts.log_rec "<pick>" [source]', file=sys.stderr)
        return 64
    pick = argv[1]
    source = argv[2] if len(argv) > 2 else ""
    appended = append_rec(pick, source)
    if appended:
        print(f"logged: {pick}")
    else:
        print(f"already logged today: {pick}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
