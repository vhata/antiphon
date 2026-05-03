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

| Command                         | What it does                                                    | Needs `.env` |
| ------------------------------- | --------------------------------------------------------------- | :----------: |
| `make profile`                  | Compact listening-shape across 4 time windows + recent + loved. | yes          |
| `make gems`                     | Dormant artists in the overall top 100–500.                     | yes          |
| `make mood NAME='<mood>'`       | Picks for a mood as ready-to-click Spotify search links.        | no           |

Or run directly: `uv run python -m scripts.profile`,
`uv run python -m scripts.forgotten_gems [N]`,
`uv run python -m scripts.mood "<mood>"`.

For the data-fetching scripts, source `.env` first:
`set -a; source .env; set +a`.

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
