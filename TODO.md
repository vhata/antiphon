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

## Soon — scripts that take work off Claude

Surfaced from the *reach-for-a-script-first* principle in
`CLAUDE.md`. Each is mechanical work currently done in chat that
ought to live in a script.

- **`make reject ARTIST='...' REASON='...'`** — append an entry to
  `dislikes.md` without invoking Claude. The mechanical version of
  what Claude currently does when the user says "I hate this".
- **`make validate MOOD='...' PICK='...'`** — promote a pick from
  Candidates → Validated under a named mood in `moods.md`.
  Mechanical edit; no reasoning needed.
- **`make recent N=7`** — last N days of scrobbles in compact form.
  A subset of `make profile` for when focus beats breadth.
- **`make similar ARTIST='...'`** — `artist.getSimilar` wrapper
  returning the top N similar artists with overlap-against-library
  pre-computed (highlights gaps). The mechanical layer that feeds
  Claude when reasoning about adjacents is needed.
- **`make stats`** — library-coverage one-liner: total unique
  artists, top-N concentration, decade distribution, longest
  scrobble streak. Diagnostic; no reasoning.

## Soon — other

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

