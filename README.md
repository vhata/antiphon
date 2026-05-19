# Antiphon

A personal music recommender where the brain lives in Markdown.

No recommendation logic in code — a handful of `.md` files turn
[Claude Code](https://claude.com/claude-code) into a music agent
that reads your real last.fm history every session and recommends
music grounded in what you actually listen to, not what an
algorithm thinks you should. A small set of Python helpers wrap the
data layer (last.fm API → compact text) for token efficiency. One
helper (`make populate-mood`) deliberately invokes Claude headless
to seed mood candidates on demand; everything else keeps the
reasoning in chat.

> *An antiphon is a sung response — a call answered with a
> counter-call. You ask; the library answers.*

## Design properties

- **Local-first.** Your listening data is fetched from last.fm and
  used to produce recommendations on the spot. The only data that
  leaves your machine is the explicit invocation of `make
  populate-mood`, which sends mood context to Claude headless. A
  handful of small files persist locally (all gitignored,
  listener-specific): a SQLite cache of raw scrobble events at
  `antiphon.db` (purely a performance layer over the last.fm API —
  delete it and the next run rebuilds), an append-only `session.log.md`
  for the cool-down convention, a `daily.log.md` for the daily
  one-track horoscope, and an optional `sleep_albums.md` filter list.
  Aggregations, similar-artist queries, and tag endpoints are not
  cached and refetch per session.
- **Markdown is the architecture.** Antiphon stays in Markdown form
  for as long as it can. The line at which it would graduate to
  real software is documented in [`WISHLIST.md`](WISHLIST.md) § 4.
- **The long tail matters.** Antiphon is biased toward respecting
  the obscure half of your library, on the grounds that the
  mainstream half is well-served by every other recommender on earth.
- **Every recommendation cites its reasoning.** Picks should trace
  back to a specific signal in your listening data.
- **Generated content is always labelled.** If Claude produces a
  fake liner note or a hallucinated anecdote, it says so plainly.

## Get started

New here? Walk through [`ONBOARDING.md`](ONBOARDING.md).

## Use it

What to type to get music: [`USING.md`](USING.md).

## Other documents

- [`FEATURES.md`](FEATURES.md) — what's shipped.
- [`TODO.md`](TODO.md) — concrete near-term work.
- [`WISHLIST.md`](WISHLIST.md) — full design space, including the
  unhinged. Section 4 explains the no-application-code stance.
- [`CLAUDE.md`](CLAUDE.md) — operating instructions Claude reads
  every session.

## License

[MIT](LICENSE) — do what you like with it.
