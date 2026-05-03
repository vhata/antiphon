"""Tests for scripts.add_mood."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import add_mood

SAMPLE = """# Moods

intro

---

## small hours

*Middle of the night.*

### Validated

*(none yet)*

### Candidates

*(none yet)*

---

## Adding a new mood

ignore.
"""


def _write(tmp_path: Path) -> Path:
    p = tmp_path / "moods.md"
    p.write_text(SAMPLE)
    return p


def test_add_inserts_new_mood_before_meta(tmp_path: Path) -> None:
    p = _write(tmp_path)
    add_mood.add("deep work", "Focused coding.", path=p)
    body = p.read_text()

    assert "## deep work" in body
    assert "*Focused coding.*" in body

    new_idx = body.find("## deep work")
    meta_idx = body.find("## Adding a new mood")
    small_idx = body.find("## small hours")

    assert small_idx < new_idx < meta_idx
    new_section = body[new_idx:meta_idx]
    assert "### Validated" in new_section
    assert "### Candidates" in new_section
    assert "*(none yet)*" in new_section


def test_add_uses_placeholder_description_when_omitted(tmp_path: Path) -> None:
    p = _write(tmp_path)
    add_mood.add("commute", path=p)
    body = p.read_text()
    assert "## commute" in body
    assert f"*{add_mood.DEFAULT_DESC}*" in body


def test_add_refuses_duplicate_mood(tmp_path: Path) -> None:
    p = _write(tmp_path)
    with pytest.raises(RuntimeError, match="already exists"):
        add_mood.add("small hours", "dup", path=p)


def test_add_refuses_duplicate_case_insensitive(tmp_path: Path) -> None:
    p = _write(tmp_path)
    with pytest.raises(RuntimeError, match="already exists"):
        add_mood.add("Small Hours", "dup", path=p)


def test_add_refuses_when_moods_md_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="not found"):
        add_mood.add("X", path=tmp_path / "missing.md")
