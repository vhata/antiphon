"""Tests for scripts.validate."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import validate

SAMPLE_MOODS = """# Moods

intro

---

## small hours

*Middle of the night.*

### Validated

- **Brian Eno — *Music for Airports*** — canonical.

### Candidates

- **Max Richter — *From Sleep*** — composed for sleep.
- **Stars of the Lid — *Refinement*** — drone.
- **Nils Frahm — *Spaces*** — piano.

---

## deep work

*Focused coding.*

### Validated

*(none yet)*

### Candidates

- **Tycho — *Dive*** — instrumental.

---
"""


def _write_sample(tmp_path: Path) -> Path:
    p = tmp_path / "moods.md"
    p.write_text(SAMPLE_MOODS)
    return p


def _section_between(body: str, start_marker: str, end_marker: str) -> str:
    start = body.find(start_marker)
    end = body.find(end_marker, start + len(start_marker))
    if end == -1:
        return body[start:]
    return body[start:end]


def test_promote_moves_bullet_from_candidates_to_validated(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    validate.promote("small hours", "Stars of the Lid", path=p, today="2026-05-04")
    body = p.read_text()

    val = _section_between(body, "## small hours", "### Candidates")
    cand = _section_between(body, "### Candidates", "## deep work")

    assert "Stars of the Lid" in val
    assert "Stars of the Lid" not in cand
    assert "Validated 2026-05-04" in val


def test_promote_replaces_none_yet_in_validated(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    validate.promote("deep work", "Tycho", path=p, today="2026-05-04")
    body = p.read_text()

    val = _section_between(body, "## deep work", "### Candidates")
    assert "*(none yet)*" not in val
    assert "Tycho" in val


def test_promote_leaves_none_yet_when_candidates_empty(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    # deep work has only one candidate; after promotion the section is empty.
    validate.promote("deep work", "Tycho", path=p, today="2026-05-04")
    body = p.read_text()
    cand = body[body.find("## deep work") :]
    cand_section = cand[cand.find("### Candidates") :]
    assert "*(none yet)*" in cand_section


def test_promote_raises_on_unknown_mood(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    with pytest.raises(RuntimeError, match="not found"):
        validate.promote("nonexistent", "anything", path=p)


def test_promote_raises_on_unknown_pick(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    with pytest.raises(RuntimeError, match="not found in candidates"):
        validate.promote("small hours", "Aphex Twin", path=p)


def test_promote_case_insensitive_pick_match(tmp_path: Path) -> None:
    p = _write_sample(tmp_path)
    validate.promote("small hours", "stars of the lid", path=p, today="2026-05-04")
    body = p.read_text()
    val = _section_between(body, "## small hours", "### Candidates")
    cand = _section_between(body, "### Candidates", "## deep work")
    assert "Stars of the Lid" in val
    assert "Stars of the Lid" not in cand
