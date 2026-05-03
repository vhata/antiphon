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

- **`make setup` — interactive NUX wizard for first-time fork-ers**
  — one command from clone to ready-to-use, minimal manual steps.
  Concrete flow (`scripts/setup.py`, stdlib-only so it runs before
  `make install`):
    1. Greet; list the four files about to be created.
    2. Prompt for last.fm username; populate `user.md` from
       `user.example.md`. Skip if `user.md` exists.
    3. Prompt for last.fm API key (link to the registration URL for
       those without one); populate `.env` from `.env.example`.
       Skip if `.env` already has a non-empty `LASTFM_API_KEY`.
    4. Copy `moods.example.md` → `moods.md` and
       `dislikes.example.md` → `dislikes.md` (skip each if target
       exists).
    5. Print next steps: `make install`, then `make profile` to
       verify, then open in Claude Code.
    6. Mention the `lastfm-mcp.com` path (Path B) for those who'd
       rather skip the API key entirely.
  Idempotent — re-running is safe. Does NOT shell out to
  `claude mcp add` (manual step), does NOT auto-install uv
  (chicken-and-egg). After this ships, `ONBOARDING.md` reorganises
  around `make setup` with the manual steps becoming the fallback.
- **Now-playing chaser** — a `/next`-style request: pull the most
  recent scrobble, suggest something that segues sonically.
- **Cool-down for past recs** — lightweight session log so I don't
  recommend the same thing twice in nearby sessions.
- **`make add-mood NAME='...'`** — append a new mood section to
  `moods.md` with the standard scaffold: italic description
  placeholder, "picks should..." paragraph, empty `### Validated`
  with `*(none yet)*`, empty `### Candidates` with `*(none yet)*`.
  Inserts above the meta `## Adding a new mood` section. Refuses
  if a mood with the same name already exists.
  Mechanical scaffold is the script; filling in the description and
  candidate picks is either hand-editing or chat with Claude. Pairs
  with the existing `make validate MOOD=... PICK=...` (promote
  candidate → validated) so the mood lifecycle is fully scriptable
  end-to-end.

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

