"""Tests for scripts.populate_mood — pure logic only (no claude CLI invocation)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import populate_mood

SAMPLE_MOODS = """\
# Moods

intro

---

## feisty

*I'm brat and fuck you all*

### Validated

*(none yet)*

### Candidates

*(none yet)*

---

## with-existing

*Some mood with existing picks.*

### Validated

- **Validated Artist — *Album*** — already in.

### Candidates

- **Existing Cand — *Album*** — already a candidate.

---
"""


def test_extract_description() -> None:
    section = "*hello world*\n\nrest of body"
    assert populate_mood._extract_description(section) == "hello world"


def test_extract_description_empty_when_no_italic() -> None:
    assert populate_mood._extract_description("no italic here\n\nbody") == ""


def test_format_picks_handles_empty() -> None:
    assert populate_mood._format_picks([]) == "(none)"


def test_format_picks_emits_bullets() -> None:
    picks = ["**X — *Y*** — why", "**A — *B*** — why2"]
    out = populate_mood._format_picks(picks)
    assert out == "- **X — *Y*** — why\n- **A — *B*** — why2"


def test_parse_response_picks_out_bullets() -> None:
    response = """\
Here are some picks:

- **Charli XCX — *brat* (2024)** — namesake.
- **M.I.A. — *Kala* (2007)** — fuck-you energy.

Hope this helps!
"""
    bullets = populate_mood.parse_response(response)
    assert len(bullets) == 2
    assert "Charli XCX" in bullets[0]
    assert "M.I.A." in bullets[1]


def test_parse_response_handles_continuation_lines() -> None:
    response = """\
- **Long Artist — *Album*** —
  this rationale spans
  multiple lines.
- **Short — *X*** — single line.
"""
    bullets = populate_mood.parse_response(response)
    assert len(bullets) == 2
    assert "spans" in bullets[0]
    assert "multiple lines" in bullets[0]


def test_parse_response_empty_input() -> None:
    assert populate_mood.parse_response("") == []
    assert populate_mood.parse_response("just prose, no bullets") == []


def test_build_prompt_substitutes_fields() -> None:
    prompt = populate_mood.build_prompt(
        name="feisty",
        description="brat",
        shape="(shape stub)",
        validated=[],
        candidates=[],
        n=5,
    )
    assert "**feisty**" in prompt
    assert "brat" in prompt
    assert "(shape stub)" in prompt
    assert "(none)" in prompt
    assert "Propose 5 NEW" in prompt


def test_populate_appends_picks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "moods.md"
    p.write_text(SAMPLE_MOODS)

    fake_claude_response = (
        "- **New Artist 1 — *Album1* (2020)** — first pick.\n"
        "- **New Artist 2 — *Album2* (2021)** — second pick.\n"
    )

    def fake_claude(prompt: str) -> str:
        return fake_claude_response

    # Stub the listening shape so we don't hit the API.
    monkeypatch.setattr(populate_mood, "_profile_summary", lambda _user: "(stub)")
    monkeypatch.setattr(populate_mood, "get_username", lambda: "tester")

    added = populate_mood.populate("feisty", n=2, path=p, claude_caller=fake_claude)
    assert added == 2

    body = p.read_text()
    assert "New Artist 1" in body
    assert "New Artist 2" in body
    # The Candidates placeholder is replaced; the Validated placeholder stays
    # (populate-mood only touches Candidates).
    feisty_section = body[body.find("## feisty") : body.find("## with-existing")]
    cand_section = feisty_section[feisty_section.find("### Candidates") :]
    assert "*(none yet)*" not in cand_section
    val_section = feisty_section[
        feisty_section.find("### Validated") : feisty_section.find("### Candidates")
    ]
    assert "*(none yet)*" in val_section


def test_populate_raises_on_unknown_mood(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "moods.md"
    p.write_text(SAMPLE_MOODS)
    monkeypatch.setattr(populate_mood, "_profile_summary", lambda _user: "(stub)")
    monkeypatch.setattr(populate_mood, "get_username", lambda: "tester")
    with pytest.raises(RuntimeError, match="not found"):
        populate_mood.populate(
            "nonexistent", n=2, path=p, claude_caller=lambda _p: "- **X — *Y*** — z."
        )


def test_populate_raises_when_claude_returns_no_bullets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = tmp_path / "moods.md"
    p.write_text(SAMPLE_MOODS)
    monkeypatch.setattr(populate_mood, "_profile_summary", lambda _user: "(stub)")
    monkeypatch.setattr(populate_mood, "get_username", lambda: "tester")
    with pytest.raises(RuntimeError, match="no parseable bullets"):
        populate_mood.populate(
            "feisty", n=2, path=p, claude_caller=lambda _p: "just prose, no bullets"
        )
