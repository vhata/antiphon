"""Tests for scripts.chase — URL building + module exposure."""

from __future__ import annotations

from scripts import chase


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
