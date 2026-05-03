# Antiphon

A personal music recommender where the brain lives in Markdown.

No recommendation logic in code — a handful of `.md` files turn
[Claude Code](https://claude.com/claude-code) into a music agent
that reads your real last.fm history every session and recommends
music grounded in what you actually listen to, not what an
algorithm thinks you should. A few short Python helpers wrap the
data layer for token efficiency, not intelligence; the reasoning
stays with Claude.

> *An antiphon is a sung response — a call answered with a
> counter-call. You ask; the library answers.*

## Design properties

- **Local-only.** Your listening data is read from last.fm during a
  session and used to produce recommendations on the spot. Nothing
  is cached, logged, or forwarded.
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
