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

- **Migrate remaining scrobble-window scripts to the cache.** The
  cache module (`scripts/_cache.py`) and the heat-map have moved
  over; `recent`, `rut`, and the pulse panel of `dashboard` are
  still on direct paginated `user.getRecentTracks` calls. One PR
  per script keeps blast radius small.

## Soon

*(none — see `WISHLIST.md` for the broader design space)*

## Maybe

- **(Explicitly deferred)** Interactive `textual` TUI with
  navigation, key bindings, and persistent state — over the
  `WISHLIST.md §4` line (real application code). Re-evaluate only
  if the static snapshot version proves clearly inadequate.
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
