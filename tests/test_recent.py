"""Tests for scripts.recent — module-level smoke."""

from __future__ import annotations

from scripts import recent


def test_module_exposes_main_and_constants() -> None:
    assert hasattr(recent, "main")
    assert recent.DEFAULT_DAYS == 7
