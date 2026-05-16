"""Tests for scripts._spotify — token cache + search helpers, all mocked."""

from __future__ import annotations

import io
import json
import urllib.request
from typing import Any
from urllib.error import HTTPError

import pytest

from scripts import _spotify

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _reset_module_state() -> None:
    """Wipe in-process token cache between tests."""
    _spotify._token_cache = None


def _set_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id-xyz")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret-xyz")


def _unset_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    # Stop the _load_env_file fallback from clobbering the test environment.
    monkeypatch.setattr(_spotify, "_load_env_file", lambda: None)


class _FakeHTTPResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode()

    def __enter__(self) -> _FakeHTTPResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class _Recorder:
    """Stand-in for urllib.request.urlopen that records every request."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = list(responses)
        self.calls: list[Any] = []

    def __call__(self, request: Any, *_args: Any, **_kw: Any) -> _FakeHTTPResponse:
        self.calls.append(request)
        if not self._responses:
            raise AssertionError("urlopen called more times than the test set up")
        return _FakeHTTPResponse(self._responses.pop(0))


def _install_urlopen(monkeypatch: pytest.MonkeyPatch, recorder: _Recorder) -> _Recorder:
    """Patch urlopen in the stdlib module the production code imports from."""
    monkeypatch.setattr(urllib.request, "urlopen", recorder)
    return recorder


# ---------------------------------------------------------------------------
# is_available
# ---------------------------------------------------------------------------


def test_is_available_false_when_no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _unset_creds(monkeypatch)
    assert _spotify.is_available() is False


def test_is_available_false_with_only_id(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _unset_creds(monkeypatch)
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "only-id")
    monkeypatch.setattr(_spotify, "_load_env_file", lambda: None)
    assert _spotify.is_available() is False


def test_is_available_false_with_blank_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _unset_creds(monkeypatch)
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "")
    monkeypatch.setattr(_spotify, "_load_env_file", lambda: None)
    assert _spotify.is_available() is False


def test_is_available_true_with_both(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    assert _spotify.is_available() is True


# ---------------------------------------------------------------------------
# token acquisition + caching
# ---------------------------------------------------------------------------


def test_get_token_fetches_and_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    recorder = _install_urlopen(
        monkeypatch, _Recorder([{"access_token": "tok-1", "expires_in": 3600}])
    )

    t1 = _spotify._get_token()
    t2 = _spotify._get_token()

    assert t1 == "tok-1"
    assert t2 == "tok-1"
    # Single token call despite two requests.
    assert len(recorder.calls) == 1

    # The single request goes to the token endpoint with basic auth + grant_type body.
    request = recorder.calls[0]
    assert request.full_url == "https://accounts.spotify.com/api/token"
    auth_header = request.get_header("Authorization") or request.get_header("Authorization".lower())
    assert auth_header is not None
    assert auth_header.startswith("Basic ")
    body = request.data
    assert isinstance(body, bytes)
    assert b"grant_type=client_credentials" in body


def test_get_token_refetches_when_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    recorder = _install_urlopen(
        monkeypatch,
        _Recorder(
            [
                {"access_token": "tok-1", "expires_in": 60},
                {"access_token": "tok-2", "expires_in": 60},
            ]
        ),
    )

    fake_now = [1_000_000.0]
    # Patch the time module the production code imported.
    import time as _time

    monkeypatch.setattr(_time, "time", lambda: fake_now[0])

    assert _spotify._get_token() == "tok-1"
    # Jump past the cached token's expiry (with the safety skew).
    fake_now[0] += 10_000
    assert _spotify._get_token() == "tok-2"
    assert len(recorder.calls) == 2


def test_get_token_returns_none_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)

    def boom(*_a: Any, **_kw: Any) -> _FakeHTTPResponse:
        raise HTTPError(
            url="https://accounts.spotify.com/api/token",
            code=400,
            msg="bad creds",
            hdrs=None,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert _spotify._get_token() is None


def test_get_token_returns_none_when_missing_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _unset_creds(monkeypatch)
    assert _spotify._get_token() is None


# ---------------------------------------------------------------------------
# search helpers
# ---------------------------------------------------------------------------


def _stub_token(monkeypatch: pytest.MonkeyPatch, value: str | None = "tok-test") -> None:
    monkeypatch.setattr(_spotify, "_get_token", lambda: value)


def test_search_track_returns_direct_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch)

    payload = {
        "tracks": {
            "items": [
                {
                    "id": "abc123",
                    "name": "Teardrop",
                    "artists": [{"name": "Massive Attack"}],
                    "external_urls": {"spotify": "https://open.spotify.com/track/abc123"},
                }
            ]
        }
    }
    recorder = _install_urlopen(monkeypatch, _Recorder([payload]))

    url = _spotify.search_track("Massive Attack", "Teardrop")
    assert url == "https://open.spotify.com/track/abc123"

    # The search request carries the Authorization header.
    request = recorder.calls[0]
    auth_header = request.get_header("Authorization")
    assert auth_header == "Bearer tok-test"
    assert "type=track" in request.full_url
    # urlencode uses `+` for spaces in query strings; Spotify treats both as space.
    assert "Massive+Attack" in request.full_url or "Massive%20Attack" in request.full_url
    assert "Teardrop" in request.full_url


def test_search_track_returns_none_on_empty_items(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch)
    _install_urlopen(monkeypatch, _Recorder([{"tracks": {"items": []}}]))

    assert _spotify.search_track("Nobody", "Nothing") is None


def test_search_track_returns_none_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _unset_creds(monkeypatch)
    assert _spotify.search_track("Whoever", "Whatever") is None


def test_search_track_returns_none_when_token_fetch_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch, value=None)
    assert _spotify.search_track("Massive Attack", "Teardrop") is None


def test_search_album_returns_direct_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch)
    payload = {
        "albums": {
            "items": [
                {
                    "id": "album-1",
                    "name": "Music for Airports",
                    "artists": [{"name": "Brian Eno"}],
                    "external_urls": {"spotify": "https://open.spotify.com/album/album-1"},
                }
            ]
        }
    }
    _install_urlopen(monkeypatch, _Recorder([payload]))
    assert _spotify.search_album("Brian Eno", "Music for Airports") == (
        "https://open.spotify.com/album/album-1"
    )


def test_search_album_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch)
    _install_urlopen(monkeypatch, _Recorder([{"albums": {"items": []}}]))
    assert _spotify.search_album("Brian Eno", "Nonexistent Album") is None


def test_search_artist_returns_direct_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch)
    payload = {
        "artists": {
            "items": [
                {
                    "id": "artist-1",
                    "name": "Brian Eno",
                    "external_urls": {"spotify": "https://open.spotify.com/artist/artist-1"},
                }
            ]
        }
    }
    _install_urlopen(monkeypatch, _Recorder([payload]))
    assert _spotify.search_artist("Brian Eno") == "https://open.spotify.com/artist/artist-1"


def test_search_artist_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch)
    _install_urlopen(monkeypatch, _Recorder([{"artists": {"items": []}}]))
    assert _spotify.search_artist("No Such Artist") is None


def test_search_falls_back_to_none_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_module_state()
    _set_creds(monkeypatch)
    _stub_token(monkeypatch)

    def boom(*_a: Any, **_kw: Any) -> _FakeHTTPResponse:
        raise HTTPError(
            url="https://api.spotify.com/v1/search",
            code=429,
            msg="rate limited",
            hdrs=None,  # type: ignore[arg-type]
            fp=io.BytesIO(b""),
        )

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert _spotify.search_track("Massive Attack", "Teardrop") is None


def test_module_exposes_public_api() -> None:
    assert hasattr(_spotify, "is_available")
    assert hasattr(_spotify, "search_artist")
    assert hasattr(_spotify, "search_album")
    assert hasattr(_spotify, "search_track")
