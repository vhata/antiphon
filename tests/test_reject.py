"""Tests for scripts.reject."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import reject

SAMPLE_DISLIKES = """# Dislikes

intro

## Artists

*(none yet)*

## Sub-genres / scenes

*(none yet)*

## Vibes / qualities

- **Existing vibe** — already here. *(2026-05-01)*

## Specific albums

*(none yet)*
"""


def _write_sample(tmp_path: Path) -> Path:
    p = tmp_path / "dislikes.md"
    p.write_text(SAMPLE_DISLIKES)
    return p


def test_reject_replaces_none_yet_placeholder(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    reject.append_rejection("Author & Punisher", "too noisy", path=p, today="2026-05-04")
    body = p.read_text()
    assert "**Author & Punisher** — too noisy. *(2026-05-04)*" in body
    assert "## Artists\n\n- **Author & Punisher**" in body
    # Other sections still hold their placeholder.
    assert "## Sub-genres / scenes\n\n*(none yet)*" in body


def test_reject_appends_when_section_already_has_entries(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    reject.append_rejection("Drop bass", "formulaic", category="Vibes", path=p, today="2026-05-04")
    body = p.read_text()
    assert "**Existing vibe** — already here. *(2026-05-01)*" in body
    assert "**Drop bass** — formulaic. *(2026-05-04)*" in body


def test_reject_category_substring_match(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    reject.append_rejection("Some scene", "boring", category="genres", path=p, today="2026-05-04")
    body = p.read_text()
    assert "## Sub-genres / scenes\n\n- **Some scene**" in body


def test_reject_raises_on_unknown_category(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    with pytest.raises(RuntimeError, match="could not find a category"):
        reject.append_rejection("X", "y", category="nonexistent", path=p)


def test_reject_raises_when_dislikes_md_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="not found"):
        reject.append_rejection("X", "y", path=tmp_path / "missing.md")
