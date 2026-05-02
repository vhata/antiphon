# Antiphon

A personal last.fm recommendation companion. There is no application
code — Claude reads the user's last.fm listening history via the Web
Services API and generates recommendations on demand, guided by the
conventions in this file and the mood library in `moods.md`.

The name *Antiphon* is the musical / liturgical term for a sung
response — a call answered with a counter-call. The user asks; the
library answers.

## Configuration

Two files hold everything that makes this *your* Antiphon — to point
this at a different listener, edit these and nothing else:

- **`user.md`** — last.fm username and any personal listening notes.
  Gitignored; copy `user.example.md` to `user.md` to set up. Read at
  the start of every session.
- **`.env`** — last.fm API key as `LASTFM_API_KEY`. Gitignored;
  copy `.env.example` to `.env` to set up. Read at session start.

Do not hardcode the username or the API key anywhere else. Last.fm
read endpoints only require an `api_key` query param — no signing,
no session token, no shared secret needed for the calls listed below.

## API base

```
https://ws.audioscrobbler.com/2.0/?method=<METHOD>&user=<USER>&api_key=<KEY>&format=json
```

Useful methods (all read-only, all work with just the API key):

- `user.getRecentTracks` — what they're playing now / recently
- `user.getTopArtists` — top artists over `period` (overall, 7day, 1month, 3month, 6month, 12month)
- `user.getTopTracks` — same shape, for tracks
- `user.getTopAlbums` — same shape, for albums
- `user.getTopTags` — their most-used tags
- `user.getLovedTracks` — explicitly loved
- `artist.getSimilar` — for branching out from a known artist
- `track.getSimilar` — for branching out from a known track
- `tag.getTopArtists` / `tag.getTopTracks` — for genre-driven discovery

Pagination is `limit` + `page`. Default `limit` is 50; raise to 200 when
you need a bigger sample.

## Moods

User-validated mood / context buckets live in `moods.md`. When the
user asks for recs framed by a mood (e.g. "small hours", "coding",
"long drive"), open `moods.md`, use the validated + candidate picks
as seeds, and follow the workflow at the bottom of that file for
promoting candidates and adding new moods.

`moods.md` is gitignored so the listener's personal picks stay local.
A generic template lives in `moods.example.md` — copy it to `moods.md`
on a fresh setup.

## Spotify links

Each recommendation must be a clickable Spotify link. Format it as a
markdown link with the artist/album/track name itself as the link
text — never paste a bare URL on its own line:

    [Brian Eno — Thursday Afternoon](https://open.spotify.com/search/Brian%20Eno%20Thursday%20Afternoon)

The URL is always a Spotify search URL of the form
`https://open.spotify.com/search/{url-encoded query}`. No Spotify Web
API, no API key, no OAuth — search URLs work without authentication
and the desired result is reliably the top hit.

Query format by target:

- artist:  `{Artist Name}`
- album:   `{Artist Name} {Album Title}`
- track:   `{Artist Name} {Track Title}`

URL-encode spaces as `%20`.

## How to make recommendations

When the user asks for recs:

1. Pull a snapshot of their listening — recent tracks plus top artists/tracks
   across multiple time windows (7day, 1month, 6month, overall) so you can
   tell what's *current* vs. what's *core*.
2. Look at the shape of it: dominant genres, recent shifts, repeated artists
   vs. one-offs, what they've loved.
3. For each direction worth recommending in, branch via `artist.getSimilar`
   or `tag.getTopArtists`, then **filter out anything already in their top
   artists** so you're not recommending what they already listen to.
4. Present a small number of picks (5–10) grouped by the rationale —
   "more of what you already love", "adjacent to your recent kick",
   "wildcard from a tag you keep returning to". Always say *why* a pick
   is on the list.
5. If they push back ("more obscure", "less metal", "skip anything I've
   already played"), refine and re-query. Don't dump a giant list up front.

## Minimising API calls

- Cache nothing on disk — each session re-fetches. Listening history changes.
- Within a single session, reuse fetched data; don't re-call the same
  endpoint with the same params twice.
- Prefer one wide call (`limit=200`) over many paginated ones when you
  need breadth.

## Working in this repo

Git is used here as a local safety net — there is no remote and pushing
is not configured. After any meaningful edit to a tracked file, make a
commit as part of the same response, without asking permission. Keep
commit subjects tight; add a body only when it adds context. Never run
`git push`; if a remote is ever added, still wait for an explicit ask.

## Out of scope

- No scrobbling, no writes, no auth flow. If the user ever asks for those,
  that's the point where this stops being a `CLAUDE.md` and becomes real
  software.
