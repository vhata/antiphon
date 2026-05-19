# Features

Feature ledger for Antiphon. One line per shipped feature.

Legend: ✓ shipped · ⋯ in progress

## Milestone — initial work

- ✓ **Forgotten-gem mode** (`CLAUDE.md` § Forgotten-gem mode) —
  surfaces dormant artists in the user's overall top 100–500 unplayed
  for ≥12 months, framed as "you used to love this". Retrieval, not
  discovery.
- ✓ **Anti-rec list** (`dislikes.md`, gitignored; `dislikes.example.md`
  template) — rejected picks persist across sessions. Claude reads and
  filters every recommendation, and appends new rejections immediately
  with a one-line reason.
- ✓ **Optional last.fm MCP integration** (`CLAUDE.md` § Data access) —
  Antiphon detects `mcp__lastfm__*` tools when present and prefers them
  over the self-contained `.env` + curl path. Both setup options
  documented in README; method-mapping table keeps them in sync.
- ✓ **Helper scripts — data readers** (`scripts/profile.py`,
  `scripts/forgotten_gems.py`, `scripts/recent.py`, `scripts/similar.py`,
  `scripts/stats.py`; `make profile` / `gems` / `recent N=7` /
  `similar ARTIST='X' N=20` / `stats`) — Python wrappers around the
  last.fm API that emit compact text instead of raw JSON. Auto-load
  `.env` so no shell preamble is needed.
- ✓ **Helper scripts — state editors** (`scripts/mood.py`,
  `scripts/reject.py`, `scripts/validate.py`, `scripts/add_mood.py`,
  `scripts/add_candidate.py`; `make mood` / `reject` / `validate` /
  `add-mood` / `add-candidate`) — render a mood as Spotify links,
  append a rejection, promote a candidate to validated, scaffold a
  new mood, or hand-add a single candidate to a mood. No API key
  needed; pure file edits via the shared `_moods` / `_dislikes`
  parser modules.
- ✓ **First-time setup wizard** (`scripts/setup.py`; `make setup`,
  or `python3 scripts/setup.py` before uv is installed) — interactive
  walkthrough that scaffolds `user.md`, `.env`, `moods.md`, and
  `dislikes.md` from their `.example` templates with two prompts
  (last.fm username and API key). Idempotent; skips already-configured
  steps. ONBOARDING reorganised around it as the Quick path with
  manual setup as fallback.
- ✓ **`make populate-mood NAME='X' [N=5]`** (`scripts/populate_mood.py`)
  — uses Claude Code headless (`claude -p`) to propose candidate picks
  for a mood. The first script that invokes an LLM rather than just
  wrapping data; prompt includes the mood's description and the
  listener's top-artists across four time windows. Picks appended via
  the shared `_moods.replace_subsection_body`.
- ✓ **Now-playing chaser** (`scripts/chase.py`; `make chase [N=5]`) —
  pulls the listener's most recent scrobble and suggests sonically
  compatible follow-ups via `track.getSimilar` (with `artist.getSimilar`
  fallback). Filters against the cool-down log.
- ✓ **Cool-down for past recs** (`scripts/log_rec.py`,
  `scripts/cooldown.py`; `make log-rec` and `make cooldown`) —
  append-only log of recommendations in `session.log.md` (gitignored).
  Codified read/append convention in `CLAUDE.md`. Retires the
  manual hold previously kept in the assistant's memory store.
- ✓ **Artist depth check** (`scripts/depth.py`; `make depth ARTIST='X'`)
  — given an artist, lists their globally-top albums alongside the
  listener's playcount per album, with a `GAP` marker on canonical
  records the listener has never touched. Drives the artist-depth
  recommendation modifier.
- ✓ **Recommendation modifiers in `CLAUDE.md`** — codified five
  prompt-shaping conventions Claude applies in chat: discovery dial
  (familiar / adjacent / outward / wildcard), era preference,
  time-of-day defaults, why-this-rec verbosity, artist depth.
  Convention-only; no scripts beyond `make depth`.
- ✓ **Rut detector** (`scripts/rut.py`; `make rut [DAYS=14]`) —
  computes top-1 and top-2 artist concentration over the last N
  days. Flags as a rut when top-1 ≥ 40% or top-2 ≥ 60% of plays
  (sample-size-aware), and surfaces *lean in* (depth into the top
  artist) vs *lean out* (forgotten gems) options.
- ✓ **Daily one-track horoscope** (`scripts/daily.py`; `make daily`)
  — single track per day, persisted in `daily.log.md` (gitignored)
  so re-running returns the same pick. Strategy rotates by
  day-of-year through five corners (`comfort`, `forgotten`, `gap`,
  `loved`, `tag-walk`) so the daily ritual stays varied.
- ✓ **Album-deep mode** (`CLAUDE.md` § Album-deep mode) — pure
  conversational convention, no script. Triggered by *"sit with me
  through <album>"* / *"liner notes for <album>"*; produces
  track-by-track notes for an album the listener is about to play.
  Distinct from `depth`, which is about what to play *next*.
- ✓ **Period-in-music report** (`scripts/review.py`; `make review
  PERIOD={week,month,quarter,year}`) — categorises this period's top
  artists against the listener's overall taste: *newcomers* (not in
  overall top 100), *comfort returners* (also in overall top 25),
  and *mid-tier* (overall rank 26-100). Plus a one-line volume note.
  Periodic check-in when a real period boundary hits.
