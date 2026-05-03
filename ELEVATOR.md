# Antiphon — the elevator version

A personal music recommender where the brain lives in Markdown.

No recommendation logic in code — a handful of `.md` files turn
Claude Code into a music agent that reads your real last.fm history
every session and recommends music grounded in what you actually
listen to, not what an algorithm thinks you should.

A few short Python helpers wrap the data layer for token efficiency,
not intelligence; the reasoning stays with Claude. Long tail
respected. Every pick cites its reasoning. Nothing is cached,
nothing leaves your machine. Fork it, drop your last.fm credentials
into two files, run `make install`, you're going in a couple of
minutes.
