"""Tests for scripts.add_candidate."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import add_candidate

SAMPLE_MOODS = """\
# Moods

intro

---

## empty

*Empty mood.*

### Validated

*(none yet)*

### Candidates

*(none yet)*

---

## populated

*Mood with picks.*

### Validated

*(none yet)*

### Candidates

- **Existing — *Album*** — already there.

---
"""


def _write(tmp_path: Path) -> Path:
    p = tmp_path / "moods.md"
    p.write_text(SAMPLE_MOODS)
    return p


def test_format_bullet_full() -> None:
    out = add_candidate.format_bullet("Charli XCX", "brat", "2024", "namesake")
    assert out == "- **Charli XCX — *brat* (2024)** — namesake."


def test_format_bullet_no_year() -> None:
    out = add_candidate.format_bullet("X", "Y", "", "z")
    assert out == "- **X — *Y*** — z."


def test_format_bullet_no_why() -> None:
    out = add_candidate.format_bullet("X", "Y", "2020")
    assert out == "- **X — *Y* (2020)**"


def test_format_bullet_strips_trailing_period_in_why() -> None:
    out = add_candidate.format_bullet("X", "Y", "", "rationale.")
    assert out == "- **X — *Y*** — rationale."


def test_add_candidate_replaces_none_yet(tmp_path: Path) -> None:
    p = _write(tmp_path)
    add_candidate.add_candidate("empty", "Artist", "Album", "2024", "why", path=p)
    body = p.read_text()
    sec = body[body.find("## empty") : body.find("## populated")]
    assert "*(none yet)*" not in sec[sec.find("### Candidates") :]
    assert "**Artist — *Album* (2024)** — why." in body


def test_add_candidate_appends_to_existing(tmp_path: Path) -> None:
    p = _write(tmp_path)
    add_candidate.add_candidate("populated", "New", "NewAlbum", "", "fresh", path=p)
    body = p.read_text()
    assert "**Existing — *Album***" in body
    assert "**New — *NewAlbum*** — fresh." in body


def test_add_candidate_raises_on_unknown_mood(tmp_path: Path) -> None:
    p = _write(tmp_path)
    with pytest.raises(RuntimeError, match="not found"):
        add_candidate.add_candidate("nonexistent", "A", "B", path=p)


def test_add_candidate_raises_when_moods_md_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="not found"):
        add_candidate.add_candidate("any", "A", "B", path=tmp_path / "missing.md")
