"""Tests for scripts._dislikes — shared dislikes.md helpers."""

from __future__ import annotations

from scripts import _dislikes

SAMPLE = """# Dislikes

intro

## Artists

*(none yet)*

## Sub-genres / scenes

- **Some scene** — boring. *(2026-05-01)*

## Vibes / qualities

*(none yet)*
"""


def test_find_category_exact() -> None:
    info = _dislikes.find_category(SAMPLE, "Artists")
    assert info is not None
    heading, body, start, end = info
    assert heading == "## Artists"
    assert "*(none yet)*" in body
    assert SAMPLE[start:end].startswith("## Artists")


def test_find_category_substring_match() -> None:
    info = _dislikes.find_category(SAMPLE, "genres")
    assert info is not None
    heading, _, _, _ = info
    assert heading == "## Sub-genres / scenes"


def test_find_category_returns_none_for_missing() -> None:
    assert _dislikes.find_category(SAMPLE, "nonexistent") is None


def test_list_categories() -> None:
    cats = _dislikes.list_categories(SAMPLE)
    assert "Artists" in cats
    assert "Sub-genres / scenes" in cats
    assert "Vibes / qualities" in cats
