---
name: antiphon-review
description: Project-aware pre-commit review for the Antiphon repository. Reads CLAUDE.md, README.md, FEATURES.md, and WISHLIST.md § 4 before inspecting staged changes. Reports findings the lint layer cannot catch — convention drift, missing living-document updates, accidental crossings of the "becomes software" line the project explicitly avoids, and patterns established by feedback that the diff has slipped past. Reports only; does not auto-apply fixes. Use at the end of a meaningful chunk of work before commit.
---

# antiphon-review

Layer 2 review for the Antiphon repository. Catches what lint cannot.
Reports findings only; does not auto-fix.

## 1. Read the canonical brief

Before looking at any diff, read in full:

- `CLAUDE.md` — operating instructions for Antiphon plus the patterns
  section established by user feedback. Both are load-bearing.
- `README.md` — what Antiphon is and how it's used.
- `FEATURES.md` — what's shipped.
- `WISHLIST.md` § 4 — the "becomes software" line. Many architectural
  choices are "deliberately not done until X."

## 2. Identify the diff

Run `git diff --staged`. If staging is empty, fall back to
`git diff` against the working tree.

Read every hunk. Note the files touched and the surfaces affected.

## 3. Walk the review categories

### A. Convention drift

Antiphon has narrow, opinionated conventions in `CLAUDE.md`. Does the
diff respect them?

- Spotify links inline as markdown links with the title as link text;
  no bare URLs on their own line.
- Every recommendation cites the signal that produced it.
- Data access path A (MCP) preferred when available, path B
  (`.env` + curl) as fallback.
- Voice (per the user's global rule) does not leak into files written
  to disk — file content stays neutral and professional regardless of
  the voice in chat.

### B. Living-document updates

Per `CLAUDE.md` § Living documents, a commit that ships
user-observable change must touch the relevant document.

- User-observable behaviour changed → `README.md` updated?
- Feature shipped or moved status → `FEATURES.md` updated?
- TODO completed → entry removed from `TODO.md`, recorded in `Shipped`?
- New convention surfaced from feedback → captured in `CLAUDE.md`?

### C. "Becomes software" line

Antiphon's pitch is "Markdown is the architecture; no application
code; no infrastructure until graduation." The line is documented in
`WISHLIST.md` § 4. Does the diff cross it? If so, is the crossing
deliberate (with rationale captured) or accidental?

The `scripts/` Python helpers are an established narrow exception
(token-saving for in-session use). New infrastructure additions
beyond that should be flagged.

### D. Token economy

Antiphon is consumed by Claude in-conversation. Does the diff add
prose to a session-loaded file (`CLAUDE.md`, `user.md`, `moods.md`,
`dislikes.md`) that pays for its tokens? Long-form explanation belongs
in `README.md` / `WISHLIST.md` / `TODO.md`; session-loaded files stay
tight.

### E. Naming and tone

- New modes / moods / sub-features: names should describe a thing's
  nature over its temperament (this is why the project is called
  Antiphon and not Reverie).
- Commit messages neutral and concise; the user's "voice" rule does
  not bleed into git history.

## 4. Write the report

Group findings into three buckets:

- **Blockers** — violations of an explicit rule. Must be fixed before
  commit.
- **Concerns** — judgment calls worth flagging. The user decides.
- **Notes** — observations worth recording without action.

Format the verdict at the end:

> Blockers: N · Concerns: M · Notes: K · {commit / fix-then-commit / do-not-commit}

Do not auto-apply fixes. The skill is reports-only; the user (or the
assistant in a separate turn) does the fixing.
