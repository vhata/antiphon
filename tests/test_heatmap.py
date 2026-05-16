"""Tests for scripts.heatmap — pure bucketing and rendering."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from scripts import heatmap


def _track(when: datetime) -> dict[str, Any]:
    return {"date": {"uts": str(int(when.timestamp()))}, "artist": {"#text": "X"}, "name": "Y"}


def test_module_exposes_main_and_bucket() -> None:
    assert hasattr(heatmap, "main")
    assert hasattr(heatmap, "bucket_by_hour_dow")
    assert hasattr(heatmap, "render_grid")


def test_bucket_empty_returns_seven_by_twentyfour_zeros() -> None:
    grid = heatmap.bucket_by_hour_dow([], tz=UTC)
    assert len(grid) == 7
    assert all(len(row) == 24 for row in grid)
    assert sum(sum(row) for row in grid) == 0


def test_bucket_places_scrobble_in_correct_cell() -> None:
    # 2026-05-13 (a Wednesday) at 21:00 UTC.
    tracks = [_track(datetime(2026, 5, 13, 21, 0, tzinfo=UTC))]
    grid = heatmap.bucket_by_hour_dow(tracks, tz=UTC)
    assert grid[2][21] == 1  # Wednesday is index 2
    assert sum(sum(row) for row in grid) == 1


def test_bucket_accumulates_repeated_scrobbles() -> None:
    when = datetime(2026, 5, 11, 9, 0, tzinfo=UTC)  # Monday 09:00
    tracks = [_track(when), _track(when), _track(when)]
    grid = heatmap.bucket_by_hour_dow(tracks, tz=UTC)
    assert grid[0][9] == 3


def test_bucket_ignores_now_playing() -> None:
    tracks: list[dict[str, Any]] = [
        {"@attr": {"nowplaying": "true"}, "name": "live"},
        _track(datetime(2026, 5, 11, 9, 0, tzinfo=UTC)),
    ]
    grid = heatmap.bucket_by_hour_dow(tracks, tz=UTC)
    assert sum(sum(row) for row in grid) == 1


def test_bucket_skips_tracks_without_date_field() -> None:
    tracks: list[dict[str, Any]] = [{"artist": {"#text": "?"}, "name": "?"}]
    grid = heatmap.bucket_by_hour_dow(tracks, tz=UTC)
    assert sum(sum(row) for row in grid) == 0


def test_render_grid_returns_eight_lines_header_plus_seven_days() -> None:
    grid = [[0] * 24 for _ in range(7)]
    rendered = heatmap.render_grid(grid)
    assert len(rendered.splitlines()) == 8


def test_render_grid_includes_day_labels() -> None:
    grid = [[0] * 24 for _ in range(7)]
    rendered = heatmap.render_grid(grid)
    for day_name in heatmap.DAY_NAMES:
        assert day_name in rendered


def test_render_grid_peak_cell_uses_top_block() -> None:
    grid = [[0] * 24 for _ in range(7)]
    grid[3][14] = 99  # peak somewhere mid-week, mid-afternoon
    rendered = heatmap.render_grid(grid)
    assert "█" in rendered
