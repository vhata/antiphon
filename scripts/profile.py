"""Compact listening-shape summary for the configured Antiphon user.

Pulls recent tracks + top artists across four time windows + loved
tracks, and prints a tight text format suitable for pasting into an
LLM context.

Reads username from `user.md`; reads LASTFM_API_KEY from the env
(source `.env` first).

Usage:
    set -a; source .env; set +a
    uv run python -m scripts.profile
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts._lastfm import call


def get_username(user_md_path: Path | None = None) -> str:
    """Read the listener's last.fm username from user.md.

    The path defaults to the repo root's user.md but can be overridden
    for testing.
    """
    if user_md_path is None:
        user_md_path = Path(__file__).resolve().parent.parent / "user.md"
    if not user_md_path.exists():
        raise RuntimeError(
            f"user.md not found at {user_md_path}. Copy user.example.md and fill in your username."
        )
    # Match either '**Username:** xyz' or '**last.fm username:** xyz', case-insensitive.
    match = re.search(
        r"\*\*[^*\n]*username:\*\*\s+(\S+)",
        user_md_path.read_text(),
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError(
            "could not find username in user.md (expected a line like '**Username:** vhata')"
        )
    return match.group(1)


def _print_top_artists(user: str, period: str, limit: int, label: str) -> None:
    print(f"{label} (top {limit}):")
    response = call("user.getTopArtists", user=user, period=period, limit=limit)
    for artist in response["topartists"]["artist"]:
        print(f"  {artist['playcount']:>5}  {artist['name']}")
    print()


def main() -> None:
    user = get_username()
    print(f"=== {user} listening profile ===")
    print()

    print("RECENT (last 30):")
    recent = call("user.getRecentTracks", user=user, limit=30)
    for track in recent["recenttracks"]["track"]:
        artist = track.get("artist", {}).get("#text", "?")
        print(f"  {artist} — {track.get('name', '?')}")
    print()

    _print_top_artists(user, "7day", 10, "TOP 7d")
    _print_top_artists(user, "1month", 15, "TOP 1mo")
    _print_top_artists(user, "6month", 25, "TOP 6mo")
    _print_top_artists(user, "overall", 25, "TOP all-time")

    print("LOVED (latest 15):")
    loved = call("user.getLovedTracks", user=user, limit=15)
    for track in loved["lovedtracks"]["track"]:
        print(f"  {track['artist']['name']} — {track['name']}")


if __name__ == "__main__":
    main()
