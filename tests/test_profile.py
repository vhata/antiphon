"""Tests for scripts.profile — username parsing only (no network)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import profile


def test_profile_module_exposes_main_and_get_username() -> None:
    assert hasattr(profile, "main")
    assert hasattr(profile, "get_username")


def test_get_username_parses_well_formed_user_md(tmp_path: Path) -> None:
    user_md = tmp_path / "user.md"
    user_md.write_text("# User\n\n## last.fm\n\n- **Username:** alice\n")
    assert profile.get_username(user_md) == "alice"


def test_get_username_raises_when_file_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="not found"):
        profile.get_username(tmp_path / "nope.md")


def test_get_username_raises_when_no_username_line(tmp_path: Path) -> None:
    user_md = tmp_path / "user.md"
    user_md.write_text("# User\n\nno username here\n")
    with pytest.raises(RuntimeError, match="could not find username"):
        profile.get_username(user_md)
