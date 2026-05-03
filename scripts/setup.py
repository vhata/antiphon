"""Interactive setup wizard for first-time Antiphon users.

Walks the new user from a fresh clone to a configured local install:
the four gitignored state files (`user.md`, `.env`, `moods.md`,
`dislikes.md`) get scaffolded from their committed `.example`
templates, with prompts for the two values that need them (the
last.fm username and API key).

Stdlib-only, so it runs *before* `make install` (no uv required).
Idempotent: re-running skips already-configured steps.

Usage:
    python3 scripts/setup.py
    make setup
"""

from __future__ import annotations

import re
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

USER_MD = REPO_ROOT / "user.md"
USER_EXAMPLE = REPO_ROOT / "user.example.md"
ENV = REPO_ROOT / ".env"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
MOODS = REPO_ROOT / "moods.md"
MOODS_EXAMPLE = REPO_ROOT / "moods.example.md"
DISLIKES = REPO_ROOT / "dislikes.md"
DISLIKES_EXAMPLE = REPO_ROOT / "dislikes.example.md"

KEY_REGISTRATION_URL = "https://www.last.fm/api/account/create"


def has_username(user_md_text: str) -> bool:
    """True if user.md has a populated username (not the example placeholder)."""
    match = re.search(
        r"\*\*[^*\n]*username:\*\*\s+(\S+)",
        user_md_text,
        re.IGNORECASE,
    )
    if not match:
        return False
    value = match.group(1).strip()
    return not value.startswith("*(")  # *(your last.fm username)* placeholder


def has_api_key(env_text: str) -> bool:
    """True if env_text has a non-empty LASTFM_API_KEY assignment."""
    for line in env_text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("LASTFM_API_KEY="):
            _, _, value = stripped.partition("=")
            if value.strip():
                return True
    return False


def _step_user_md(prompt_for: Callable[[str], str]) -> None:
    print()
    print("Step 1 — user.md  (your last.fm username)")
    if USER_MD.exists() and has_username(USER_MD.read_text()):
        print("  ✓ already configured, skipping")
        return
    if not USER_EXAMPLE.exists():
        print(f"  ⚠ user.example.md missing at {USER_EXAMPLE}; cannot scaffold")
        return
    username = prompt_for("  Your last.fm username: ").strip()
    if not username:
        print("  ⚠ skipped (no username given)")
        return
    template = USER_EXAMPLE.read_text()
    populated = template.replace("*(your last.fm username)*", username)
    USER_MD.write_text(populated)
    print(f"  ✓ wrote user.md (username: {username})")


def _step_env(prompt_for: Callable[[str], str]) -> None:
    print()
    print("Step 2 — .env  (your last.fm API key)")
    if ENV.exists() and has_api_key(ENV.read_text()):
        print("  ✓ already configured, skipping")
        return
    if not ENV_EXAMPLE.exists():
        print(f"  ⚠ .env.example missing at {ENV_EXAMPLE}; cannot scaffold")
        return
    print(f"  Get a free key at: {KEY_REGISTRATION_URL}")
    api_key = prompt_for("  Paste your LASTFM_API_KEY: ").strip()
    if not api_key:
        print("  ⚠ skipped (no key given)")
        return
    template = ENV_EXAMPLE.read_text()
    if "LASTFM_API_KEY=" in template:
        new_lines = [
            f"LASTFM_API_KEY={api_key}" if line.lstrip().startswith("LASTFM_API_KEY=") else line
            for line in template.splitlines()
        ]
        populated = "\n".join(new_lines)
        if not populated.endswith("\n"):
            populated += "\n"
    else:
        populated = template.rstrip() + f"\nLASTFM_API_KEY={api_key}\n"
    ENV.write_text(populated)
    print("  ✓ wrote .env")


def _step_copy(label: str, source: Path, target: Path) -> None:
    print()
    print(f"Step — {label}")
    if target.exists():
        print(f"  ✓ {target.name} already exists, skipping")
        return
    if not source.exists():
        print(f"  ⚠ {source.name} missing at {source}; cannot scaffold")
        return
    shutil.copy(source, target)
    print(f"  ✓ copied {source.name} → {target.name}")


def main(prompt_for: Callable[[str], str] = input) -> int:
    print("┌────────────────────────────────────────┐")
    print("│  Antiphon setup                        │")
    print("└────────────────────────────────────────┘")
    print()
    print("Configures four gitignored state files (safe to re-run):")
    print("  user.md       — your last.fm username")
    print("  .env          — your last.fm API key")
    print("  moods.md      — mood library (copy of moods.example.md)")
    print("  dislikes.md   — anti-rec list (copy of dislikes.example.md)")

    _step_user_md(prompt_for)
    _step_env(prompt_for)
    _step_copy("moods.md", MOODS_EXAMPLE, MOODS)
    _step_copy("dislikes.md", DISLIKES_EXAMPLE, DISLIKES)

    print()
    print("┌────────────────────────────────────────┐")
    print("│  Done.                                 │")
    print("└────────────────────────────────────────┘")
    print()
    print("Next steps:")
    print("  1. make install   — install the Python toolchain (requires uv)")
    print("  2. make profile   — verify the last.fm connection works")
    print("  3. open in Claude Code, ask 'What should I listen to right now?'")
    print()
    print("If you'd rather use the lastfm-mcp.com OAuth path instead of an")
    print("API key, see ONBOARDING.md § 'Path B'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
