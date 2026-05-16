"""Optional Spotify Web API client-credentials integration.

The Antiphon default is to emit Spotify *search* URLs which work
without authentication. When the listener configures Spotify API
credentials (`SPOTIFY_CLIENT_ID` + `SPOTIFY_CLIENT_SECRET`), this
module resolves direct track / album / artist URIs via the Spotify
Web API for cleaner links.

The integration is strictly opt-in: every helper here returns `None`
when credentials are missing or the Spotify API misbehaves. Callers
fall back to the existing search-URL pattern silently.

Stdlib only — `urllib`, `json`, `base64`. No new dependencies.
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"

# Refresh a little before the server-reported expiry so we never race
# the clock on the API side.
_EXPIRY_SKEW_SECONDS = 30

# In-process token cache. (token, expires_at_unix_seconds).
_token_cache: tuple[str, float] | None = None


def _load_env_file() -> None:
    """Populate Spotify env vars from `.env` if either is unset.

    Matches the loader in `scripts/_lastfm.py` so the same `.env` file
    works for both credentials without a shell preamble.
    """
    if "SPOTIFY_CLIENT_ID" in os.environ and "SPOTIFY_CLIENT_SECRET" in os.environ:
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


def _credentials() -> tuple[str, str] | None:
    _load_env_file()
    client_id = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return None
    return (client_id, client_secret)


def is_available() -> bool:
    """True iff both Spotify env vars are set to non-empty values."""
    return _credentials() is not None


def _get_token() -> str | None:
    """Return a valid bearer token, fetching one if the cache is empty / stale.

    Returns None when credentials are missing or the token endpoint
    refuses the request. Callers should fall back to search URLs.
    """
    global _token_cache

    creds = _credentials()
    if creds is None:
        return None

    now = time.time()
    if _token_cache is not None:
        token, expires_at = _token_cache
        if now < expires_at:
            return token

    client_id, client_secret = creds
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    body = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    request = urllib.request.Request(
        TOKEN_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:  # noqa: S310 (trusted host)
            payload = cast(dict[str, Any], json.loads(response.read()))
    except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
        return None

    token_any = payload.get("access_token")
    expires_any = payload.get("expires_in")
    if not isinstance(token_any, str) or not isinstance(expires_any, int):
        return None

    _token_cache = (token_any, now + max(0, expires_any - _EXPIRY_SKEW_SECONDS))
    return token_any


def _search(query: str, item_type: str, key: str) -> str | None:
    """Run a Spotify /v1/search call and return the first hit's URL, or None."""
    token = _get_token()
    if token is None:
        return None

    params = urllib.parse.urlencode({"q": query, "type": item_type, "limit": 1})
    url = f"{API_BASE}/search?{params}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request) as response:  # noqa: S310 (trusted host)
            payload = cast(dict[str, Any], json.loads(response.read()))
    except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
        return None

    items = payload.get(key, {}).get("items") or []
    if not items:
        return None
    first = items[0]

    direct = first.get("external_urls", {}).get("spotify")
    if isinstance(direct, str) and direct:
        return direct

    item_id = first.get("id")
    if isinstance(item_id, str) and item_id:
        return f"https://open.spotify.com/{item_type}/{item_id}"

    return None


def search_track(artist: str, track: str) -> str | None:
    """Resolve a track to its direct Spotify URL, or None when unavailable."""
    query = f"{artist} {track}".strip()
    if not query:
        return None
    return _search(query, "track", "tracks")


def search_album(artist: str, album: str) -> str | None:
    """Resolve an album to its direct Spotify URL, or None when unavailable."""
    query = f"{artist} {album}".strip()
    if not query:
        return None
    return _search(query, "album", "albums")


def search_artist(name: str) -> str | None:
    """Resolve an artist to its direct Spotify URL, or None when unavailable."""
    query = name.strip()
    if not query:
        return None
    return _search(query, "artist", "artists")
