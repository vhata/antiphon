"""Glanceable single-screen listening snapshot.

Usage:
    uv run python -m scripts.dashboard
    make dashboard

Static one-shot render. Fetches a wide read of the listener's recent
data and prints a rich-formatted snapshot: top artists across the four
time windows, a 30-day scrobble sparkline, top tags, mood-library
fullness, the cool-down list, and a loved-tracks delta. No persistent
state, no interactivity — stays a text-emitting script.
"""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime, timedelta
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts._lastfm import call
from scripts._moods import MOODS_MD, find_mood_section, list_moods, picks_in
from scripts.cooldown import recent_recs
from scripts.profile import get_username

WINDOWS: list[tuple[str, str]] = [
    ("7day", "7 day"),
    ("1month", "1 month"),
    ("6month", "6 month"),
    ("overall", "overall"),
]
SPARK_BLOCKS = "▁▂▃▄▅▆▇█"
PULSE_DAYS = 30
TOP_PER_WINDOW = 5
TOP_GENRES = 8
GENRE_SEED_ARTISTS = 10  # artists.getInfo is called once per seed; keep modest
GENRE_TAGS_PER_ARTIST = 5  # take this many top tags per artist before aggregating
COOLDOWN_DAYS = 7
THIN_MOOD_THRESHOLD = 3  # validated picks below this are flagged as thin
LOVED_WINDOW_DAYS = 7


def sparkline(values: list[int]) -> str:
    if not values:
        return ""
    peak = max(values)
    if peak == 0:
        return SPARK_BLOCKS[0] * len(values)
    steps = len(SPARK_BLOCKS) - 1
    return "".join(SPARK_BLOCKS[min(steps, int(v / peak * steps))] for v in values)


def count_by_day(
    tracks: list[dict[str, Any]],
    today: date,
    days: int = PULSE_DAYS,
) -> list[int]:
    counts = [0] * days
    earliest = today - timedelta(days=days - 1)
    for track in tracks:
        attrs = track.get("@attr") or {}
        if attrs.get("nowplaying") == "true":
            continue
        date_field = track.get("date")
        if not date_field:
            continue
        ts = int(date_field["uts"])
        day = datetime.fromtimestamp(ts, tz=UTC).date()
        offset = (day - earliest).days
        if 0 <= offset < days:
            counts[offset] += 1
    return counts


def mood_health(moods_text: str) -> list[tuple[str, int, int]]:
    """For each mood, return (name, validated_count, candidate_count)."""
    result: list[tuple[str, int, int]] = []
    for name in list_moods(moods_text):
        section = find_mood_section(moods_text, name)
        if section is None:
            continue
        validated = len(picks_in(section, "Validated"))
        candidates = len(picks_in(section, "Candidates"))
        result.append((name, validated, candidates))
    return result


def aggregate_artist_tags(
    items: list[tuple[int, list[str]]],
    top_n: int = TOP_GENRES,
) -> list[tuple[str, int]]:
    """Aggregate artist tags weighted by playcount × inverse-rank.

    `items` is a list of (playcount, ordered_tags) pairs — one per
    artist — where `ordered_tags` is the artist's top tags as returned
    by last.fm in descending order of tag popularity. Each tag's score
    for an artist is `playcount * (GENRE_TAGS_PER_ARTIST - rank)`, so
    the artist's top tag contributes most. Returns the top_n tags by
    total score, descending.
    """
    scores: dict[str, int] = {}
    for playcount, tags in items:
        for rank, tag in enumerate(tags[:GENRE_TAGS_PER_ARTIST]):
            if not tag:
                continue
            weight = (GENRE_TAGS_PER_ARTIST - rank) * playcount
            scores[tag] = scores.get(tag, 0) + weight
    return sorted(scores.items(), key=lambda kv: -kv[1])[:top_n]


def loved_in_window(
    loved: list[dict[str, Any]],
    now: datetime,
    days: int = LOVED_WINDOW_DAYS,
) -> int:
    cutoff = int((now - timedelta(days=days)).timestamp())
    count = 0
    for track in loved:
        date_field = track.get("date")
        if not date_field:
            continue
        ts = int(date_field["uts"])
        if ts >= cutoff:
            count += 1
    return count


def _fetch_pulse_tracks(user: str) -> list[dict[str, Any]]:
    cutoff = datetime.now(UTC) - timedelta(days=PULSE_DAYS)
    response = call(
        "user.getRecentTracks",
        user=user,
        limit=200,
        **{"from": int(cutoff.timestamp())},
    )
    tracks = response.get("recenttracks", {}).get("track", [])
    return list(tracks) if isinstance(tracks, list) else [tracks]


def _header_panel(user: str, total_plays: int) -> Panel:
    today_str = date.today().isoformat()
    body = Text(
        f"{user}   ·   {today_str}   ·   {total_plays:,} total scrobbles",
        justify="center",
    )
    return Panel(body, title="Antiphon — listening snapshot", padding=(0, 2))


