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

*(nothing in flight — pick from `Next` to start)*

## Next

- **Now-playing chaser** — a `/next`-style request: pull the most
  recent scrobble, suggest something that segues sonically.
- **Cool-down for past recs** — lightweight session log so I don't
  recommend the same thing twice in nearby sessions.
- **`make populate-mood NAME='X'` — first script that invokes an LLM**
  — calls Claude Code headless (`claude -p`) with the mood's
  description (parsed from `moods.md`) plus the listener's listening
  shape (`scripts/profile` output) and asks for 4–5 candidate bullets.
  Output appended to the mood's `### Candidates` section via
  `_moods.replace_subsection_body`. No new auth needed — Claude Code
  is already a prerequisite; depends on `claude` being on PATH and the
  headless mode behaving predictably.

  **Architectural step worth naming.** Until now, scripts wrap data
  and Claude does the reasoning in chat. This puts reasoning *behind*
  a script — a small but real line crossed. Worth doing for the
  ergonomics (especially in scripted flows where breaking into chat
  is friction), but worth knowing we are stepping over it. Sister
  scripts that could follow once this lands and proves stable:
  `populate-dislikes`, `populate-recs`, `chase` (the now-playing
  chaser, which currently sits as its own TODO).

## Soon

- **Time-of-day defaults** — at 02:30 default to `small hours`, at
  09:00 default to a morning mood (TBD which one).
- **Discovery dial** — per-request: `familiar` / `adjacent` / `outward`
  / `wildcard`.
- **Era preference dial** — per-request, optional: only pre-1990,
  only post-2020, no preference.
- **Artist-depth mode** — "give me the next album to dig into for
  {existing artist}". High-leverage for the heavy-rotation names.
- **Library-coverage stat** — one-liner on request: "X unique
  artists, Y% of plays from your top 5, here's where the long tail
  starts."

## Maybe

- **Rut detector** — when 1–2 artists dominate ≥40% of plays for ≥2
  weeks, flag and offer either deeper dive or deliberate detour.
- **Spotify Web API (Client Credentials)** — direct track URIs
  instead of search URLs. ~10 minutes of setup to register an app.
- **`why this rec?` verbosity setting** — terse / paragraph / essay.
- **Held in reserve: YAML frontmatter for structured Markdown** —
  the established Markdown-meets-structure pattern (Hugo / Jekyll /
  MDX). If the shared-parser approach above hits a real wall — a
  parsing case that conventions cannot rescue — migrate each `##`
  section in `moods.md` and `dislikes.md` to carry a 3-line YAML
  frontmatter block (name, type, brief description) with prose
  underneath. Adds the `pyyaml` dep. Migration is mechanical
  (one-time script). Parser becomes `yaml.safe_load` rather than
  regex. **Do not pull forward** until the shared-parser approach
  visibly fails — format changes are larger than they look in the
  abstract.

