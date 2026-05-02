# Moods

User-validated mood / context buckets for last.fm recommendations.
Each mood has a short description, a list of *validated* picks (the
user has confirmed they work for this mood), and a list of *candidates*
still under evaluation.

When the user asks for recs in one of these moods, branch from the
validated picks first; fall back to candidates if the validated set is
thin. Move candidates → validated as the user confirms them, and drop
anything they reject.

This file is a worked-example template. Copy it to `moods.md` (which
is gitignored, so user-specific picks stay local) and edit there. This
template stays generic.

---

## small hours

*Middle of the night, woken up, want to wind back down toward sleep.*

Picks should: be long-form, low-transition, mostly instrumental or
near-vocal-less, predictable in shape, and never escalate. Avoid
lyrics the listener will attend to, beat drops, or anything dark
enough to spike alertness. Drone, ambient, modern classical, slow
piano, and the quietest end of downtempo are all in scope.

### Validated

*(populate as the user confirms picks)*

### Candidates

- **Brian Eno — *Music for Airports* (1978) / *Apollo: Atmospheres &
  Soundtracks* (1983) / *Thursday Afternoon* (1985) / *Discreet Music*
  (1975)** — the canonical ambient texts.
- **Max Richter — *From Sleep* (2015)** — 1-hour edit of *Sleep*, an
  album literally composed to be slept through. The on-the-nose pick.
- **Stars of the Lid — *And Their Refinement of the Decline* (2007)**
  — glacial drone, no hooks, no surprises.
- **Nils Frahm — *Spaces* (2013) / *All Melody* (2018)** — solo piano
  and quiet electronics, slow build, never sharp.
- **A Winged Victory for the Sullen — *A Winged Victory for the
  Sullen* (2011)** — chamber drone, post-classical, mournful but not
  anxious.

---

## Adding a new mood

1. User describes the mood in their own words.
2. Pick a short, evocative name (2–3 words).
3. Drop a description of what the mood asks for, then 4–6 candidate picks.
4. As the user listens and reports back, promote candidates → validated
   or remove them.
