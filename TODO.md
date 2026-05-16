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


## Soon

*(none — see `WISHLIST.md` for the broader design space)*

## Maybe

- **`make dashboard` — glanceable listening snapshot.** Single
  command, `rich`-formatted full-screen panel: top 5 artists across
  the 4 time windows (7day / 1month / 6month / overall) side-by-side,
  30-day scrobble sparkline, top tags, mood-library fullness (which
  moods are thin on candidates), cool-down count, weekly loved-tracks
  delta. Static one-shot — stays on the right side of `WISHLIST.md §4`
  so long as it remains a text-emitting script with no persistent
  state or interactivity. Adds `rich` as a dep. Idea-time rationale:
  surfaced when the listener wanted a passive read on their listening
  while out of the house and unable to play music.
- **`make timeline` — discovery timeline of top-50 artists.** For
  each artist in the overall top 50, find the date of their first
  scrobble; print a year-by-year list of "in {year}, you discovered
  {artist}". Narrative, not real-time. Caveat: a full historical
  scrobble scan is expensive (deep `user.getRecentTracks` pagination)
  and may force the `WISHLIST.md §4` SQLite question if used often.
- **`make heatmap` — ASCII listening heat-map.** Hours-of-day ×
  days-of-week density grid. Behavioural, not musical — reveals
  *when* you listen. Promotes the "Day-of-week / time-of-day
  distributions" idea from `WISHLIST.md §6`. Same data-cost concern
  as `timeline`.
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
