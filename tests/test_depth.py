"""Tests for scripts.depth — module-level smoke."""

from __future__ import annotations

from scripts import depth


def test_module_exposes_main_and_helpers() -> None:
    assert hasattr(depth, "main")
    assert hasattr(depth, "artist_top_albums")
    assert hasattr(depth, "user_albums_for_artist")


def test_default_user_depth_is_1000() -> None:
    assert depth.DEFAULT_USER_DEPTH == 1000
