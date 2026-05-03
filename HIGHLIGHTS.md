# Antiphon — what you can actually do

A capability tour. For setup see [`ONBOARDING.md`](ONBOARDING.md);
for the shipped-features ledger see [`FEATURES.md`](FEATURES.md);
for the project overview see [`README.md`](README.md).

## Talk to it

Open the directory in [Claude Code](https://claude.com/claude-code)
and ask in plain English:

- *"What should I listen to right now?"* — Claude pulls your
  listening shape (recent + top across multiple time windows +
  loved) and offers picks grouped by rationale.
- *"Give me something for small hours."* (or any mood from
  `moods.md`: `deep work`, `kitchen`, `rainy sunday`, `wake up`,
  `dinner party`, `catharsis`, `post-fight`, `3am insomnia`) —
  picks drawn from your validated and candidate sets for that mood.
- *"Forgotten gems."* — artists from your overall top 100–500 you
  haven't played in the last 12 months, framed as *you used to love
  this*.
- *"Deeper into Brian Eno."* — depth-mode for an artist already in
  your library: the next album to dig into rather than a similar
  artist.
- *"I hate this."* / *"Skip jam-band noodling."* — Claude appends
  the rejection to `dislikes.md` with a one-line reason and never
  re-suggests anything that matches.
- *"Anti-Spotify mode."* — actively avoid the obvious next-step
  picks Spotify's algorithm would surface.
- *"Read my library back to me."* — a prose portrait of your taste,
  grounded in actual play counts and ranks.

Recommendations come back as inline markdown links to Spotify
searches. Click through to play.

## Run a script (no Claude in the loop)

After `make install` (uv-managed Python deps):

| Command                                | What it does                                                       | Needs `.env` |
| -------------------------------------- | ------------------------------------------------------------------ | :----------: |
| `make profile`                         | Compact listening-shape across 4 time windows + recent + loved.    | yes          |
| `make gems`                            | Dormant artists in the overall top 100–500 (forgotten-gem mode).   | yes          |
| `make mood NAME='<mood>'`              | Picks for a mood as ready-to-click Spotify search links.           | no           |

Or run directly: `uv run python -m scripts.profile`,
`uv run python -m scripts.forgotten_gems [N]`,
`uv run python -m scripts.mood "<mood>"`.

For data-fetching scripts, source `.env` first:
`set -a; source .env; set +a`.

## Files you edit

| File           | Purpose                                                               |
| -------------- | --------------------------------------------------------------------- |
| `user.md`      | Your last.fm username + any personal listening notes for Claude.      |
| `.env`         | Your last.fm API key (`LASTFM_API_KEY`).                              |
| `moods.md`     | Per-mood validated and candidate picks; evolves as you use Antiphon.  |
| `dislikes.md`  | Anti-rec list; appended automatically by Claude when you reject.      |

All four are gitignored — a fork-er gets the `.example` templates
and fills in their own.

## Make targets at a glance

Run `make` (no target) for the live list. Stable named entrypoints:

- `make install` — uv sync, install dev deps.
- `make check` — format-check + lint + typecheck + tests.
- `make format` / `make lint` / `make typecheck` / `make test`.
- `make clean` — remove cache directories.
- `make profile` / `make gems` / `make mood NAME='...'`.

## Design principles

- **Local-only.** Your listening data is read from last.fm by Claude
  during a session and used to produce recommendations on the spot.
  Nothing is cached, logged, or forwarded.
- **Markdown is the architecture.** Antiphon stays in Markdown form
  for as long as it can. The line at which it would graduate to
  real software is documented in [`WISHLIST.md`](WISHLIST.md) § 4.
- **The long tail matters.** Antiphon is biased toward respecting
  the obscure half of your library, on the grounds that the
  mainstream half is well-served by every other recommender on
  earth.
- **Every recommendation cites its reasoning.** Picks should trace
  back to a specific signal in your listening data ("you have 2,628
  plays of Massive Attack but no Tricky", etc.).
- **Generated content is always labelled.** If Claude produces a
  fake liner note or a hallucinated artist anecdote, it says so
  plainly.

## "Where's the UI?"

The chat interface *is* the UI. Every recommendation comes through
conversation; every mood is invoked by name; every rejection is
logged by telling Claude to filter against it in future sessions.
Building a traditional UI — a webpage, a CLI, a mobile app — would
cross the line into "real software" and lose the property that
makes Antiphon different from every other music recommender.

Two middle-ground extensions could meet ergonomics without breaking
the philosophy:

- An **iOS Shortcut** that opens Claude Code with a preset prompt,
  so a one-tap *small hours* sits on a home screen for the
  3am-in-bed case.
- An **MCP server** that lets other AI clients (Claude Desktop,
  ChatGPT, Gemini) query Antiphon's recommendation flow without the
  user needing to be in this terminal.

Neither is built. Both are noted in [`WISHLIST.md`](WISHLIST.md)
for when they're worth doing.
