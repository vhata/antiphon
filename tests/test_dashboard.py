"""Tests for scripts.dashboard — pure data-shaping functions."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from scripts import dashboard


def test_module_exposes_main() -> None:
    assert hasattr(dashboard, "main")


def test_sparkline_empty_returns_empty_string() -> None:
    assert dashboard.sparkline([]) == ""


def test_sparkline_all_zeros_uses_lowest_block() -> None:
    assert dashboard.sparkline([0, 0, 0]) == "▁▁▁"


def test_sparkline_uniform_nonzero_renders_uniform_bars() -> None:
    rendered = dashboard.sparkline([3, 3, 3, 3])
    assert len(rendered) == 4
    # all the same character
    assert len(set(rendered)) == 1


def test_sparkline_range_spans_low_to_high() -> None:
    rendered = dashboard.sparkline([0, 1, 2, 3, 4, 5, 6, 7])
    assert len(rendered) == 8
    assert rendered[0] == "▁"
    assert rendered[-1] == "█"


def test_count_by_day_buckets_two_into_today_one_into_yesterday() -> None:
    today = date(2026, 5, 15)
    tracks: list[dict[str, Any]] = [
        {"date": {"uts": str(int(datetime(2026, 5, 15, 10, 0, tzinfo=UTC).timestamp()))}},
        {"date": {"uts": str(int(datetime(2026, 5, 15, 13, 0, tzinfo=UTC).timestamp()))}},
        {"date": {"uts": str(int(datetime(2026, 5, 14, 9, 0, tzinfo=UTC).timestamp()))}},
    ]
    counts = dashboard.count_by_day(tracks, today, days=30)
    assert len(counts) == 30
    assert counts[-1] == 2
    assert counts[-2] == 1


def test_count_by_day_ignores_now_playing() -> None:
    today = date(2026, 5, 15)
    tracks: list[dict[str, Any]] = [
        {"@attr": {"nowplaying": "true"}, "name": "live"},
        {"date": {"uts": str(int(datetime(2026, 5, 15, 10, 0, tzinfo=UTC).timestamp()))}},
    ]
    counts = dashboard.count_by_day(tracks, today, days=30)
    assert counts[-1] == 1


def test_count_by_day_skips_tracks_outside_window() -> None:
    today = date(2026, 5, 15)
    tracks: list[dict[str, Any]] = [
        {"date": {"uts": str(int(datetime(2026, 3, 15, 10, 0, tzinfo=UTC).timestamp()))}},
    ]
    counts = dashboard.count_by_day(tracks, today, days=30)
    assert sum(counts) == 0


def test_mood_health_counts_validated_and_candidates_per_mood() -> None:
    text = """# Moods

## small hours

Late-night, slow.

### Validated

- **Brian Eno — *Thursday Afternoon***
- **Stars of the Lid — *Avec Laudenum***

### Candidates

- **Max Richter — *Sleep***

## coding

### Validated

*(none yet)*

### Candidates

- **GAS — *Pop***
- **Tim Hecker — *Ravedeath, 1972***

## Adding a new mood

Meta section — should be excluded.
"""
    health = dashboard.mood_health(text)
    assert ("small hours", 2, 1) in health
    assert ("coding", 0, 2) in health
    assert all(name.lower() != "adding a new mood" for name, _, _ in health)


def test_aggregate_artist_tags_returns_empty_for_empty_input() -> None:
    assert dashboard.aggregate_artist_tags([]) == []


def test_aggregate_artist_tags_weights_higher_ranks_more() -> None:
    # A single artist with playcount 100 and two tags. Tag at rank 0
    # should score higher than tag at rank 1.
    result = dashboard.aggregate_artist_tags([(100, ["trip-hop", "electronic"])], top_n=2)
    assert result[0][0] == "trip-hop"
    assert result[1][0] == "electronic"
    assert result[0][1] > result[1][1]


def test_aggregate_artist_tags_sums_across_artists() -> None:
    # Two artists both tagged "electronic"; the tag should accumulate.
    result = dashboard.aggregate_artist_tags(
        [
            (1000, ["electronic"]),
            (500, ["electronic"]),
        ],
        top_n=5,
    )
    assert len(result) == 1
    assert result[0][0] == "electronic"
    # weight = (5 - 0) * playcount summed = 5 * 1500 = 7500
    assert result[0][1] == 7500


def test_aggregate_artist_tags_respects_top_n() -> None:
    items: list[tuple[int, list[str]]] = [
        (100, ["a", "b", "c", "d", "e"]),
    ]
    assert len(dashboard.aggregate_artist_tags(items, top_n=3)) == 3


def test_aggregate_artist_tags_caps_per_artist_at_genre_tags_per_artist() -> None:
    # Tags past the GENRE_TAGS_PER_ARTIST cutoff are ignored.
    long_tag_list = [f"tag{i}" for i in range(20)]
    result = dashboard.aggregate_artist_tags([(100, long_tag_list)], top_n=20)
    assert len(result) == dashboard.GENRE_TAGS_PER_ARTIST


def test_loved_in_window_filters_by_timestamp() -> None:
    now = datetime(2026, 5, 15, 12, 0, tzinfo=UTC)
    one_day_ago = int(datetime(2026, 5, 14, 12, 0, tzinfo=UTC).timestamp())
    ten_days_ago = int(datetime(2026, 5, 5, 12, 0, tzinfo=UTC).timestamp())
    loved: list[dict[str, Any]] = [
        {"date": {"uts": str(one_day_ago)}, "artist": {"name": "X"}, "name": "Y"},
        {"date": {"uts": str(ten_days_ago)}, "artist": {"name": "A"}, "name": "B"},
    ]
    assert dashboard.loved_in_window(loved, now, days=7) == 1


def test_loved_in_window_handles_missing_date_field() -> None:
    now = datetime(2026, 5, 15, 12, 0, tzinfo=UTC)
    loved: list[dict[str, Any]] = [{"artist": {"name": "X"}, "name": "Y"}]
    assert dashboard.loved_in_window(loved, now, days=7) == 0
