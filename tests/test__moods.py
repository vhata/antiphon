"""Tests for scripts._moods — the shared moods.md parser/mutator."""

from __future__ import annotations

from scripts import _moods

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


def test_find_mood_section_returns_body() -> None:
    body = _moods.find_mood_section(SAMPLE, "small hours")
    assert body is not None
    assert "Middle of the night" in body
    assert "Brian Eno" in body
    assert "deep work" not in body


def test_find_mood_section_case_insensitive() -> None:
    assert _moods.find_mood_section(SAMPLE, "Small Hours") is not None
    assert _moods.find_mood_section(SAMPLE, "SMALL HOURS") is not None


def test_find_mood_section_returns_none_for_missing() -> None:
    assert _moods.find_mood_section(SAMPLE, "no such mood") is None


def test_picks_in_validated() -> None:
    section = _moods.find_mood_section(SAMPLE, "small hours")
    assert section is not None
    picks = _moods.picks_in(section, "Validated")
    assert len(picks) == 1
    assert "Brian Eno" in picks[0]


def test_picks_in_candidates_joins_continuation_lines() -> None:
    section = _moods.find_mood_section(SAMPLE, "small hours")
    assert section is not None
    picks = _moods.picks_in(section, "Candidates")
    assert len(picks) == 2
    assert "Stars of the Lid" in picks[1]
    assert "glacial drone" in picks[1]


def test_picks_in_skips_none_yet() -> None:
    section = _moods.find_mood_section(SAMPLE, "deep work")
    assert section is not None
    assert _moods.picks_in(section, "Validated") == []


def test_parse_pick_simple_album() -> None:
    artist, album = _moods.parse_pick("**Brian Eno — *Music for Airports* (1978)** — canonical.")
    assert artist == "Brian Eno"
    assert album == "Music for Airports"


def test_parse_pick_multi_album_returns_first() -> None:
    artist, album = _moods.parse_pick("**Tycho — *Dive* (2011) / *Awake* (2014)** — instrumental.")
    assert artist == "Tycho"
    assert album == "Dive"


def test_list_moods_excludes_meta() -> None:
    moods = _moods.list_moods(SAMPLE)
    assert "small hours" in moods
    assert "deep work" in moods
    assert "Adding a new mood" not in moods


def test_mood_exists() -> None:
    assert _moods.mood_exists(SAMPLE, "small hours")
    assert _moods.mood_exists(SAMPLE, "Small Hours")
    assert not _moods.mood_exists(SAMPLE, "nonexistent")


def test_replace_subsection_body_modifies_only_target_subsection() -> None:
    section = _moods.find_mood_section(SAMPLE, "small hours")
    assert section is not None
    new_section = _moods.replace_subsection_body(section, "Candidates", "*(empty)*\n")
    assert "*(empty)*" in new_section
    assert "Brian Eno" in new_section  # Validated untouched
    assert "Max Richter" not in new_section  # old Candidates body gone


def test_append_mood_section_inserts_before_meta() -> None:
    scaffold = (
        "## new mood\n\n*test description.*\n\n"
        "### Validated\n\n*(none yet)*\n\n"
        "### Candidates\n\n*(none yet)*"
    )
    result = _moods.append_mood_section(SAMPLE, scaffold)
    assert "## new mood" in result
    # New mood appears before the meta section
    new_idx = result.find("## new mood")
    meta_idx = result.find("## Adding a new mood")
    assert new_idx < meta_idx
    # And after the existing moods
    deep_idx = result.find("## deep work")
    assert deep_idx < new_idx
