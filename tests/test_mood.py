"""Tests for scripts.mood — rendering layer (parser tests live in test__moods)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import mood
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
