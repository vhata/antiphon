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
- **Anti-rec list** — `dislikes.md` (gitignored) + `dislikes.example.md`
  template, with the read/filter/append rule wired into `CLAUDE.md`.
  Rejected picks are now persistent across sessions.
- **Optional last.fm MCP integration** — `CLAUDE.md` and `README.md`
  now document two data-access paths: self-contained `.env` API key
  (default), or [lastfm-mcp.com](https://lastfm-mcp.com) via OAuth.
  Antiphon detects MCP tools (`mcp__lastfm__*`) at session start and
  prefers them when present, falling back to direct curl + API key
  otherwise. Method-mapping table in `CLAUDE.md` keeps the two paths
  in sync.
- **Contractify option-2 hygiene** — `FEATURES.md` ledger,
  `.claude/skills/antiphon-review/SKILL.md` Layer-2 review skill,
  and a "Living documents" section in `CLAUDE.md` (with the
  codify-before-deciding-to-implement rule). The Markdown-only
  subset of the contractify skill, deliberately skipping the
  Makefile / hooks / CI that don't fit a no-application-code project.
- **Python scaffolding for helper scripts** — `pyproject.toml` (uv,
  dev-only: ruff + mypy + pytest, `package = false`), a real
  `Makefile` with `install`/`check`/`format`/`lint`/`typecheck`/
  `test` plus project-specific `profile`/`gems` targets, `scripts/`
  + `tests/` directories with shared `scripts/_lastfm.py`, gitignore
  updates. Deliberate, narrow crossing of WISHLIST § 4's
  "becomes software" line, scoped to the helper scripts.
- **`scripts/profile.py`** — compact listening-shape summary across
  the four time windows + recent + loved. Run via `make profile`.
  Replaces the multi-call inline curl burst that previously consumed
  significant context at session start.
- **`scripts/forgotten_gems.py`** — promotes the previously-inline
  forgotten-gem algorithm into a script. Run via `make gems` (or
  `uv run python -m scripts.forgotten_gems N` for a specific count).
  CLAUDE.md § Forgotten-gem mode now points at the script rather
  than describing the algorithm inline.
