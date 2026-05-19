"""Tests for scripts._lastfm — request timeout and env-loading."""

from __future__ import annotations

import io
import json
import urllib.request
from typing import Any

import pytest

from scripts import _lastfm


class _FakeResponse:
    """Minimal stand-in for `urllib.request.urlopen`'s context-manager result."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return io.BytesIO(json.dumps(self._payload).encode("utf-8")).read()


def test_call_passes_request_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every call() must pass `REQUEST_TIMEOUT_SECONDS` to urlopen."""
    captured: dict[str, Any] = {}

    def fake_urlopen(url: str, **kwargs: Any) -> _FakeResponse:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return _FakeResponse({"ok": True})

    monkeypatch.setenv("LASTFM_API_KEY", "test-key")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = _lastfm.call("user.getRecentTracks", user="alice", limit=10)

    assert result == {"ok": True}
    assert captured["kwargs"].get("timeout") == _lastfm.REQUEST_TIMEOUT_SECONDS
    assert "user.getRecentTracks" in captured["url"]
    assert "user=alice" in captured["url"]


def test_request_timeout_is_a_positive_finite_number() -> None:
    """Sanity check on the constant — must be a positive finite float."""
    assert _lastfm.REQUEST_TIMEOUT_SECONDS > 0
    assert _lastfm.REQUEST_TIMEOUT_SECONDS < 600  # not allowed to be 'forever-ish'


def test_load_env_file_skips_when_var_already_set(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    """An env-var already in the environment is preserved (file is not read)."""
    env = tmp_path / ".env"
    env.write_text("LASTFM_API_KEY=from-file\n")
    monkeypatch.setattr(_lastfm, "ENV_PATH", env)
    monkeypatch.setenv("LASTFM_API_KEY", "from-env")
    _lastfm._load_env_file()
    import os

    assert os.environ["LASTFM_API_KEY"] == "from-env"
