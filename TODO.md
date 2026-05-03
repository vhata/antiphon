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

- **Period-in-music report** (`make review PERIOD=month` or `=year`)
  — composite analytics: top artists this period vs. baseline, what
  disappeared, what appeared, dominant tags, listening volume curve.
  Heavy on the LLM-narration side. Useful as a periodic check-in.
  Larger scope than daily; build only when a real period boundary
  approaches.
- **Album-deep mode** — pure Claude convention in `CLAUDE.md`, no
  script. Sit with one album for the duration of a listen and
  produce track-by-track liner notes as it plays. Different from
  `depth` (which suggests what to play next); this is about
  listening *into* a record. Triggered by phrases like *"sit with
  me through X"* or *"liner notes for X"*.

## Soon

*(none — see `WISHLIST.md` for the broader design space)*

## Maybe

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
