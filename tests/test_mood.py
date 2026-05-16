"""Tests for scripts.mood — rendering layer (parser tests live in test__moods)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import _spotify, mood
from scripts._moods import find_mood_section

SAMPLE = """\
# Moods

---

## small hours

*Middle of the night, want to wind down.*

### Validated

- **Brian Eno — *Music for Airports* (1978)** — canonical.

### Candidates

- **Max Richter — *From Sleep* (2015)** — composed for sleep.
"""


def test_spotify_search_url_encodes_spaces() -> None:
    url = mood.spotify_search_url("Brian Eno Music for Airports")
    assert url.startswith("https://open.spotify.com/search/")
    assert "%20" in url


def test_render_emits_markdown_links_for_each_pick() -> None:
    section = find_mood_section(SAMPLE, "small hours")
    assert section is not None
    output = mood.render("small hours", section)
    assert "# small hours" in output
    assert "## Validated" in output
    assert "## Candidates" in output
    assert "[Brian Eno — Music for Airports](https://open.spotify.com/search/" in output
    assert "[Max Richter — From Sleep](https://open.spotify.com/search/" in output


def test_render_includes_italic_description() -> None:
    section = find_mood_section(SAMPLE, "small hours")
    assert section is not None
    output = mood.render("small hours", section)
    assert "*Middle of the night, want to wind down.*" in output


def test_main_with_no_arg_lists_moods(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    moods_md = tmp_path / "moods.md"
    moods_md.write_text(SAMPLE)
    monkeypatch.setattr(mood, "MOODS_MD", moods_md)

    exit_code = mood.main(None)
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Available moods:" in out
    assert "small hours" in out


def test_main_with_empty_string_lists_moods(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    moods_md = tmp_path / "moods.md"
    moods_md.write_text(SAMPLE)
    monkeypatch.setattr(mood, "MOODS_MD", moods_md)

    exit_code = mood.main("")
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Available moods:" in out


def test_main_with_unknown_mood_returns_2(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    moods_md = tmp_path / "moods.md"
    moods_md.write_text(SAMPLE)
    monkeypatch.setattr(mood, "MOODS_MD", moods_md)

    exit_code = mood.main("nonexistent")
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "not found" in captured.err
    assert "small hours" in captured.err  # available moods listed


# Spotify integration: render uses direct URLs when available, search URLs otherwise.


def test_spotify_url_no_creds_uses_search() -> None:
    url = mood.spotify_url("Brian Eno", "Music for Airports")
    assert url.startswith("https://open.spotify.com/search/")


def test_spotify_url_direct_album_when_creds_and_hit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(_spotify, "search_album", lambda a, b: "https://open.spotify.com/album/aaa")
    assert mood.spotify_url("Brian Eno", "Music for Airports") == (
        "https://open.spotify.com/album/aaa"
    )


def test_spotify_url_direct_artist_when_no_album(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(_spotify, "search_album", lambda *a, **kw: pytest.fail("no album"))
    monkeypatch.setattr(_spotify, "search_artist", lambda a: "https://open.spotify.com/artist/bbb")
    assert mood.spotify_url("Brian Eno") == "https://open.spotify.com/artist/bbb"


def test_spotify_url_falls_back_when_creds_present_but_miss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(_spotify, "search_album", lambda a, b: None)
    monkeypatch.setattr(_spotify, "search_artist", lambda a: None)
    assert mood.spotify_url("Brian Eno", "Music for Airports").startswith(
        "https://open.spotify.com/search/"
    )
    assert mood.spotify_url("Brian Eno").startswith("https://open.spotify.com/search/")


def test_render_uses_direct_urls_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(
        _spotify,
        "search_album",
        lambda artist, album: f"https://open.spotify.com/album/{artist.replace(' ', '')}",
    )
    section = find_mood_section(SAMPLE, "small hours")
    assert section is not None
    output = mood.render("small hours", section)
    assert "https://open.spotify.com/album/BrianEno" in output
    assert "https://open.spotify.com/album/MaxRichter" in output
    assert "open.spotify.com/search" not in output
