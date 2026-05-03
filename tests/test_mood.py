"""Tests for scripts.mood — parsing and rendering, no filesystem dependency."""

from __future__ import annotations

from scripts import mood

SAMPLE = """\
# Moods

intro paragraph

---

## small hours

*Middle of the night, want to wind down.*

Picks should: be long-form.

### Validated

- **Brian Eno — *Music for Airports* (1978)** — canonical.

### Candidates

- **Max Richter — *From Sleep* (2015)** — composed for sleep.
- **Stars of the Lid — *And Their Refinement of the Decline* (2007)** —
  glacial drone, no hooks, no surprises.

---

## deep work

*Focused coding.*

### Validated

*(none yet)*

### Candidates

- **Tycho — *Dive* (2011) / *Awake* (2014)** — instrumental electronic.

---

## Adding a new mood

ignore this section.
"""


def test_find_section_returns_body() -> None:
    section = mood.find_section(SAMPLE, "small hours")
    assert section is not None
    assert "Middle of the night" in section
    assert "Brian Eno" in section
    assert "deep work" not in section
    assert "Adding a new mood" not in section


def test_find_section_case_insensitive() -> None:
    assert mood.find_section(SAMPLE, "Small Hours") is not None
    assert mood.find_section(SAMPLE, "SMALL HOURS") is not None


def test_find_section_returns_none_for_missing() -> None:
    assert mood.find_section(SAMPLE, "no such mood") is None


def test_extract_picks_validated() -> None:
    section = mood.find_section(SAMPLE, "small hours")
    assert section is not None
    picks = mood.extract_picks(section, "Validated")
    assert len(picks) == 1
    assert "Brian Eno" in picks[0]


def test_extract_picks_candidates_joins_continuation_lines() -> None:
    section = mood.find_section(SAMPLE, "small hours")
    assert section is not None
    picks = mood.extract_picks(section, "Candidates")
    assert len(picks) == 2
    assert "Stars of the Lid" in picks[1]
    assert "glacial drone" in picks[1]  # continuation line joined


def test_extract_picks_skips_none_yet() -> None:
    section = mood.find_section(SAMPLE, "deep work")
    assert section is not None
    assert mood.extract_picks(section, "Validated") == []


def test_parse_pick_simple_album() -> None:
    artist, album = mood.parse_pick("**Brian Eno — *Music for Airports* (1978)** — canonical.")
    assert artist == "Brian Eno"
    assert album == "Music for Airports"


def test_parse_pick_multi_album_returns_first() -> None:
    artist, album = mood.parse_pick("**Tycho — *Dive* (2011) / *Awake* (2014)** — instrumental.")
    assert artist == "Tycho"
    assert album == "Dive"


def test_spotify_search_url_encodes_spaces() -> None:
    url = mood.spotify_search_url("Brian Eno Music for Airports")
    assert url.startswith("https://open.spotify.com/search/")
    assert "%20" in url


def test_render_emits_markdown_links() -> None:
    section = mood.find_section(SAMPLE, "small hours")
    assert section is not None
    output = mood.render("small hours", section)
    assert "# small hours" in output
    assert "## Validated" in output
    assert "## Candidates" in output
    assert "[Brian Eno — Music for Airports](https://open.spotify.com/search/" in output


def test_list_moods_excludes_meta() -> None:
    moods = mood.list_moods(SAMPLE)
    assert "small hours" in moods
    assert "deep work" in moods
    assert "Adding a new mood" not in moods
