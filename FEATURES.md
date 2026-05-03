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
  `scripts/reject.py`, `scripts/validate.py`; `make mood NAME='...'` /
  `make reject LABEL='X' REASON='Y' [CATEGORY='...']` /
  `make validate MOOD='X' PICK='Y'`) — read `moods.md` for the named
  mood and emit Spotify links; append a rejection to `dislikes.md`;
  promote a candidate to validated under a mood. No API key needed;
  pure file edits.
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
