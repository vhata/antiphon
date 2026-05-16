"""Tests for scripts.chase — URL building + module exposure."""

from __future__ import annotations

import pytest

from scripts import _spotify, chase


def test_spotify_url_with_track_encodes_spaces() -> None:
    url = chase.spotify_url("Massive Attack", "Teardrop")
    assert url.startswith("https://open.spotify.com/search/")
    assert "Massive%20Attack%20Teardrop" in url


def test_spotify_url_artist_only_when_no_track() -> None:
    url = chase.spotify_url("Massive Attack")
    assert url.endswith("Massive%20Attack")


def test_spotify_url_strips_extra_whitespace() -> None:
    url = chase.spotify_url("Massive Attack", "")
    assert url.endswith("Massive%20Attack")
    assert "%20%20" not in url


def test_module_exposes_main_and_helpers() -> None:
    assert hasattr(chase, "main")
    assert hasattr(chase, "latest_track")
    assert hasattr(chase, "similar_tracks")
    assert hasattr(chase, "similar_artists")


# Spotify integration branches.


def test_spotify_url_no_creds_uses_search() -> None:
    url = chase.spotify_url("Massive Attack", "Teardrop")
    assert url.startswith("https://open.spotify.com/search/")


def test_spotify_url_direct_track_when_creds_and_hit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(_spotify, "search_track", lambda a, t: "https://open.spotify.com/track/aaa")
    assert chase.spotify_url("Massive Attack", "Teardrop") == ("https://open.spotify.com/track/aaa")


def test_spotify_url_direct_artist_when_no_track(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    # search_track must not be called when track is empty.
    monkeypatch.setattr(_spotify, "search_track", lambda *a, **kw: pytest.fail("should not call"))
    monkeypatch.setattr(_spotify, "search_artist", lambda a: "https://open.spotify.com/artist/bbb")
    assert chase.spotify_url("Massive Attack") == "https://open.spotify.com/artist/bbb"


def test_spotify_url_falls_back_when_creds_present_but_miss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(_spotify, "search_track", lambda a, t: None)
    monkeypatch.setattr(_spotify, "search_artist", lambda a: None)
    assert chase.spotify_url("Massive Attack", "Teardrop").startswith(
        "https://open.spotify.com/search/"
    )
    assert chase.spotify_url("Massive Attack").startswith("https://open.spotify.com/search/")
