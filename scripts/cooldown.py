"""Show recommendations from the last N days (the cool-down list).

Usage:
    uv run python -m scripts.cooldown [DAYS]
    make cooldown DAYS=7

Reads `session.log.md` and prints entries within the cutoff. Claude
runs this at session start to know what NOT to re-recommend.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from scripts.log_rec import SESSION_LOG

DEFAULT_DAYS = 7


def recent_recs(
    days: int = DEFAULT_DAYS,
    path: Path | None = None,
    today: str | None = None,
) -> list[tuple[str, str, str]]:
    """Return `[(date, pick, source)]` for entries within the cutoff."""
    if path is None:
        path = SESSION_LOG
    if today is None:
        today = date.today().isoformat()

    if not path.exists():
        return []

    cutoff = (date.fromisoformat(today) - timedelta(days=days)).isoformat()

    entries: list[tuple[str, str, str]] = []
    for line in path.read_text().splitlines():
        if not line.startswith("- "):
            continue
        parts = [p.strip() for p in line[2:].split("|")]
        if len(parts) < 2:
            continue
        entry_date = parts[0]
        if entry_date < cutoff:
            continue
        pick = parts[1]
        source = parts[2] if len(parts) > 2 else ""
        entries.append((entry_date, pick, source))
    return entries


def main(argv: list[str]) -> int:
    days = int(argv[1]) if len(argv) > 1 and argv[1] else DEFAULT_DAYS
    entries = recent_recs(days)
    if not entries:
        print(f"No recommendations logged in the last {days} days.")
        return 0
    print(f"Recommendations from the last {days} days ({len(entries)} entries):")
    for entry_date, pick, source in entries:
        suffix = f"  ({source})" if source else ""
        print(f"  {entry_date}  {pick}{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
