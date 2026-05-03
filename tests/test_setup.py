"""Tests for scripts.setup — non-interactive (input is injected)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from pathlib import Path

import pytest

from scripts import setup


@pytest.fixture
def tmp_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A tmp dir that mimics the repo: example files + patched path constants."""
    (tmp_path / "user.example.md").write_text(
        "# User\n\n## last.fm\n\n- **Username:** *(your last.fm username)*\n"
    )
    (tmp_path / ".env.example").write_text("# Get a free key at https://example\nLASTFM_API_KEY=\n")
    (tmp_path / "moods.example.md").write_text("# Moods\n\n[template content]\n")
    (tmp_path / "dislikes.example.md").write_text("# Dislikes\n\n[template content]\n")

    monkeypatch.setattr(setup, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(setup, "USER_MD", tmp_path / "user.md")
    monkeypatch.setattr(setup, "USER_EXAMPLE", tmp_path / "user.example.md")
    monkeypatch.setattr(setup, "ENV", tmp_path / ".env")
    monkeypatch.setattr(setup, "ENV_EXAMPLE", tmp_path / ".env.example")
    monkeypatch.setattr(setup, "MOODS", tmp_path / "moods.md")
    monkeypatch.setattr(setup, "MOODS_EXAMPLE", tmp_path / "moods.example.md")
    monkeypatch.setattr(setup, "DISLIKES", tmp_path / "dislikes.md")
    monkeypatch.setattr(setup, "DISLIKES_EXAMPLE", tmp_path / "dislikes.example.md")

    return tmp_path


def scripted_input(responses: Iterable[str]) -> Callable[[str], str]:
    """Return a fake `input()` that yields each response in order."""
    iterator: Iterator[str] = iter(responses)

    def fake(_prompt: str = "") -> str:
        return next(iterator)

    return fake


def test_full_run_writes_all_four_files(tmp_repo: Path) -> None:
    setup.main(prompt_for=scripted_input(["vhata", "test-key-123"]))

    user_md = (tmp_repo / "user.md").read_text()
    assert "**Username:** vhata" in user_md
    assert "*(your last.fm username)*" not in user_md

    env_text = (tmp_repo / ".env").read_text()
    assert "LASTFM_API_KEY=test-key-123" in env_text

    assert (tmp_repo / "moods.md").read_text() == "# Moods\n\n[template content]\n"
    assert (tmp_repo / "dislikes.md").read_text() == "# Dislikes\n\n[template content]\n"


def test_re_run_is_idempotent(tmp_repo: Path) -> None:
    setup.main(prompt_for=scripted_input(["vhata", "test-key-123"]))
    user_before = (tmp_repo / "user.md").read_text()
    env_before = (tmp_repo / ".env").read_text()

    # Second run requires no inputs — nothing needs prompting.
    setup.main(prompt_for=scripted_input([]))

    assert (tmp_repo / "user.md").read_text() == user_before
    assert (tmp_repo / ".env").read_text() == env_before


def test_skips_user_md_when_already_configured(tmp_repo: Path) -> None:
    (tmp_repo / "user.md").write_text("# User\n\n- **Username:** alice\n")
    setup.main(prompt_for=scripted_input(["test-key-123"]))
    assert "Username:** alice" in (tmp_repo / "user.md").read_text()


def test_skips_env_when_key_already_present(tmp_repo: Path) -> None:
    (tmp_repo / ".env").write_text("LASTFM_API_KEY=existing-key\n")
    setup.main(prompt_for=scripted_input(["vhata"]))
    assert "LASTFM_API_KEY=existing-key" in (tmp_repo / ".env").read_text()


def test_skips_moods_md_when_present(tmp_repo: Path) -> None:
    (tmp_repo / "moods.md").write_text("# my moods\n\nhand-edited\n")
    setup.main(prompt_for=scripted_input(["vhata", "test-key-123"]))
    assert (tmp_repo / "moods.md").read_text() == "# my moods\n\nhand-edited\n"


def test_has_username_detects_placeholder() -> None:
    assert not setup.has_username("- **Username:** *(your last.fm username)*")
    assert setup.has_username("- **Username:** vhata")
    assert setup.has_username("- **last.fm username:** vhata")
    assert not setup.has_username("no username here")


def test_has_api_key_detects_empty_or_missing() -> None:
    assert not setup.has_api_key("LASTFM_API_KEY=\n")
    assert not setup.has_api_key("# comment\nLASTFM_API_KEY=  \n")
    assert not setup.has_api_key("OTHER_KEY=value\n")
    assert setup.has_api_key("LASTFM_API_KEY=actual-key\n")
