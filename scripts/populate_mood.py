"""Use Claude (via `claude -p` headless mode) to propose candidate
picks for a mood, and append them to `moods.md`.

Usage:
    uv run python -m scripts.populate_mood "<mood>" [N]
    make populate-mood NAME='feisty' N=5

Reads the mood's description from `moods.md`, pulls the listener's
listening shape, calls `claude -p` with a tight prompt asking for N
candidate bullets, and appends them to the mood's `### Candidates`
section.

Requires the `claude` CLI on PATH.

This is the first script in `scripts/` that invokes an LLM rather
than just wrapping data — the architectural step is named in
WISHLIST § 4 commentary.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from scripts._lastfm import call
from scripts._moods import (
    MOODS_MD,
    find_mood_section,
    find_subsection,
    picks_in,
    replace_mood_section_body,
    replace_subsection_body,
    split_bullets,
    strip_none_yet,
)
from scripts.profile import get_username

DEFAULT_N = 5

PROMPT_TEMPLATE = """\
You are populating the candidate list for a mood-based music recommender.

# Mood

**{name}** — {description}

# Listener's listening shape

{shape}

# Existing picks for this mood

Validated (do NOT repeat):
{validated}

Candidates (do NOT repeat):
{candidates}

# Task

Propose {n} NEW candidate picks for the mood above. Each pick MUST be a single
markdown bullet in this exact format:

- **Artist Name — *Album Title* (year)** — one-line rationale.

Output ONLY the bullets. No preamble, no headings, no explanation, no blank
lines between bullets.

Lean on the mood description and on the listener's library shape to find
adjacent picks. Avoid artists already heavily represented in the listener's
top 25 unless the mood specifically calls for them.
"""


def _extract_description(mood_section: str) -> str:
    match = re.match(r"\s*\*([^*]+)\*", mood_section)
    return match.group(1).strip() if match else ""


def _profile_summary(user: str) -> str:
    """Compact listening summary suitable for prompt context."""
    parts: list[str] = []
    for period, label, n in [
        ("7day", "Top 7d", 5),
        ("1month", "Top 1mo", 10),
        ("6month", "Top 6mo", 15),
        ("overall", "Top all-time", 25),
    ]:
        response = call("user.getTopArtists", user=user, period=period, limit=n)
        artists = response["topartists"]["artist"]
        parts.append(f"{label}:")
        for artist in artists:
            parts.append(f"  {artist['playcount']:>5}  {artist['name']}")
        parts.append("")
    return "\n".join(parts)


def _format_picks(picks: list[str]) -> str:
    if not picks:
        return "(none)"
    return "\n".join(f"- {p}" for p in picks)


def build_prompt(
    name: str,
    description: str,
    shape: str,
    validated: list[str],
    candidates: list[str],
    n: int,
) -> str:
    return PROMPT_TEMPLATE.format(
        name=name,
        description=description,
        shape=shape,
        validated=_format_picks(validated),
        candidates=_format_picks(candidates),
        n=n,
    )


def call_claude(prompt: str) -> str:
    """Invoke `claude -p` with the prompt and return stdout."""
    result = subprocess.run(  # noqa: S603, S607 (deliberate CLI invocation)
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def parse_response(response: str) -> list[str]:
    """Extract bullet entries from Claude's response.

    Tolerates preamble or trailing text — picks out lines starting with
    `- ` and joins continuation lines (indented or following the bullet).
    """
    bullets: list[str] = []
    current: list[str] = []
    for line in response.splitlines():
        if line.startswith("- "):
            if current:
                bullets.append(" ".join(current).strip())
                current = []
            current.append(line[2:].strip())
        elif current and (line.startswith("  ") or line.startswith("\t")):
            current.append(line.strip())
        elif current and not line.strip():
            bullets.append(" ".join(current).strip())
            current = []
    if current:
        bullets.append(" ".join(current).strip())
    return [b for b in bullets if b]


def populate(
    name: str,
    n: int = DEFAULT_N,
    path: Path | None = None,
    claude_caller: callable[[str], str] | None = None,  # type: ignore[valid-type]
) -> int:
    """Append N proposed candidates to a mood. Returns the count appended."""
    if path is None:
        path = MOODS_MD
    if claude_caller is None:
        claude_caller = call_claude
    if not path.exists():
        raise RuntimeError(f"moods.md not found at {path}")

    text = path.read_text()
    section = find_mood_section(text, name)
    if section is None:
        raise RuntimeError(f"mood '{name}' not found in moods.md")

    description = _extract_description(section)
    if not description:
        raise RuntimeError(f"mood '{name}' has no italic description")

    user = get_username()
    shape = _profile_summary(user)

    validated = picks_in(section, "Validated")
    candidates = picks_in(section, "Candidates")

    prompt = build_prompt(name, description, shape, validated, candidates, n)
    response = claude_caller(prompt)
    new_picks = parse_response(response)

    if not new_picks:
        raise RuntimeError("claude returned no parseable bullets")

    cand_info = find_subsection(section, "Candidates")
    if not cand_info:
        raise RuntimeError("no Candidates subsection in mood")
    _, cand_body, _, _ = cand_info
    cand_body_clean = strip_none_yet(cand_body)
    cand_preamble, cand_bullets = split_bullets(cand_body_clean)

    for pick in new_picks:
        cand_bullets.append("- " + pick)

    joiner = "\n\n" if cand_preamble.strip() else "\n"
    new_cand_body = (cand_preamble.rstrip() + joiner + "\n".join(cand_bullets)).rstrip() + "\n\n"

    new_section = replace_subsection_body(section, "Candidates", new_cand_body)
    new_text = replace_mood_section_body(text, name, new_section)
    path.write_text(new_text)

    return len(new_picks)


def main(argv: list[str]) -> int:
    if len(argv) < 2 or not argv[1]:
        print('usage: uv run python -m scripts.populate_mood "<mood>" [N]', file=sys.stderr)
        return 64
    name = argv[1]
    n = int(argv[2]) if len(argv) > 2 and argv[2] else DEFAULT_N
    try:
        added = populate(name, n)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"claude -p failed (exit {exc.returncode}):", file=sys.stderr)
        print(exc.stderr, file=sys.stderr)
        return 1
    print(f"appended {added} candidate picks to '{name}'")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
