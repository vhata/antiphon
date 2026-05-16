"""Shared parser for sleep_albums.md.

The format mirrors the bullet style used by `moods.md` and
`dislikes.md`: a Markdown file with one or more bullets of the form
`- **Artist — *Album***` (extra prose after the bold block is
allowed and ignored). Bullets without a recognisable album are
skipped.

The filter is applied to scrobble-shaped views (the heat-map today,
future behavioural reports) so that records the listener falls
asleep to do not skew early-morning activity cells.
"""

from __future__ import annotations

from pathlib import Path

from scripts._moods import parse_pick, split_bullets

SLEEP_ALBUMS_MD = Path(__file__).resolve().parent.parent / "sleep_albums.md"


def parse(text: str) -> list[tuple[str, str]]:
    """Return `(artist, album)` pairs from raw Markdown text.

    Both artist and album are lowercased so the caller can match
    case-insensitively without re-normalising. Bullets that do not
    parse to an `(artist, album)` pair — including the `*(none yet)*`
    placeholder — are skipped.
    """
    pairs: list[tuple[str, str]] = []
    preamble, bullets = split_bullets(text)
    # `split_bullets` leaves a leading bullet (one that begins at
    # offset 0 with no preceding newline) inside `preamble`. Promote
    # it so single-bullet inputs parse correctly.
    if preamble.startswith("- "):
        bullets = [preamble, *bullets]
    for raw in bullets:
        content = raw[2:].strip() if raw.startswith("- ") else raw.strip()
        if not content or content.startswith("*("):
            continue
        artist, album = parse_pick(content)
        if not album:
            continue
        pairs.append((artist.lower(), album.lower()))
    return pairs


def load(path: Path = SLEEP_ALBUMS_MD) -> list[tuple[str, str]]:
    """Read `path` and return the parsed `(artist, album)` pairs.

    Returns `[]` if the file does not exist — the filter is
    listener-specific and absence means "no filter".
    """
    if not path.exists():
        return []
    return parse(path.read_text())


def matches(artist: str, album: str, pairs: list[tuple[str, str]]) -> bool:
    """True if `(artist, album)` matches any pair in `pairs`.

    Comparison is case-insensitive on both sides. An empty `pairs`
    list always returns False.
    """
    if not pairs:
        return False
    a = artist.lower()
    b = album.lower()
    return (a, b) in pairs
