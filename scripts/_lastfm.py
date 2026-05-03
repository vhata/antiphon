"""Shared last.fm Web Services API helpers.

Public read-only API; the only credential is the API key, read from
the LASTFM_API_KEY environment variable. Source `.env` before invoking
any script that calls these helpers.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, cast

API_BASE = "https://ws.audioscrobbler.com/2.0/"


def _api_key() -> str:
    key = os.environ.get("LASTFM_API_KEY")
    if not key:
        raise RuntimeError(
            "LASTFM_API_KEY not in environment. Source .env first: `set -a; source .env; set +a`"
        )
    return key


def call(method: str, **params: str | int) -> dict[str, Any]:
    """Call a last.fm API method and return the parsed JSON response."""
    query: dict[str, str] = {
        "method": method,
        "api_key": _api_key(),
        "format": "json",
    }
    for name, value in params.items():
        query[name] = str(value)
    url = f"{API_BASE}?{urllib.parse.urlencode(query)}"
    with urllib.request.urlopen(url) as response:  # noqa: S310 (trusted host)
        return cast(dict[str, Any], json.loads(response.read()))
