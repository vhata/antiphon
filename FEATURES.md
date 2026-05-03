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
- ✓ **Helper scripts** (`scripts/profile.py`, `scripts/forgotten_gems.py`,
  `scripts/mood.py`; `make profile`, `make gems`, `make mood NAME='...'`)
  — Python wrappers around the data layer that emit compact text instead
  of raw JSON. `profile` returns a tight listening-shape snapshot;
  `gems` returns the forgotten-gem dormant set; `mood` parses `moods.md`
  for a named mood and prints its validated + candidate picks as
  Spotify search links (no API key needed; pure file lookup).
- ✓ **Layer-2 review skill** (`.claude/skills/antiphon-review/SKILL.md`)
  — project-aware pre-commit review reading `CLAUDE.md`, `README.md`,
  `FEATURES.md`, and `WISHLIST.md` § 4 before inspecting the diff.
  Reports convention drift, missing living-doc updates, and accidental
  crossings of the "becomes software" line. Reports only; no auto-fix.
