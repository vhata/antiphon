"""Tests for scripts.daily — strategy rotation, persistence, idempotency."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from scripts import daily


def test_strategy_for_date_is_stable() -> None:
    d1 = date(2026, 5, 3)
    assert daily.strategy_for_date(d1) == daily.strategy_for_date(d1)


def test_strategy_for_date_rotates_across_days() -> None:
    strategies = [daily.strategy_for_date(date(2026, 5, n)) for n in range(1, 11)]
    # Should hit at least 4 of the 5 strategies in 10 days
    assert len(set(strategies)) >= 4


def test_existing_pick_returns_none_for_no_log(tmp_path: Path) -> None:
    assert daily.existing_pick("2026-05-03", path=tmp_path / "missing.md") is None


def test_existing_pick_finds_logged_entry(tmp_path: Path) -> None:
    p = tmp_path / "daily.log.md"
    p.write_text("# Daily picks\n\n- 2026-05-03 | Artist — Track | comfort\n")
    entry = daily.existing_pick("2026-05-03", path=p)
    assert entry is not None
    assert "Artist — Track" in entry
    assert "comfort" in entry


def test_existing_pick_returns_none_for_other_date(tmp_path: Path) -> None:
    p = tmp_path / "daily.log.md"
    p.write_text("# Daily picks\n\n- 2026-05-02 | Artist — Track | comfort\n")
    assert daily.existing_pick("2026-05-03", path=p) is None


def test_append_pick_creates_file_with_header(tmp_path: Path) -> None:
    p = tmp_path / "daily.log.md"
    daily.append_pick("2026-05-03", "Artist", "Track", "comfort", path=p)
    text = p.read_text()
    assert "# Daily picks" in text
    assert "- 2026-05-03 | Artist — Track | comfort" in text


def test_append_pick_dedupes(tmp_path: Path) -> None:
    p = tmp_path / "daily.log.md"
    daily.append_pick("2026-05-03", "X", "Y", "comfort", path=p)
    daily.append_pick("2026-05-03", "X", "Y", "comfort", path=p)
    assert p.read_text().count("X — Y") == 1


def test_spotify_url_encodes_spaces() -> None:
    url = daily.spotify_url("Massive Attack", "Teardrop")
    assert "Massive%20Attack%20Teardrop" in url


def test_strategies_set_matches_pickers() -> None:
    assert set(daily.STRATEGIES) == set(daily.PICKERS.keys())
