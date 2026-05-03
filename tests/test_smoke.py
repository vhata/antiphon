"""Smoke tests — no network, no environment setup required."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import _lastfm


def test_lastfm_module_imports() -> None:
    assert hasattr(_lastfm, "call")
    assert _lastfm.API_BASE.startswith("https://")


def test_api_key_raises_when_unset_and_no_env_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("LASTFM_API_KEY", raising=False)
    monkeypatch.setattr(_lastfm, "ENV_PATH", tmp_path / "missing.env")
    with pytest.raises(RuntimeError, match="LASTFM_API_KEY"):
        _lastfm._api_key()


def test_api_key_loaded_from_env_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("LASTFM_API_KEY=test-key\n")
    monkeypatch.delenv("LASTFM_API_KEY", raising=False)
    monkeypatch.setattr(_lastfm, "ENV_PATH", env)
    assert _lastfm._api_key() == "test-key"


def test_env_var_takes_precedence_over_env_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env = tmp_path / ".env"
    env.write_text("LASTFM_API_KEY=from-file\n")
    monkeypatch.setenv("LASTFM_API_KEY", "from-env")
    monkeypatch.setattr(_lastfm, "ENV_PATH", env)
    assert _lastfm._api_key() == "from-env"


def test_env_file_handles_comments_quotes_and_export(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env = tmp_path / ".env"
    env.write_text('# a comment line\n\nexport LASTFM_API_KEY="quoted-key"\nOTHER_VAR=other\n')
    monkeypatch.delenv("LASTFM_API_KEY", raising=False)
    monkeypatch.setattr(_lastfm, "ENV_PATH", env)
    assert _lastfm._api_key() == "quoted-key"
