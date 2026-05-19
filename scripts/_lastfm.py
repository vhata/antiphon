"""Shared last.fm Web Services API helpers.

Public read-only API; the only credential is the API key, read from
the LASTFM_API_KEY environment variable. If the variable is not set,
the helpers fall back to reading `.env` at the repo root — no need to
`source .env` before running a script.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, cast

API_BASE = "https://ws.audioscrobbler.com/2.0/"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Per-request timeout for last.fm calls. Without this, a dropped TCP
# connection causes urlopen() to block indefinitely (no default in
# Python's urllib), which has hung multi-hour backfills in the past.
REQUEST_TIMEOUT_SECONDS = 30.0


def _load_env_file() -> None:
    """If LASTFM_API_KEY is unset, try to populate it from .env at repo root.

    Existing environment variables take precedence over file values.
    Tolerates `KEY=value`, `KEY="value"`, `export KEY=value`, comments,
    and blank lines. Anything else is ignored silently.
    """
    if "LASTFM_API_KEY" in os.environ:
        return
    if not ENV_PATH.exists():
        return
    for raw in ENV_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def _api_key() -> str:
    _load_env_file()
    key = os.environ.get("LASTFM_API_KEY")
    if not key:
        raise RuntimeError(
            "LASTFM_API_KEY not found in environment or in .env. "
            "Copy .env.example to .env and add your last.fm API key."
        )
    return key


def call(method: str, **params: str | int) -> dict[str, Any]:
    """Call a last.fm API method and return the parsed JSON response.

    Applies `REQUEST_TIMEOUT_SECONDS` so a dropped connection raises
    `socket.timeout` instead of hanging indefinitely.
    """
    query: dict[str, str] = {
        "method": method,
        "api_key": _api_key(),
        "format": "json",
    }
    for name, value in params.items():
        query[name] = str(value)
    url = f"{API_BASE}?{urllib.parse.urlencode(query)}"
    with urllib.request.urlopen(  # noqa: S310 (trusted host)
        url, timeout=REQUEST_TIMEOUT_SECONDS
    ) as response:
        return cast(dict[str, Any], json.loads(response.read()))
