# Using Antiphon

What to type to get music. For setup see [`ONBOARDING.md`](ONBOARDING.md);
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

**Reading data from last.fm:**

| Command                                 | What it does                                                            |
| --------------------------------------- | ----------------------------------------------------------------------- |
| `make profile`                          | Compact listening-shape across 4 time windows + recent + loved.         |
| `make gems`                             | Dormant artists in the overall top 100–500 (forgotten-gem retrieval).   |
| `make recent N=7`                       | Last N days of scrobbles + per-artist tally for the period.             |
| `make similar ARTIST='X' N=20`          | Artists similar to X, with library overlap marked (gaps flagged).       |
| `make stats`                            | Library-coverage diagnostic: top-N concentration, long-tail size.       |

**Editing local state:**

| Command                                                           | What it does                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------- |
| `make mood NAME='<mood>'`                                         | Picks for a mood as Spotify search links. No arg lists all moods. |
| `make reject LABEL='X' REASON='Y' [CATEGORY='Artists']`           | Append to `dislikes.md` under a category.                     |
| `make validate MOOD='small hours' PICK='Stars of the Lid'`        | Promote a candidate bullet to validated under a mood.         |
| `make add-mood NAME='deep work' DESC='Focused coding.'`           | Scaffold a new mood section in `moods.md`.                    |
| `make populate-mood NAME='deep work' N=5`                         | Ask Claude (headless `claude -p`) to propose mood candidates. |
| `make log-rec PICK='Artist — Album' SOURCE='<mood>'`              | Log a recommendation to `session.log.md` (cool-down basis).   |
| `make cooldown DAYS=7`                                            | Show recommendations from the last N days.                    |
| `make chase N=5`                                                  | Now-playing chaser: similar tracks to your latest scrobble.   |
| `make depth ARTIST='Pink Floyd'`                                  | Artist depth check: which canonical albums you've under-played. |
| `make rut DAYS=14`                                                | Detect listening rut: top-1 / top-2 concentration check.      |

Or run any of them directly: `uv run python -m scripts.<name> [args]`.

The data-fetching scripts auto-load `.env` from the repo root if
`LASTFM_API_KEY` is not already in your shell environment — no need
to source it manually. The state-editing and `mood` scripts need no
credentials.

## Files you edit

| File           | Purpose                                                              |
| -------------- | -------------------------------------------------------------------- |
| `user.md`      | Your last.fm username + any personal listening notes for Claude.     |
| `.env`         | Your last.fm API key (`LASTFM_API_KEY`).                             |
| `moods.md`     | Per-mood validated and candidate picks; evolves as you use Antiphon. |
| `dislikes.md`  | Anti-rec list; appended automatically by Claude when you reject.     |

All four are gitignored — a fork-er gets the `.example` templates
and fills in their own.

## All make targets at a glance

Run `make` (no target) for the live list. Stable named entrypoints:

- `make install` — uv sync, install dev deps.
- `make check` — format-check + lint + typecheck + tests.
- `make format` / `make lint` / `make typecheck` / `make test`.
- `make clean` — remove cache directories.
- `make profile` / `make gems` / `make mood NAME='...'`.
