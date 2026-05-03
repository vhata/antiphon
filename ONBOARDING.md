# Onboarding

From zero to your first recommendation in a couple of minutes. If
anything below trips you up, the **Troubleshooting** section near
the bottom probably covers it.

## Prerequisites

- [Claude Code](https://claude.com/claude-code) installed.
- A last.fm account with a publicly visible listening history.
- A terminal you are comfortable using.
- (Optional, for helper scripts) [uv](https://docs.astral.sh/uv/)
  for the Python toolchain.

## 1. Clone

```sh
git clone https://github.com/vhata/antiphon.git
cd antiphon
```

## 2. Pick a data-access path

Antiphon needs to read your last.fm history. There are two ways;
either is fine.

### Path A — self-contained (default)

Free last.fm API key from
<https://www.last.fm/api/account/create>. Then:

```sh
cp .env.example .env
# edit .env and paste your key into LASTFM_API_KEY=
```

Zero hosted dependencies. Everything runs locally.

### Path B — hosted MCP

Install the lastfm MCP server (one command, OAuth-based, no API
key needed):

```sh
claude mcp add --transport http lastfm https://lastfm-mcp.com/mcp
```

Sign in with your last.fm account when prompted. Powered by
[lastfm-mcp.com](https://lastfm-mcp.com) (third-party hosted —
trades self-containment for setup convenience). Antiphon detects
the MCP automatically and prefers it when present.

## 3. Configure your identity

```sh
cp user.example.md user.md
# edit user.md and set your last.fm username
```

You can also add personal listening notes (musical heritage,
preferences, anything you'd like Claude to weight every session) but
that's optional and grows over time.

## 4. (Optional) Seed your mood library

```sh
cp moods.example.md moods.md
```

This becomes your evolving library of mood / context buckets
("small hours", "deep work", etc.) and the picks you have validated
against them. You can also leave it for Claude to populate by use.

## 5. (Optional) Install the helper-script toolchain

If you want the `make profile` / `make gems` / `make mood`
shortcuts that bypass Claude entirely:

```sh
make install
```

This requires uv. If you only want to talk to Claude in the
directory, you can skip this — Antiphon works without the helpers.

## 6. Open in Claude Code

```sh
claude
```

(Or open the directory in your IDE with the Claude Code extension.)

## 7. Ask for your first recommendation

Just ask, in plain English:

> What should I listen to right now?

Claude pulls your real listening history (recent + top across
multiple time windows + loved tracks), reads its shape, and offers
recommendations grouped by rationale — each one a clickable Spotify
search link.

For more of what you can ask, see
[`HIGHLIGHTS.md`](HIGHLIGHTS.md).

---

## Troubleshooting

### *"could not find username in user.md"*

Your `user.md` is missing the username line. It should contain
something like:

```markdown
- **Username:** yourhandle
```

(The older `**last.fm username:**` form also works — the parser is
case-insensitive and tolerant of either.)

### `make profile` says *"LASTFM_API_KEY not in environment"*

Source `.env` before invoking the data-fetching scripts:

```sh
set -a; source .env; set +a
make profile
```

`make mood` does *not* need this — it only reads `moods.md`.

### `make` returns *"No rule to make target"*

Either you haven't run `make install` yet, or you're not in the
`antiphon/` directory. Run `make` (no arguments) to see the live
list of available targets.

### Claude doesn't seem to know about my last.fm history

- Check `user.md` exists and has the right username.
- If you chose **Path A**, confirm `LASTFM_API_KEY` is set in your
  shell (`echo $LASTFM_API_KEY`).
- If you chose **Path B**, run `claude mcp list` to confirm the
  `lastfm` MCP is registered and authenticated.

### A recommendation came back as a plain URL instead of a clickable link

This is a render-side issue with whichever client you're using —
Antiphon always emits inline markdown links. If a client renders
markdown poorly, the link still works as plain text.

### I want to add my own mood / dislike / etc.

Edit `moods.md` and `dislikes.md` directly, or just tell Claude in
chat — it will update the files for you. Both are gitignored, so
your edits stay on your machine.

---

## Where to next

- [`HIGHLIGHTS.md`](HIGHLIGHTS.md) — what you can actually do.
- [`FEATURES.md`](FEATURES.md) — what's shipped.
- [`TODO.md`](TODO.md) — what's planned next.
- [`WISHLIST.md`](WISHLIST.md) — the full design space, including
  the deliberately-not-yet-built and the deliberately-never-built.
