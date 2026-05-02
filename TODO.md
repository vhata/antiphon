# TODO

Concrete, near-term work for Antiphon. Items move from `WISHLIST.md`
into here when they become real plans, and out of here into the
`Shipped` section when done. If something starts to feel speculative
or uncertain, it goes back to the wishlist.

This file should stay short and honest.

---

## In flight

*(nothing in flight — pick from `Next` to start)*

## Next

- **Anti-rec list** — `dislikes.md` (gitignored) + `dislikes.example.md`
  template. Logs rejected artists / scenes / vibes so they never get
  re-suggested.
- **Now-playing chaser** — a `/next`-style request: pull the most
  recent scrobble, suggest something that segues sonically.
- **Cool-down for past recs** — lightweight session log so I don't
  recommend the same thing twice in nearby sessions.

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

## Shipped

- **Forgotten-gem mode** — `CLAUDE.md`. Surfaces artists in the
  overall top 100–500 unplayed for ≥12 months, framed as "you used
  to love this". Pure retrieval, not discovery.