def _top_artists_table(user: str) -> Table:
    table = Table(title="Top artists", show_header=True, header_style="bold")
    for _, label in WINDOWS:
        table.add_column(label, no_wrap=False)
    columns: list[list[str]] = []
    for api_period, _ in WINDOWS:
        response = call("user.getTopArtists", user=user, period=api_period, limit=TOP_PER_WINDOW)
        artists = response.get("topartists", {}).get("artist", [])
        columns.append([f"{a['name']} ({int(a['playcount'])})" for a in artists])
    rows = max((len(c) for c in columns), default=0)
    for i in range(rows):
        table.add_row(*(c[i] if i < len(c) else "" for c in columns))
    return table


def _pulse_panel(tracks: list[dict[str, Any]]) -> Panel:
    counts = count_by_day(tracks, date.today())
    line = sparkline(counts)
    total = sum(counts)
    body = Text(f"{line}\n\n{total:,} scrobbles over the last {PULSE_DAYS} days")
    return Panel(body, title=f"Last {PULSE_DAYS} days")


def _fetch_genre_seeds(user: str) -> list[tuple[int, list[str]]]:
    """Fetch (playcount, top-tags) for each of the top N overall artists."""
    response = call(
        "user.getTopArtists",
        user=user,
        period="overall",
        limit=GENRE_SEED_ARTISTS,
    )
    artists = response.get("topartists", {}).get("artist", [])
    seeds: list[tuple[int, list[str]]] = []
    for artist in artists:
        name = artist.get("name", "")
        if not name:
            continue
        playcount = int(artist.get("playcount", 0))
        info = call("artist.getInfo", artist=name)
        tags_data = info.get("artist", {}).get("tags", {}).get("tag", [])
        if isinstance(tags_data, dict):
            tags_data = [tags_data]
        tag_names = [t.get("name", "") for t in tags_data if t.get("name")]
        seeds.append((playcount, tag_names))
    return seeds


def _genres_panel(seeds: list[tuple[int, list[str]]]) -> Panel:
    if not seeds:
        return Panel(Text("(no artist data)"), title="Library genres")
    aggregated = aggregate_artist_tags(seeds)
    if not aggregated:
        return Panel(Text("(no tags found on top artists)"), title="Library genres")
    width = max(len(tag) for tag, _ in aggregated)
    lines = [f"{tag.ljust(width)}   {score:,}" for tag, score in aggregated]
    return Panel(
        Text("\n".join(lines)),
        title=f"Library genres (top {len(aggregated)}, weighted by playcount × tag rank)",
    )


def _moods_panel() -> Panel:
    if not MOODS_MD.exists():
        return Panel(Text("(moods.md not found)"), title="Mood library")
    health = mood_health(MOODS_MD.read_text())
    if not health:
        return Panel(Text("(no moods yet — see moods.example.md)"), title="Mood library")
    table = Table(show_header=True, box=None, padding=(0, 2, 0, 0))
    table.add_column("mood")
    table.add_column("validated", justify="right")
    table.add_column("candidates", justify="right")
    for name, validated, candidates in health:
        marker = "  ·" if validated < THIN_MOOD_THRESHOLD else ""
        table.add_row(name + marker, str(validated), str(candidates))
    return Panel(table, title="Mood library  ( · = thin, fewer than 3 validated)")


def _cooldown_panel() -> Panel:
    entries = recent_recs(COOLDOWN_DAYS)
    if not entries:
        body = Text(f"(no recs logged in the last {COOLDOWN_DAYS} days)")
    else:
        body = Text("\n".join(f"{d}   {pick}" for d, pick, _ in entries))
    return Panel(body, title=f"Cool-down (last {COOLDOWN_DAYS} days)")


def _loved_panel(user: str) -> Panel:
    response = call("user.getLovedTracks", user=user, limit=20)
    loved = response.get("lovedtracks", {}).get("track", [])
    if isinstance(loved, dict):
        loved = [loved]
    fresh = loved_in_window(loved, datetime.now(UTC), days=LOVED_WINDOW_DAYS)
    lines = [f"{fresh} new loved track(s) in the last {LOVED_WINDOW_DAYS} days"]
    if loved:
        lines.append("")
        for track in loved[:5]:
            artist = track.get("artist", {}).get("name", "?")
            name = track.get("name", "?")
            lines.append(f"  {artist} — {name}")
    return Panel(Text("\n".join(lines)), title="Loved (most recent)")


def main() -> int:
    user = get_username()
    console = Console()

    info = call("user.getInfo", user=user)["user"]
    total = int(info.get("playcount", 0))

    pulse_tracks = _fetch_pulse_tracks(user)
    genre_seeds = _fetch_genre_seeds(user)

    console.print(_header_panel(user, total))
    console.print(_top_artists_table(user))
    console.print(_pulse_panel(pulse_tracks))
    console.print(_genres_panel(genre_seeds))
    console.print(_moods_panel())
    console.print(_cooldown_panel())
    console.print(_loved_panel(user))
    return 0


if __name__ == "__main__":
    sys.exit(main())
