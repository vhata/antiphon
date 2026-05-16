"""Shared test setup.

Antiphon's tests must never hit a real network. The Spotify integration
is opt-in via env vars; some tests run in a developer environment that
*does* have those vars set, which would otherwise let the search-URL
fallback path silently call the live Spotify API. Strip them at session
scope and prevent the `.env` loader from putting them back.
"""

from __future__ import annotations

import pytest

from scripts import _spotify


@pytest.fixture(autouse=True)
def _isolate_spotify_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Block live Spotify access during tests unless a test opts back in."""
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    monkeypatch.setattr(_spotify, "_load_env_file", lambda: None)
    _spotify._token_cache = None
