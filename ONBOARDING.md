# Onboarding

From zero to your first recommendation in a couple of minutes. Most
fork-ers should follow the **Quick path**; the **Manual setup**
section is the fallback for those who prefer hand-editing files,
and the **Path B** section covers the OAuth-based alternative.

If anything trips you up, **Troubleshooting** at the bottom probably
covers it.

## Prerequisites

- [Claude Code](https://claude.com/claude-code) installed.
- A last.fm account with publicly visible listening history.
- A terminal you are comfortable using.
- Python 3 (any modern version) for the setup wizard.
- (For the helper scripts) [uv](https://docs.astral.sh/uv/).

## Quick path

```sh
git clone https://github.com/vhata/antiphon.git
cd antiphon
python3 scripts/setup.py
```

The wizard prompts for your last.fm username and an API key (link
shown in-flight; takes about a minute at
<https://www.last.fm/api/account/create>), then scaffolds four
gitignored files: `user.md`, `.env`, `moods.md`, `dislikes.md`. It
is idempotent — re-running skips already-configured steps.

Then:

```sh
make install            # uv-managed Python toolchain
make profile            # verify the last.fm connection works
claude                  # open the project in Claude Code, then ask:
                        # "What should I listen to right now?"
```

For more of what you can ask, see [`USING.md`](USING.md).

## Path B — hosted MCP (skip the API key)

If you'd rather not register for a last.fm API key, install the
[lastfm-mcp.com](https://lastfm-mcp.com) MCP server (one command,
OAuth-based):

```sh
claude mcp add --transport http lastfm https://lastfm-mcp.com/mcp
```

Sign in with your last.fm account when prompted. Antiphon detects
the MCP automatically and prefers it when present, so the `.env`
step in the wizard becomes unnecessary — skip the API-key prompt
when it appears.

This trades self-containment for setup convenience; the MCP is a
third-party hosted service.

## Manual setup

If you'd rather skip the wizard:

```sh
cp .env.example .env             # then paste your LASTFM_API_KEY
cp user.example.md user.md       # then set your last.fm username
cp moods.example.md moods.md
cp dislikes.example.md dislikes.md
make install
```

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

### `make profile` says *"LASTFM_API_KEY not found in environment or in .env"*

Either `.env` does not exist at the repo root, or it does not
contain a `LASTFM_API_KEY=` line with a non-empty value. Run
`python3 scripts/setup.py` (which will populate `.env` if missing)
or hand-edit. The scripts auto-load `.env` — no need to source it
manually.

### `make` returns *"No rule to make target"*

Either you haven't run `make install` yet, or you're not in the
`antiphon/` directory. Run `make` (no arguments) to see the live
list of available targets.

### Claude doesn't seem to know about my last.fm history

- Check `user.md` exists and has the right username.
- If you chose **Path A**, confirm `LASTFM_API_KEY` is set in your
  `.env` (`grep LASTFM_API_KEY .env`).
- If you chose **Path B**, run `claude mcp list` to confirm the
  `lastfm` MCP is registered and authenticated.

### A recommendation came back as a plain URL instead of a clickable link

A render-side issue with whichever client you're using — Antiphon
always emits inline markdown links. If a client renders Markdown
poorly, the link still works as plain text.

### I want to add my own mood / dislike

Either tell Claude in chat (it will update the files for you), or
use the helper scripts directly:

```sh
make add-mood NAME='deep work' DESC='Focused coding.'
make reject LABEL='Author & Punisher' REASON='too noisy'
```

See [`USING.md`](USING.md) for the full list of helper-script
shortcuts.

---

## Where to next

- [`USING.md`](USING.md) — what to type to get music.
- [`FEATURES.md`](FEATURES.md) — what's shipped.
- [`TODO.md`](TODO.md) — what's planned next.
- [`WISHLIST.md`](WISHLIST.md) — the full design space, including
  the deliberately-not-yet-built and the deliberately-never-built.
