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
