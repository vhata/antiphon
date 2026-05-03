"""Tests for scripts.stats — pure-arithmetic helpers."""

from __future__ import annotations

from scripts import stats


def test_pct_basic() -> None:
    assert stats.pct(50, 200) == 25.0


def test_pct_zero_denominator_returns_zero() -> None:
    assert stats.pct(50, 0) == 0.0


def test_module_exposes_main() -> None:
    assert hasattr(stats, "main")
