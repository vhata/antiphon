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
  `scripts/reject.py`, `scripts/validate.py`, `scripts/add_mood.py`;
  `make mood NAME='...'` / `make reject LABEL='X' REASON='Y'
  [CATEGORY='...']` / `make validate MOOD='X' PICK='Y'` /
  `make add-mood NAME='X' DESC='Y'`) — render a mood as Spotify
  links, append a rejection, promote a candidate to validated, or
  scaffold a new mood section. No API key needed; pure file edits
  via the shared `_moods` / `_dislikes` parser modules.
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
- ✓ **Shared Markdown parser modules** (`scripts/_moods.py`,
  `scripts/_dislikes.py`) — single source of truth for parsing and
  mutating `moods.md` and `dislikes.md`. Every script that touches
  those files imports here rather than re-implementing the regex.
  Internal API but user-visible benefit is consistency: edits done
  by one script land the same way as edits done by another.
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
