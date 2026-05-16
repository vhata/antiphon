# Sleep albums

Records the listener falls asleep to. Long-form ambient or
near-vocal-less records that scrobble through the night — they
register as plays, but they are passive overnight audio, not
active listening.

Behavioural views (today: the heat-map; future: any "when do I
listen" report) filter scrobbles matching this list before bucketing
so the early-morning cells reflect what the listener actually does
at 03:00, not the eight-hour tail of an album left running.

This file is a worked-example template. Copy it to `sleep_albums.md`
(gitignored, so listener-specific titles stay local) and edit there.

## Format

Each entry is a Markdown bullet matching the bullet style used by
`moods.md`: bold artist and italic album, separated by an em dash.

```
- **<Artist Name> — *<Album Title>***
```

Extra prose after the bold block is allowed and ignored by the
parser. The filter matches on artist + album, case-insensitive.

## Filter list

- **Brian Eno — *Music for Airports***
- **Brian Eno — *Thursday Afternoon***
- **Stars of the Lid — *And Their Refinement of the Decline***
- **A Winged Victory for the Sullen — *Atomos***
- **Max Richter — *From Sleep***