- ✓ **Listening heat-map** (`scripts/heatmap.py`; `make heatmap
  [DAYS=90]`) — 7×24 grid of scrobble density by day-of-week and
  hour-of-day, rendered as block characters scaled to the peak cell.
  Reads scrobbles via `scripts/_cache.py` so repeat runs over the
  same window do no API work; widening the window only fetches the
  uncovered gap. Timestamps are interpreted in the listener's *local*
  timezone (scrobbles are stored in UTC, but the question "when do I
  listen?" is only meaningful locally). Pure bucketing + render
  functions are unit-tested separately from the data plumbing.
- ✓ **Sleep-album filter for behavioural views** (`sleep_albums.md`,
  gitignored; `sleep_albums.example.md` template; `scripts/_sleep.py`)
  — listener-specific list of records they fall asleep to. The
  heat-map drops scrobbles matching the list before bucketing so
  the early-morning cells reflect active listening rather than
  overnight tails of long-form ambient. Pass `--include-sleep` to
  the heat-map for the raw view. Parser lives beside `_moods.py` /
  `_dislikes.py`; absence of the file is a clean no-op.
- ✓ **Cache adoption: `recent`, `rut`, `dashboard` pulse** — all
  three scripts now read scrobble windows via `scripts/_cache.py`
  instead of paginating `user.getRecentTracks` directly. Repeat runs
  over the same window do no API work; widening the window only
  fetches the uncovered gap. No user-visible behaviour change beyond
  speed.
- ✓ **Discovery timeline** (`scripts/timeline.py`; `make timeline
  [N=50]`) — for each of the listener's overall top-N artists,
  finds the date of their first scrobble and emits a year-by-year
  list ("in 2008: Massive Attack, Pink Floyd, Portishead"). Reads
  the full scrobble history through `scripts/_cache.py`; the first
  run triggers a one-time backfill (slow), subsequent runs are
  instant. Pure year-bucketing + earliest-uts logic unit-tested
  with stubbed cache; main path verified with mocks rather than a
  live backfill.
- ✓ **Listening snapshot dashboard** (`scripts/dashboard.py`;
  `make dashboard`) — single-screen `rich`-formatted view of the
  listener's current shape: top artists across the four time windows
  side-by-side, a 30-day scrobble sparkline, a library-genres panel
  (tags aggregated from `artist.getInfo` on the top 10 overall
  artists, weighted by playcount × tag rank — so the panel reflects
  the *library*, not the listener's self-tagging), mood-library
  fullness (with thin moods flagged), the cool-down list, and a
  loved-tracks weekly delta. Static one-shot — no persistent state,
  no interactivity — so it stays on the right side of
  `WISHLIST.md` § 4. First runtime dep (`rich`); pure data-shaping
  functions are unit-tested separately from the layout.
- ✓ **Shared Markdown parser modules** (`scripts/_moods.py`,
  `scripts/_dislikes.py`) — single source of truth for parsing and
  mutating `moods.md` and `dislikes.md`. Every script that touches
  those files imports here rather than re-implementing the regex.
  Internal API but user-visible benefit is consistency: edits done
  by one script land the same way as edits done by another.
- ✓ **SQLite scrobble cache** (`scripts/_cache.py`; `antiphon.db` at
  the repo root, gitignored) — on-demand cache of raw scrobble events
  keyed on UNIX timestamp, with per-user `oldest_uts_cached` /
  `newest_uts_cached` watermarks. `get_scrobbles(user, from_uts,
  to_uts)` extends the cache by contiguous interval and returns dicts
  shaped like `user.getRecentTracks` track entries. Stdlib-only.
  Adopted by `heatmap`, `recent`, `rut`, `dashboard` (pulse panel),
  and `timeline`. Deliberate graduation per `WISHLIST.md` § 4.
- ✓ **Text-first state hierarchy** (`CLAUDE.md` § Where state lives) —
  Markdown for human-curated state, JSON when text gets awkward (none
  yet), SQLite on the becomes-software side of `WISHLIST.md` § 4 and
  not crossed casually. Live data fetched per-call, not cached.
- ✓ **Reach-for-a-script-first principle** (`CLAUDE.md` § When to
  reach for a script vs reason in chat) — mechanical work goes to
  scripts; Claude tokens are reserved for taste reasoning.
- ✓ **Layer-2 review skill** (`.claude/skills/antiphon-review/SKILL.md`)
  — project-aware pre-commit review reading `CLAUDE.md`, `README.md`,
  `FEATURES.md`, and `WISHLIST.md` § 4 before inspecting the diff.
  Reports convention drift, missing living-doc updates, and accidental
  crossings of the "becomes software" line. Reports only; no auto-fix.
- ✓ **Optional Spotify Web API integration** (`scripts/_spotify.py`,
  `SPOTIFY_CLIENT_ID` + `SPOTIFY_CLIENT_SECRET` in `.env`) — when both
  env vars are set, recommendation links resolve to direct
  `open.spotify.com/{track,album,artist}/<id>` URLs via the Spotify
  Web API client-credentials flow. Missing credentials or API misses
  fall back silently to the existing search-URL convention. Stdlib
  only; in-process token cache. Callers: `daily`, `chase`, `mood`.
