"""Tests for scripts.forgotten_gems — pure-data logic, no network."""

from __future__ import annotations

from typing import Any

import pytest

from scripts import forgotten_gems


def test_module_exposes_main_and_find_dormant() -> None:
    assert hasattr(forgotten_gems, "main")
    assert hasattr(forgotten_gems, "find_dormant")


def test_default_n_is_15() -> None:
    assert forgotten_gems.DEFAULT_N == 15


def test_find_dormant_filters_by_rank_and_recency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Returns overall-top-100-500 artists not in the 12-month top."""

    def fake_call(method: str, **params: object) -> dict[str, Any]:
        period = params.get("period")
        if period == "overall":
            return {
                "topartists": {
                    "artist": [
                        {
                            "@attr": {"rank": "50"},
                            "playcount": "1000",
                            "name": "TooHigh",
                        },
                        {
                            "@attr": {"rank": "100"},
                            "playcount": "500",
                            "name": "InBand",
                        },
                        {
                            "@attr": {"rank": "150"},
                            "playcount": "300",
                            "name": "Recent",
                        },
                        {
                            "@attr": {"rank": "501"},
                            "playcount": "20",
                            "name": "TooLow",
                        },
                    ]
                }
            }
        if period == "12month":
            return {"topartists": {"artist": [{"name": "Recent"}]}}
        raise AssertionError(f"unexpected period: {period!r}")

    monkeypatch.setattr(forgotten_gems, "call", fake_call)
    dormant = forgotten_gems.find_dormant("anyone")
    names = {row[2] for row in dormant}
    assert names == {"InBand"}
