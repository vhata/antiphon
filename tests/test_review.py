"""Tests for scripts.review — categorisation logic."""

from __future__ import annotations

from typing import Any

import pytest

from scripts import review


def _artist(name: str, plays: int, rank: int = 1) -> dict[str, Any]:
    return {"name": name, "playcount": str(plays), "@attr": {"rank": str(rank)}}


def test_review_rejects_unknown_period() -> None:
    with pytest.raises(ValueError, match="unknown period"):
        review.review("vhata", "decade")


def test_review_categorises_newcomers_returners_mid_tier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # overall[:25] becomes the "core" set; MidArtist must sit at index >= 25
    # to fall into mid-tier.
    overall = (
        [_artist("CoreArtist", 5000, 1)]
        + [_artist(f"Filler{i}", 100 - i, i + 2) for i in range(49)]
        + [_artist("MidArtist", 50, 51)]
        + [_artist(f"Trailer{i}", 40 - i, 52 + i) for i in range(49)]
    )

    current = [
        _artist("CoreArtist", 30),
        _artist("MidArtist", 20),
        _artist("BrandNew", 15),
    ]

    def fake_call(method: str, **params: Any) -> Any:
        if params.get("period") == "overall":
            return {"topartists": {"artist": overall}}
        return {"topartists": {"artist": current}}

    monkeypatch.setattr(review, "call", fake_call)
    result = review.review("vhata", "month")

    def names(group: list[dict[str, Any]]) -> list[str]:
        return [a["name"] for a in group]

    assert names(result["returners"]) == ["CoreArtist"]
    assert names(result["mid_tier"]) == ["MidArtist"]
    assert names(result["newcomers"]) == ["BrandNew"]


def test_review_period_map_keys_match_supported_periods() -> None:
    assert set(review.PERIOD_MAP.keys()) == {"week", "month", "quarter", "year"}


def test_review_includes_period_volume(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_call(method: str, **params: Any) -> Any:
        if params.get("period") == "overall":
            return {"topartists": {"artist": [_artist("X", 100, 1)]}}
        return {"topartists": {"artist": [_artist("X", 50), _artist("Y", 30), _artist("Z", 20)]}}

    monkeypatch.setattr(review, "call", fake_call)
    result = review.review("vhata", "month")
    assert result["period_volume"] == 100
