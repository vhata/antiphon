# Antiphon

A personal last.fm recommendation companion. Antiphon is **not a piece of
software** — it is a small set of Markdown documents that turn an LLM
(specifically [Claude Code](https://claude.com/claude-code)) into a music
recommendation agent grounded in your real last.fm listening history.

> *An antiphon is a sung response — a call answered with a counter-call.
> You ask; the library answers.*

---

## How it works

There is no application code. When you run Claude Code in this directory:

- **`CLAUDE.md`** tells Claude what to do — how to query the last.fm API,
  how to format recommendations as Spotify search links, how to use the
  mood system, and the standing recommendation logic.
- **`user.md`** (gitignored — see `user.example.md`) holds your last.fm
  username and any personal listening notes Claude should respect every
  session.
- **`.env`** (gitignored — see `.env.example`) holds your last.fm API key.
- **`moods.md`** (gitignored — see `moods.example.md`) is your evolving
  library of mood / context buckets ("small hours", "deep work", "long
  drive") and the picks you have validated against them.

Claude reads these files, queries the last.fm Web Services API live for
your scrobbling history, and generates recommendations on demand. Nothing
is cached on disk; every session starts fresh from your most recent data.

## Setup

1. Clone this repository.
2. Get a free last.fm API key at <https://www.last.fm/api/account/create>.
3. Configure your environment:
   ```bash
   cp .env.example .env             # then add your LASTFM_API_KEY
   cp user.example.md user.md       # then add your last.fm username
   cp moods.example.md moods.md     # this becomes your living mood library
   ```
4. Open the directory in [Claude Code](https://claude.com/claude-code).
5. Ask for a recommendation.

You should not need to edit `CLAUDE.md` to use Antiphon. The three files
above are the only ones that hold your data.

## Examples

- *"What should I listen to right now?"* — Claude pulls your recent
  scrobbles and top artists across multiple time windows, reads the shape
  of your listening, and offers recommendations grouped by rationale.
- *"Give me something for small hours."* — Claude opens your mood library,
  finds the bucket you named, and serves picks from your validated +
  candidate set.
- *"Deeper into Brian Eno."* — Depth-mode: rather than recommending new
  artists, Claude suggests the next album to dig into for an artist
  already in your library.
- *"Anti-Spotify mode."* — Actively avoid the obvious next-step picks
  Spotify's algorithm would surface.
- *"What did I love this time last year?"* — Time-travel mode against
  your scrobble history.

The full design space is catalogued (sometimes seriously, often not) in
[`TODO.md`](TODO.md).

## File reference

| File                | Tracked | Purpose                                                |
| ------------------- | :-----: | ------------------------------------------------------ |
| `CLAUDE.md`         | ✓       | Operating instructions for Claude.                     |
| `README.md`         | ✓       | This file.                                             |
| `LICENSE`           | ✓       | MIT.                                                   |
| `TODO.md`           | ✓       | Wishlist of directions Antiphon could grow in.         |
| `user.example.md`   | ✓       | Template for personal config.                          |
| `user.md`           | —       | Your last.fm username and listening notes.             |
| `.env.example`      | ✓       | Template for credentials.                              |
| `.env`              | —       | Your last.fm API key.                                  |
| `moods.example.md`  | ✓       | Mood-library template with one worked example.         |
| `moods.md`          | —       | Your evolving mood library.                            |

## Design principles

- **No telemetry, no cloud, nothing leaves your machine.** Your listening
  data is read from last.fm by Claude during a session and used to
  produce recommendations on the spot. Nothing is cached, logged, or
  forwarded.
- **Markdown is the architecture.** As long as Antiphon can stay in
  Markdown form, it will. The line at which it would graduate to real
  software is documented in `TODO.md` § 4.
- **The long tail matters.** Antiphon is biased toward respecting the
  obscure half of your library, on the grounds that the mainstream half
  is well-served by every other recommender on earth.
- **Every recommendation cites its reasoning.** Picks should trace back
  to a specific signal in your listening data ("you have 2,628 plays of
  Massive Attack but no Tricky", etc.).
- **Generated content is always labelled.** If Claude produces a fake
  liner note or a hallucinated artist anecdote, it says so plainly.

## License

[MIT](LICENSE) — do what you like with it.
