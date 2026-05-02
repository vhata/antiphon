# Dislikes

The anti-rec list. Artists, sub-genres, scenes, vibes, and specific
albums the listener has actively rejected. Claude reads this every
recommendation session and filters as hard against it as it does
against the top-artists list (no point re-suggesting something the
user has explicitly said no to).

This file is a worked-example template. Copy it to `dislikes.md`
(gitignored, so your rejections stay local) and edit there.

## Format

Each entry is a short label, a one-line reason, and the date logged.
Reasons matter — they let Claude judge edge cases (e.g. a rejection
of *noisy industrial* should not block quiet ambient even if both
fall under "industrial" in some genre tree).

```
- **<label>** — <one-line reason>. *(YYYY-MM-DD)*
```

## Artists

Specific artists never to recommend.

*(none yet)*

## Sub-genres / scenes

Whole corners of the map to avoid.

*(none yet)*

## Vibes / qualities

Cross-cutting properties (e.g. "no jam-band noodling", "no
sleaze-rock vocals", "no 4/4 EDM build-drop structure").

*(none yet)*

## Specific albums

When the artist is fine but one record isn't.

*(none yet)*
