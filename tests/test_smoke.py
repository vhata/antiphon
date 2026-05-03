"""Smoke tests — no network, no environment setup required."""

from __future__ import annotations

import pytest

from scripts import _lastfm


def test_lastfm_module_imports() -> None:
    assert hasattr(_lastfm, "call")
    assert _lastfm.API_BASE.startswith("https://")


def test_api_key_raises_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LASTFM_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="LASTFM_API_KEY"):
        _lastfm._api_key()
