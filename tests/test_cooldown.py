"""Tests for scripts.log_rec and scripts.cooldown."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import cooldown, log_rec


def test_append_rec_creates_file_with_header(tmp_path: Path) -> None:
    p = tmp_path / "session.log.md"
    appended = log_rec.append_rec("Artist — Album", "small hours", path=p, today="2026-05-04")
    assert appended is True
    text = p.read_text()
    assert "Session log" in text
    assert "- 2026-05-04 | Artist — Album | small hours" in text


def test_append_rec_dedupes(tmp_path: Path) -> None:
    p = tmp_path / "session.log.md"
    log_rec.append_rec("X — Y", "mood", path=p, today="2026-05-04")
    appended_again = log_rec.append_rec("X — Y", "mood", path=p, today="2026-05-04")
    assert appended_again is False
    text = p.read_text()
    assert text.count("X — Y") == 1


def test_append_rec_handles_no_source(tmp_path: Path) -> None:
    p = tmp_path / "session.log.md"
    log_rec.append_rec("Artist — Album", path=p, today="2026-05-04")
    assert "- 2026-05-04 | Artist — Album | " in p.read_text()


def test_recent_recs_returns_empty_when_no_log(tmp_path: Path) -> None:
    assert cooldown.recent_recs(7, path=tmp_path / "missing.log.md") == []


def test_recent_recs_filters_by_cutoff(tmp_path: Path) -> None:
    p = tmp_path / "session.log.md"
    p.write_text(
        "# Session log\n\n## Entries\n\n"
        "- 2026-04-20 | Old — Album | mood\n"
        "- 2026-05-01 | Newer — Album | mood\n"
        "- 2026-05-04 | Newest — Album | mood\n"
    )
    entries = cooldown.recent_recs(days=7, path=p, today="2026-05-04")
    names = [e[1] for e in entries]
    assert "Newer — Album" in names
    assert "Newest — Album" in names
    assert "Old — Album" not in names


def test_recent_recs_includes_source(tmp_path: Path) -> None:
    p = tmp_path / "session.log.md"
    p.write_text("# Session log\n\n- 2026-05-04 | X — Y | small hours\n- 2026-05-04 | A — B | \n")
    entries = cooldown.recent_recs(days=7, path=p, today="2026-05-04")
    assert ("2026-05-04", "X — Y", "small hours") in entries
    assert ("2026-05-04", "A — B", "") in entries


def test_recent_recs_skips_non_bullet_lines(tmp_path: Path) -> None:
    p = tmp_path / "session.log.md"
    p.write_text("# Session log\n\nSome prose\n\n- 2026-05-04 | X — Y | mood\nanother prose line\n")
    entries = cooldown.recent_recs(days=7, path=p, today="2026-05-04")
    assert entries == [("2026-05-04", "X — Y", "mood")]


@pytest.mark.parametrize("days", [1, 7, 30, 365])
def test_recent_recs_respects_days_arg(tmp_path: Path, days: int) -> None:
    p = tmp_path / "session.log.md"
    p.write_text(
        "# Session log\n\n"
        "- 2025-05-04 | OneYearAgo | mood\n"
        "- 2026-04-27 | OneWeekAgo | mood\n"
        "- 2026-05-04 | Today | mood\n"
    )
    entries = cooldown.recent_recs(days=days, path=p, today="2026-05-04")
    names = {e[1] for e in entries}
    assert "Today" in names
    if days >= 7:
        assert "OneWeekAgo" in names
    else:
        assert "OneWeekAgo" not in names
    if days >= 365:
        assert "OneYearAgo" in names
    else:
        assert "OneYearAgo" not in names
