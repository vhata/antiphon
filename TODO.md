# TODO

Concrete, near-term work for Antiphon. Items move from `WISHLIST.md`
into here when they become real plans, and out of here when done —
deleted, not archived. User-observable shipped features land in
`FEATURES.md`; pure infrastructure changes live in the git log. If
something starts to feel speculative or uncertain, it goes back to
the wishlist.

This file should stay short and honest.

---

## In flight

*(nothing in flight — pick from `Next` or `Soon` to start)*

## Next

- **SQLite scrobble cache (on-demand, contiguous-range model).**
  A single table `scrobbles(uts INTEGER PRIMARY KEY, artist TEXT,
  album TEXT, track TEXT)` stored in `antiphon.db` at the repo
  root (gitignored). Two watermarks — `oldest_uts_cached` and
  `newest_uts_cached` — track the cached interval. Every
  scrobble-shaped query for `[t0, t1]`:
  - If `t1 > newest_uts_cached`, fetch `[newest_uts_cached, now]`
    from `user.getRecentTracks`, append, advance the upper
    watermark.
  - If `t0 < oldest_uts_cached`, fetch `[t0, oldest_uts_cached]`
    from `user.getRecentTracks`, append, push the lower watermark
    back.
  - Then read `[t0, t1]` straight from SQLite.

  Because both extensions are always contiguous, the cached data
  is a single unbroken interval — no gap-tracking, no coverage
  ledger. UTS as primary key means duplicate inserts from overlaps
  are free.

  **Scope is strictly scrobble events.** Derived aggregations
  (`user.getTopArtists`, `user.getTopAlbums`) and metadata
  endpoints (`artist.getInfo`, `artist.getSimilar`,
  `artist.getTopTags`) are NEVER cached — they drift over time and
  must stay live.

  Lives in a new shared `scripts/_cache.py` module beside
  `_lastfm.py`. `sqlite3` is Python stdlib, so no new runtime
  dependency. `make clean` wipes the cache; deletion is always
  safe because the cache is not a source of truth — last.fm is.

  Migration is incremental: scripts that need scrobble history
  (`heatmap`, a future `timeline`, the pulse panel of `dashboard`,
  `recent`, `rut`) move to the cache one by one. Everything else
  stays on live API.

  This is the deliberate graduation flagged in `WISHLIST.md §4`
  for the scrobble-cache item specifically. Other items in §4
  (real CLI, web UI, etc.) remain held back.

- **Sleep-album filter for behavioural views.** Listener-specific
  filter list (artist + album combos) read from a gitignored
  `sleep_albums.md` with a committed `.example` template. The
  heatmap (and future behavioural views) excludes scrobbles
  matching the filter before bucketing, so early-morning cells
  reflect actual activity rather than 8-hour overnight tails of
  *Mezzanine*, *Dummy*, *From Sleep* and the like. Parser lives
  alongside the existing `_moods.py` / `_dislikes.py` shared
  modules. Heatmap gets an `--include-sleep` flag for the raw
  view. The on-disk list is small and append-only as new sleep
  records surface in conversation.


## Soon

*(none — see `WISHLIST.md` for the broader design space)*

## Maybe

- **`make timeline` — discovery timeline of top-50 artists.** For
  each artist in the overall top 50, find the date of their first
  scrobble; print a year-by-year list of "in {year}, you discovered
  {artist}". Narrative, not real-time. Caveat: a full historical
  scrobble scan is expensive (deep `user.getRecentTracks` pagination)
  and may force the `WISHLIST.md §4` SQLite question if used often.
- **(Explicitly deferred)** Interactive `textual` TUI with
  navigation, key bindings, and persistent state — over the
  `WISHLIST.md §4` line (real application code). Re-evaluate only
  if the static snapshot version proves clearly inadequate.
- **Spotify Web API (Client Credentials)** — direct track URIs
  instead of search URLs. ~10 minutes of setup to register an app.
- **Held in reserve: YAML frontmatter for structured Markdown** —
  the established Markdown-meets-structure pattern (Hugo / Jekyll /
  MDX). If the shared-parser approach hits a real wall — a parsing
  case that conventions cannot rescue — migrate each `##` section in
  `moods.md` and `dislikes.md` to carry a 3-line YAML frontmatter
  block (name, type, brief description) with prose underneath. Adds
  the `pyyaml` dep. Migration is mechanical (one-time script).
  Parser becomes `yaml.safe_load` rather than regex. **Do not pull
  forward** until the shared-parser approach visibly fails — format
  changes are larger than they look in the abstract.
