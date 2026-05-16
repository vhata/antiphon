"""Tests for scripts.rut — rut-detection logic."""

from __future__ import annotations

from typing import Any

import pytest

from scripts import rut


def _fake_recent(*artist_runs: tuple[str, int]) -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = []
    for artist, count in artist_runs:
        for _ in range(count):
            tracks.append({"artist": {"#text": artist}, "name": "track"})
    return tracks


def test_detect_rut_no_scrobbles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rut, "get_scrobbles", lambda *a, **kw: _fake_recent())
    result = rut.detect_rut("tester")
    assert result["in_rut"] is False
    assert result["total_scrobbles"] == 0


def test_detect_rut_sample_too_small(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rut, "get_scrobbles", lambda *a, **kw: _fake_recent(("Solo Artist", 10)))
    result = rut.detect_rut("tester")
    assert result["in_rut"] is False
    assert "too small" in result["reason"]


def test_detect_rut_flags_dominant_top1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        rut,
        "get_scrobbles",
        lambda *a, **kw: _fake_recent(("Massive Attack", 60), ("Other", 40)),
    )
    result = rut.detect_rut("tester")
    assert result["in_rut"] is True
    assert "Massive Attack" in result["reason"]


def test_detect_rut_flags_dominant_top2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        rut,
        "get_scrobbles",
        lambda *a, **kw: _fake_recent(("First", 35), ("Second", 35), ("Third", 30)),
    )
    result = rut.detect_rut("tester")
    assert result["in_rut"] is True
    assert "top 2" in result["reason"]


def test_detect_rut_no_flag_for_balanced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        rut,
        "get_scrobbles",
        lambda *a, **kw: _fake_recent(("A", 25), ("B", 25), ("C", 25), ("D", 25)),
    )
    result = rut.detect_rut("tester")
    assert result["in_rut"] is False


def test_thresholds_and_min_constants() -> None:
    assert rut.DEFAULT_DAYS == 14
    assert rut.TOP_1_THRESHOLD == 0.40
    assert rut.TOP_2_THRESHOLD == 0.60
    assert rut.MIN_SCROBBLES == 30
