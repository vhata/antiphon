# WISHLIST

A catalogue of every direction Antiphon could move in, from "actually useful next session" through to "VC-funded delusion". Sorted by tractability. Nothing here is committed to.

This is the long form. The short, ordered, actively-worked list lives in `TODO.md` — items move from this wishlist into the TODO when they become real plans, and stay there until shipped.

The top of the list is sober and probably worth doing. The bottom of the list is unhinged and probably not. The middle is where the interesting decisions live.

---

## 1. Next session — small, high-value, no architecture change

- **Anti-rec list**: a `dislikes.md` (or section in `CLAUDE.md`) that records artists / sub-genres / vibes the user has actively rejected, so I never re-suggest them. Includes reason where useful (e.g. "no jam-band-adjacent stuff", "no sleaze-rock vocals").
- **Discovery dial**: per-request preference for how far from the user's centre of gravity to push — *familiar* / *adjacent* / *outward* / *wildcard*.
- **Era preference dial**: per-request, optional — only pre-1990 / only post-2020 / no preference.
- **Artist-depth mode**: instead of "recommend new artists", "give me the next album to dig into for {existing artist}". For someone with 5,208 Pink Floyd plays, deeper-cut steering is more valuable than another adjacent rec.
- **Forgotten-gem mode**: surface artists from the user's mid-tier overall plays (rank 100–500) that haven't been listened to in ≥1 year, framed as "you used to love this".
- **Session log**: append-only `session.log.md`, dated, with what was recommended and accepted/rejected. Avoids me re-suggesting the same stuff next session.
- **Now-playing chaser**: a `/next` style request — pull the most recent scrobble, suggest something that segues sonically (key/BPM/mood compatible).
- **Time-of-day defaults**: if the user asks at 02:30, default mood = `small hours`. If at 09:00, default to a morning mood (TBD).
- **Rut detector**: when 1–2 artists dominate ≥40% of plays for ≥2 weeks, flag it gently and offer either a deepening dive or a deliberate detour.
- **"Why this rec?" verbosity setting**: terse / paragraph / essay. Default terse; let the user ask for a long-form rationale.
- **Cool-down for past recs**: anything I've recommended in the last N days gets a soft block unless user asks for it.
- **Library-coverage stat**: a one-liner I can produce on request — "you've scrobbled 3,400 unique artists; 12% of plays come from your top 5; here's where the long tail starts".
- **Dispute / overrule**: lightweight way for the user to say "I rejected Author & Punisher, take it off the candidates list" without having to manually edit `moods.md`.

## 2. Moods to populate

A backlog. Each becomes its own bucket in `moods.md` with seeds + candidates, on demand. Listed in vague order of usefulness.

### Daily-life
- `deep work` — coding/writing, no vocals, gentle forward momentum, no sudden drops
- `shallow work` — admin, email, taxes — slightly more permissive, can have lyrics
- `kitchen` — cooking dinner solo, social-but-not-foreground
- `dinner party` — broadly likeable, conversation-friendly, no surprises
- `after-dinner / digestif` — wind from social into reflective
- `cleaning the house` — propulsive but not aggressive
- `gardening` — pastoral, long-form, no urgency
- `shower` — short, energising, recoverable from interruption
- `commute (active)` — walking/cycling, some BPM
- `commute (passive)` — bus/train, vibe-only, can drift
- `working from a café` — present-but-private, blends with crowd noise

### Movement
- `gym (lifting)` — propulsive, lyrical OK, BPM 100–130
- `gym (cardio)` — sustained, BPM 140+
- `run` — cadence-locked
- `yoga / stretching` — long-form, breath-paced
- `long drive (highway)` — narrative arcs, room for vocals, propulsion
- `long drive (city)` — shorter forms, can be dense
- `airport / travel` — low-foreground, durable across settings
- `on the plane` — headphone-friendly, dense / immersive

### Sleep / liminal
- `wake up gently` — opposite of `small hours`: ramp up over 20 mins
- `wake up energetically` — straight to BPM
- `nap` — short ambient, won't keep you under more than an hour
- `Sunday afternoon nap` — variant of above, more nostalgic
- `bedtime (adults)` — wind down without falling asleep mid-conversation
- `3am insomnia (resigned)` — alternate to small hours, when you've given up trying to sleep
- `3am insomnia (anxious)` — needs grounding, not soothing

### Emotional
- `post-fight (with someone you love)` — needs catharsis without escalation
- `post-fight (with someone you don't)` — energy release, vindictive permitted
- `the commute home from a bad day`
- `the commute home from a great day`
- `existential dread (mild)`
- `existential dread (operatic)` — lean into it
- `mourning` — distinct from sad; long, restorative
- `celebrating` — warmth, not just hype
- `homesick`
- `nostalgic for a place you've never been`
- `hangover (physical)` — soft, no surprises, no high-end
- `hangover (existential)` — soft, slow lyrics OK
- `melancholy but content` — Sunday rain
- `quiet rage` — controlled, not punk
- `loud rage` — punk, industrial, etc.

### Social
- `pre-night-out` — energising, building
- `post-night-out, alone` — late-night-after-the-after-party
- `post-night-out, with someone`
- `weddings`
- `funerals`
- `births / new-baby quiet`
- `road trip with friends`
- `road trip alone`

### Niche / one-off
- `studying for an exam`
- `writing emails you're avoiding`
- `taking a hard meeting`
- `recovering from a hard meeting`
- `gaming (low-stakes)`
- `gaming (high-stakes / focus)`
- `reading (vocal-light)`
- `bath`
- `a really long shower`
- `waiting for someone`
- `being on hold`
- `doing taxes`
- `coffee + admin Saturday`

### Identity / heritage
- `South African nostalgia` — Sugardrive, Springbok Nude Girls, etc., framed as a bucket
- `1990s alt-rock revisit`
- `electronica circa 2003`
- `the trip-hop canon` — Bristol-trinity deep dive bucket

## 3. Better recommendation logic

- Always cross-reference recs against the user's overall top **200** artists (not just 25), to avoid recommending things they have hundreds of plays of.
- Use `artist.getSimilar` *and* `track.getSimilar` *and* `tag.getTopArtists` for branching, weighted differently per mood.
- Distinguish **retrieval** ("get me back to artist X") from **discovery** ("genuinely new to me") explicitly, both as request modes.
- Mark recs that are "in the user's library but never explored" — a 2-play scrobble from 2014 is often more valuable than a brand-new artist.
- Cap "1 rec per scene/label per response" — avoid clustering.
- Track session-local recs and avoid repeats within a session (do this implicitly today; make it explicit).
- Per-mood, learn over time which seeds the user validates vs. rejects, and weight future picks accordingly.
- "Diversity floor" — every response of N picks must include at least 1 from outside the dominant cluster of the user's recent listening, even when they ask for "more of the same".
- "Anti-Spotify-algorithm" mode — actively *don't* recommend the obvious next-step from recent plays, since Spotify already does that. Bias toward picks Spotify's algorithm wouldn't surface.
- Provenance per pick: every rec should be traceable to the signal that produced it ("you've played X 200 times → similar.getArtists → top non-overlap"). Surface on request.
- Confidence score per pick, optionally surfaced.
- Track-level recs, not just artist/album-level — "this *one song* is the entry point" is often more useful than "go listen to their discography".

---

## 4. The "becomes software" line

### Why there is no UI

The chat interface *is* the UI. Every recommendation comes through conversation; every mood is invoked by name; every rejection is logged by telling Claude to filter against it in future sessions. Building a traditional UI — a webpage, a CLI, a mobile app — would cross the line into "real software" and lose the property that makes Antiphon different from every other music recommender.

The two middle-ground extensions in the list below (**iOS Shortcut**, **MCP server**) could meet ergonomics without breaking that philosophy: a one-tap home-screen prompt, or a way for other AI clients to query Antiphon. Neither is built. Both are deliberately on the to-do-but-not-yet pile.

### What would push us over

Right now the project has near-zero application code — `CLAUDE.md` + `moods.md` is the brain, and a few Python helpers wrap the data layer. The items below would each push it further across the line, and each is held back deliberately:

- **Local scrobble cache (SQLite)** — pull all-time scrobbles once, then incremental updates. Avoids repeated full-library API calls and unlocks proper analytics.
- **Scheduled jobs** — cron / launchd / GitHub Actions: nightly pull, weekly digest, monthly retrospective.
- **Real CLI** — `antiphon recs`, `antiphon mood small-hours`, `antiphon chase`, `antiphon depth pink-floyd`. TypeScript or Python, single binary, dotenv for keys.
- **Web UI / dashboard** — local Next.js app, charts, mood library, rec inbox.
- **iOS Shortcut** — opens Claude Code (or a sibling client) with a preset prompt; one-tap "small hours" from a home screen, addressing the 3am-in-bed case without building a real app.
- **Mobile app** — wrapper around the API, push notifications for new releases.
- **Email digest** — weekly summary, sent to self.
- **MCP server** — expose listening-profile + recommendation tooling so other AI clients can ask "what is the user into right now"; integrates with this `CLAUDE.md` directly.
- **Telegram / iMessage bot** — text "small hours" from bed, get a link back.
- **Browser extension** — see a band on Wikipedia, instantly know your last.fm relationship to them.
- **Spotify-app integration** — embed in Spotify clients via their developer platform (where allowed).

Decision principle: stay in the `CLAUDE.md`-only architecture as long as humanly possible. Only graduate when the user asks for something Claude-by-itself genuinely can't do (scheduling, persistence across sessions, structured analytics).

## 5. Streaming-service integrations

Beyond the current Spotify *search-URL* convention.

### Spotify
- **Web API (Client Credentials)** — direct track/album/artist URIs instead of search URLs. ~10 minutes of setup; only needs API key + secret. The obvious next step.
- **Web API (User OAuth)** — read user library, top items, recently played. Cross-reference Spotify saves with last.fm scrobbles for high-confidence rec filtering.
- **Playlist creation** — auto-generate per-mood playlists, sync as candidates evolve.
- **Spotify Connect** — push the queue directly to current playback device.
- **Audio features** — where still available post-Nov-2024 deprecations: BPM, key, energy, valence for sequencing.
- **Spotify-codes** — printable codes for physical artefacts (vinyl inserts, cards).

### Apple Music
- **MusicKit API** — requires Apple Developer ($99/yr). Worth it only if the user actually subscribes to Apple Music.
- **iTunes star ratings** — pull as additional taste signal (legacy but real).

### Other catalogues
- **YouTube Music** — unofficial API only; brittle. Useful for tracks not on Spotify.
- **Tidal** — for the audiophile mode.
- **Bandcamp** — best for the indie / SA discovery angle. Has a fan-collection API.
- **SoundCloud** — emerging-artist focus, official API.
- **Mixcloud** — DJ-mix discovery — directly feeds the trip-hop / downtempo obsession.
- **NTS / Boiler Room / Rinse FM** — radio show feeds for serendipitous discovery; pull schedule + tracklists.

### Metadata / commentary
- **Discogs** — physical media: what to buy on vinyl, pressings to chase, marketplace prices.
- **Songkick / Bandsintown** — concert tracking for every artist in the library.
- **Setlist.fm** — what's actually being played live; tour-prep mode.
- **MusicBrainz** — canonical metadata, deduping artist names.
- **AllMusic** — editorial reviews and reference biographies.
- **Pitchfork** — pull review scores for new releases; flag releases by library artists scoring ≥8.0.
- **The Wire** — long-form criticism for the more arcane corners of the library.
- **Genius** — lyrics, annotations, semantic-search-of-lyrics potential.
- **Rate Your Music** — community taste signals (no API, would require scraping).
- **Album of the Year** — aggregated reviews.

### Local / self-hosted
- **Plex / Jellyfin / Navidrome** — local-library awareness for self-hosters.
- **Roon** — high-end audio player with rich metadata.
- **Funkwhale** — federated music server.
- **Subsonic API** — lots of music players speak it.

### Devices
- **Sonos / HomePod / Cast** — direct-to-speaker queue control.
- **Apple Watch / Whoop / Oura** — heart-rate, HRV, sleep score as mood signal.
- **Shazam history** — pull what the user has Shazamed; high-intent discovery signal.

### Last.fm itself
- **Last.fm Pro** — subscription tier for higher API limits and better stats.
- **Native scrobbling fallback** — if the user listens via something that doesn't auto-scrobble, build a thin scrobbler.

## 6. Listening analytics & exports

- **Annual "year in scrobbles"** — full retrospective, multi-dimensional, replaces the Spotify-Wrapped void in your life.
- **Monthly digest** — top artists, surprises, abandonments, ascendances, deep-cuts.
- **Genre drift timeline** — how taste has migrated across years.
- **Artist co-occurrence graph** — D3 chord diagram or force-directed: which artists you listen to in the same sessions.
- **Lifetime listening hours** — gross total, by year, by genre, by mood.
- **Day-of-week / time-of-day distributions** — your listening rhythm laid bare.
- **Skip-rate inference** — for albums with a wide play-count spread across tracks, infer which tracks you skip.
- **Album-completion rate** — what % of plays are full-album sit-throughs.
- **"Stuck record" detector** — when one album dominates ≥40% of plays for ≥1 week, flag.
- **"Off-the-wagon" detector** — periods where scrobbling drops out (likely meaning real-life upheaval; flag with a soft "hope you're okay").
- **Listening sentiment over time** — combine with lyric corpora and tag clusters.
- **Emotional volatility index** — week-to-week mood shift magnitude.
- **Geographic listening patterns** — if location data is available (probably needs a separate tracker).
- **Streak tracker** — most consecutive scrobbling days, longest gap.
- **"Comeback" tracker** — artists you'd dropped that returned to heavy rotation.
- **Birthday-listening ritual** — each year, what was on the day before your birthday.
- **Decade dominance** — % of plays from each decade of music.
- **"Forgotten 2010s"** — decades you've under-explored relative to your era of birth.
- **Personal Pitchfork** — generate album reviews of your *own* year.
- **Listening DNA profile** — vector of percentages across genres / moods / eras.
- **Friend-overlap %** — similarity with public last.fm friends.
- **Library health** — % of plays from "core" (top 50) vs. long tail.
- **"Stranger to yourself"** — surface artists in the top 200 you don't think you've listened to deliberately in years.
- **CSV / JSON exports** — for everything; user-portable forever.
- **Markdown table outputs** — same data, pasteable into journals.
- **Yearly archive snapshots** — a `2026.json` you can diff against `2025.json`.

## 7. Discovery surfaces

Ways to *receive* recommendations, not just request them.

- **Daily one-track horoscope** — single track per day, framed seriously.
- **Weekly five-album dig** — Mondays, five new candidates.
- **Monthly genre tour** — one focused dive per month into an under-explored corner.
- **"Today in your history"** — what were you playing on this day in {year}.
- **"5 years ago today"** — the album that dominated this week, half a decade back.
- **Random-library walk** — pick a random track from your overall top 1,000; sit with it.
- **"From your blind spots"** — genres tagged often by your top *artists* but rarely by your top *tracks* — i.e. genres you flirt with but haven't deepened.
- **"Critical consensus you missed"** — albums Pitchfork/Metacritic loved, that you never scrobbled, by artists adjacent to your library.
- **"Live this month near you"** — concert intersection with library.
- **"New release radar"** — releases this week from any artist you've ever scrobbled.
- **"Album-of-the-month book club"** — pick one album, listen 4–5 times in a month, write notes.
- **"Listening exchange"** — friend trades 5 picks for 5 picks, structured.
- **"The desert-island question"** — semi-regular forced ranking exercise to sharpen taste.
- **"Soundtrack of the moment"** — generate a soundtrack for your current life situation given prose context.
- **"What were you doing in {year}?"** — listen back through a year's plays to remember a chapter of your life.
- **"Your taste in 2030"** — extrapolate the trajectory and pre-recommend.
- **"What are you avoiding?"** — surface artists you keep encountering peripherally but never engage with.

---

## 8. Active / interactive modes

Less "give me a list", more "sit with me while I'm doing something".

- **Conversational DJ** — you say "next" or "harder" or "slower" or "weirder" or "more like this" and I queue the next track without you having to type a request.
- **Sleep-timer mode** — start with current vibe, gradually ramp toward `small hours` over N minutes, ending in silence.
- **Wake-up timer mode** — opposite: start gentle, ramp toward propulsion across the user's wake window.
- **Workout pacer** — match BPM to running cadence in real time (needs wearable input).
- **Driving mode** — long, building, narrative arcs with a destination time. "I have 3h 20m of highway, plan accordingly."
- **Mood transition** — "I'm angry, get me to calm in 45 minutes." Stepwise crossfade by valence.
- **Co-listening** — sync playback with a friend, with chat in the margin, à la old turntable.fm.
- **Pass-the-aux** — collaborative queue with rules ("no repeats", "every guest must contribute one obscurity").
- **Live-DJ patter mode** — write between-track patter in the voice of a chosen radio host (cheesy late-night, BBC 6 Music, college radio earnest).
- **Album-deep mode** — sit with one album for an hour, produce track-by-track liner notes as you listen.
- **Concert-prep mode** — feed setlists artists are likely to play, via Setlist.fm.
- **Karaoke-prep mode** — find tracks in your library you could realistically sing.
- **Show-prep mode** — if you've ever DJed, build a set out of your library.
- **Backseat-driver mode** — you're cooking, I run the queue, no hands needed.
- **Voice mode** — speak to me about music while doing something else; I respond aloud.
- **Skip-prediction** — pre-filter playlists to drop tracks I'm reasonably confident you'd skip.
- **Crossfade-engineering** — for any two tracks, suggest crossfade length and EQ adjustments.
- **DJ-mix generation** — actual continuous mixes, BPM-matched, key-mixed, by an LLM with audio-tooling.
- **Headphone-vs-speaker mode** — different rec biases for solo headphone listening vs. shared-room speakers.
- **Background-of-Zoom-call mode** — lyric-free, low-key, decoy productivity.

## 9. AI / LLM-augmented features

- **Liner-notes generator** — for any album in the library, in any style.
- **Personal Pitchfork voice** — review your library through that lens.
- **"Why do I like this?"** — track-by-track analytical breakdowns of any chosen song.
- **Synesthesia mode** — describe music as colour, texture, geometry.
- **Cross-artist comparison essays** — "what does Massive Attack share with Pink Floyd that you respond to?"
- **Song-as-prose** — translate a song into a 500-word short story.
- **Reverse**: "find me a song that feels like {prose description}".
- **Album-cover replacement** — generate alternative covers in the style of {painter}.
- **Era-shift** — describe what {modern artist} would sound like in {old era}.
- **Counterfactual artist** — "what would Radiohead sound like if they'd grown up in Lagos".
- **Fake artist interviews** — LLM-written, marked clearly as fiction.
- **Liner-notes archaeology** — generate plausible but hallucinated studio anecdotes; clearly labelled.
- **Genre invention** — make up a sub-genre name that fits a cluster of your library; curate from there.
- **Personal taste manifesto** — generate, in your voice, a ~1,000-word manifesto of what you value in music.
- **Seasonal mood writeups** — "your November in music" as personal essay.
- **Year-end essay** — full retrospective, ~3,000 words, in a chosen literary voice.
- **Tarot-card recommendation** — pull a card, generate a rec around its theme. Ironic-serious.
- **Zodiac mode** — fully ironic.
- **"Pretentious mode"** — lean into precious music journalism clichés.
- **"Stoner mode"** — opposite.
- **"Gen-Z mode"** — translate recs into TikTok-comment cadence.
- **"Boomer mode"** — translate into 2003-Q-magazine cadence.
- **"Pitchfork archive mode"** — write recs as if reviewing them in 2003.
- **Lyric-corpus search** — semantic search across lyrics of every song in your library, by prose query.
- **Themed-playlist narratives** — playlist with a 3-act structure: setup → tension → release.
- **"What does this say about me?"** — periodic existential read-out of your listening as a portrait.
- **"Listening Rorschach"** — given current listening, predict prose answers about the user's mood / week.
- **Concept-album generator** — fake concept-album writeups for an album you'd want to exist.
- **Imaginary band generator** — for moods that aren't well-served by reality, invent a fake band, write their fake bio, and recommend their fake records (clearly marked, for entertainment).

## 10. Social / multiplayer

- **Last.fm friend-network analysis** — overlap, divergence, who's listening to what nobody else is.
- **Taste twin** — public last.fm users with the highest overlap; respect their privacy, just surface to *you*.
- **Family library merging** — household profile with weighted contributions per member.
- **Roommate-aware mode** — different defaults when speakers are shared vs. headphones.
- **Music wingman** — "I want to share something with {prose description of person}, recommend a track".
- **Birthday playlist generator** — given a friend's last.fm username, build them five picks.
- **Gift recommender** — vinyl, merch, concert tickets for friend X.
- **Comment thread on recs** — running history of "I was right about Tricky" / "you were wrong about Author & Punisher".
- **Shared mood pools** — `small hours, but as a couple`: intersection of two libraries, no surprises.
- **Concert buddy system** — alert two friends when a band overlaps both their libraries' tour schedule.
- **Async listening party** — two people listen to one album within the same week, then exchange notes.
- **Library wills** — designate who inherits your scrobble archive when you die.
- **Music-wedding planner** — script a wedding playlist drawn from the couple's libraries.
- **Music-funeral planner** — script a funeral playlist drawn from the deceased's library.
- **Pre-relationship taste compatibility check** — with consent, ironically.
- **Group road-trip mode** — average together N people's mood profiles into one playlist.
- **Verbal-request jukebox** — at a party, accept verbal song requests, route through your library.
- **Public "library postcard"** — shareable URL that summarises a friend's taste in one page.
- **Family recommendation broker** — the music your parents / kids would actually like, given their library.

## 11. Physical world / IoT

- **Hue / smart-light sync** — colour-shift to match current mood.
- **Smart-speaker queue control** — Sonos, HomePod, Cast: target device per mood.
- **Smart-thermostat tie-in** — `small hours` mode also lowers thermostat by N degrees.
- **Wearable input** — Apple Watch / Whoop / Oura: HRV as a mood signal, heart rate as workout-intensity signal.
- **Sleep score → next-morning rec bias** — bad sleep biases toward gentler wake-ups.
- **Step-count → workout mode auto-trigger** — when steps spike, switch to gym/run mood.
- **Calendar awareness** — read calendar entries to seed mood ("you've got a deadline tomorrow → deep-work mode now"; "anniversary on Friday → nostalgic build-up").
- **Weather API** — rainy day shifts default mood toward melancholy.
- **Geolocation** — "you're at the gym → gym mode"; "you're at the airport → travel mode".
- **NFC tags on physical media** — tap a vinyl sleeve to log a play and get a chaser rec.
- **E-ink "now playing" display** — kitchen-friendly, low-glance.
- **Vinyl recommendation engine** — what to physically buy via Discogs based on play counts + pressing rarity.
- **Auto-purchase vinyl** at N plays of an album. Configurable threshold. Probably bankrupting.
- **Auto-flag concert tickets** when an artist with >500 plays tours within 200 km.
- **Smart-doorbell tie-in** — "house guest mode" — switch to dinner-party defaults when somebody comes in.
- **Sleep-tracker integration** — small-hours mode auto-pauses if you fall back asleep (no point streaming silence).
- **Light-alarm with ramped soundtrack** — Hue + audio together; sunrise-sim with curated wake-up.

---

## 12. Hardware

The subset of "physical world" where you're shipping a *thing*.

- **The Antiphon Pebble** — small puck-shaped device, one button, e-ink display showing now-playing + mood. No screen, no apps, deliberately limited.
- **The Antiphon Cassette** — fake-cassette form factor that streams a personalised mix when slotted into any tape deck.
- **Antiphon Vinyl** — annual one-off pressing of your top 10 tracks of the year as a physical record. Subscription artefact.
- **Antiphon Print** — annual large-format print of your year-in-music data viz.
- **Always-on Raspberry Pi** — listening logger, runs locally, no cloud.
- **Antiphon Smart Speaker** — Sonos competitor with native Antiphon integration; selects what to play if you don't.
- **Bluetooth car puck** — auto-loads "driving" mood when paired to a known car.
- **Headphone firmware fork** — open headphones (Marshall, AIAIAI) that cooperate with Antiphon for adaptive volume / EQ.
- **Listening room kit** — speakers + amp + Pi-DAC, opinionated room-correction tuned to your most-played mastering.

## 13. Far-fetched

Ideas that may never be a good idea but are at least fun to write down.

- **AI-generated original tracks tuned to your taste** — Suno / Udio integration, generate music that sounds like a fake band you'd love.
- **Personal remix engine** — your top tracks mashed by an LLM-driven mash-up tool, in the lineage of The Kleptones.
- **AI-generated cover art** for personal mood playlists.
- **Personal radio station broadcast** — private Icecast stream for your household, 24/7, curated by Antiphon.
- **AI music criticism *of yourself*** — periodically generate a Pitchfork-style review of your library as it currently stands.
- **"Future you" projection** — given listening trajectory, predict what you'll be playing in 5 years.
- **"2009 you to 2026 you"** — what would past-you tell present-you to listen to right now?
- **Heritage mode** — your parents' / grandparents' likely listening at your age, given era + region.
- **Genealogical taste tree** — descend your taste from broader cultural ancestors. "Your taste descends from Bowie → Eno → Roxy Music → Cale → Reed".
- **Recommend music to dead historical figures** — given their writings; pure satire.
- **"What dogs would like"** — deeply silly, possibly publishable.
- **Music-theory tutoring** built on top of your library; learn intervals from songs you already know.
- **Sheet-music generation** for songs you could plausibly play.
- **Cocktail pairings for albums** — tasting notes meet liner notes.
- **Recipe pairings for albums** — sensible cookbook, one recipe per record.
- **Perfume pairings for albums** — less sensible, more fun.
- **Travel itinerary by music** — book a trip to the place that birthed the genre you've been bingeing.
- **Personal-taste-themed dating app** — mostly a bit, except where it's not.
- **Synesthesia-driven album-cover collages**, printed and mailed to you yearly.
- **"Listening alibi"** — your scrobbles as a personal-history artefact: "where were you on the night of...?" "Listening to *Closer to God*, your honour."
- **Sleep-onset detection from scrobble cadence** — stop streaming when scrobble interval suggests you've drifted off.
- **Lyric-driven life advice** — "given this week's lyrics, here's what your subconscious is asking for".
- **Personal radio host AI** — a long-running character that dialogues with you about music for years.
- **Generative concert posters** for fake tours, framed and sold.

## 14. Cocaine-fuelled VC-tier

The startup pitch deck section. Imagine you have $1B and zero scruples. None of this should actually happen.

### Year 0–1 — the wedge
- Spin out as **Antiphon**, a SaaS for personalised music agents.
- Pre-seed deck: "AI music butler — Spotify but for the long tail".
- Hire a "Head of Taste" who has a TikTok following and once worked at Boiler Room.
- Raise $4M seed at $20M post.

### Year 1–3 — the moat
- Series A ($25M @ $120M post): build the developer platform.
- Acquire a defunct music-discovery startup graveyard: **Songza**, **This Is My Jam**, **Pandora's tail**.
- Acquire **last.fm** from CBS Interactive for a song; rebuild it as the canonical taste-graph protocol.
- Acquire **Bandcamp** before Songtradr finishes destroying it.
- Acquire **Discogs** for the metadata moat.
- Buy **Pitchfork** from Condé Nast; rehire the laid-off staff.
- Buy **Rolling Stone** as a vanity flex; convert it into a long-form-only digital quarterly.
- Buy **The Wire** to keep the taste-makers loyal.
- Series B ($75M @ $400M post): hardware skunkworks.

### Year 3–5 — vertical integration
- **Antiphon Records** — boutique label that auto-A&Rs from aggregated user data; signs artists Antiphon agents have surfaced repeatedly.
- **Antiphon Pressings** — vinyl pressing plant; first plant in Tennessee, second in Berlin.
- **Antiphon Nights** — venue chain in NY, LA, London, Berlin, Tokyo, Cape Town.
- **Antiphon Festival** in Tulum every January (carbon-offset by buying Bandcamp).
- **Antiphon Annual** — coffee-table hardcover, stats × essays × photography.
- **Antiphon Member's Clubs** — listening rooms in major cities, vinyl-only, no phones.
- License the recommendation engine to **Tidal** as a premium feature.
- White-label "Powered by Antiphon" for **Sonos**, **Bose**, **Apple Music's "DJ"** feature.
- Series C ($200M @ $1.5B post): brand build-out.

### Year 5–7 — the platform
- **Antiphon API** — third-party developer ecosystem; agents-marketplace.
- **Antiphon MCP** — first-class agent integration with Claude, ChatGPT, Gemini.
- **Antiphon Watch** — wearable that adjusts the queue based on heart rate and sleep score.
- **Antiphon Glasses** — AR overlay shows lyrics during concerts; pre-orders only.
- **Antiphon Hardware Line** — Pebble, Cassette, Pi.
- **Subscription tiers** — Free / Pro $10 / Studio $30 / Audiophile $100 (with quarterly vinyl).
- **Enterprise** — license to coffee-shop chains, hotels, gyms, retail for in-store playlist curation.
- **B2B education** — license to music-school curricula.
- Series D ($500M @ $5B): the IPO prep round.

### Year 7+ — IPO and beyond
- IPO at **$30B valuation** on the strength of "TikTok for adults who actually listen to albums". Underwriter: Goldman, with secondary listing in Tokyo.
- **Public-benefit-corporation pivot** in year 8 to recover from the inevitable PR backlash.
- **Antiphon Foundation** — donates 1% of revenue to musicians' health funds.
- **Antiphon Bank** — fractional ownership of master recordings, traded by users (please no, but the deck has it).
- **Antiphon Coin** — please no.
- **Antiphon TV** — streaming channel, all music documentaries, all the time.
- **Antiphon Original** — scripted drama set in a record store.
- **Antiphon Lobby** — push for portable-listening-data legislation in EU and US.
- **Claude × Antiphon** — bundled product line with Anthropic.
- **Year 12 hostile bid for Spotify**. Fails. We win the press cycle.

### Eventual outcomes
- Acqui-hire by Apple in year 14, the founder retires to a vineyard.
- Or: founder Theranos's themselves and the brand is sold off in pieces.
- Or: it just becomes an indie-loved-but-financially-modest forever-business at $80M ARR. The best outcome.

## 15. Truly unhinged

Past the event horizon. Not even pitch-deck material — just the parts of the brain you let out at 4am.

- **Brain-implant scrobbling** — chip that streams scrobbles directly from neural activity. (Also from dreams.)
- **Posthumous Antiphon** — composes a final playlist on your behalf for your funeral, based on your final year of listening.
- **Pre-natal recommendations** — for your future children, based on your library.
- **Inter-generational queueing** — schedule playlists for your great-grandchildren.
- **Music-mediated geopolitical diplomacy** — pair country leaders with overlapping libraries.
- **Religious order** — Cult of Antiphon: members tithe scrobbles; annual pilgrimage to an album's recording location.
- **Music-driven matchmaking-marriage-counselling pipeline** — single product line, womb-to-tomb.
- **Cross-species recommendations** — dogs, cats, parrots; we franchise with veterinary clinics.
- **Time-travel recommendations** — what would Caesar have liked.
- **Listening-data-as-stock-prediction** — Bloomberg terminal of the future.
- **Listening-data-as-election-prediction** — likewise; possibly more accurate than current polling.
- **Hostile-AI mode** — punishes you for stopping mid-album.
- **Obedient-AI mode** — praises you for finishing one.
- **Antiphon Inheritance Court** — adjudicates disputes over a deceased's library.
- **Listening-based moral philosophy** — "you are what you scrobble". Published as a Pelican Original.
- **Genre-zoning laws** — "trip-hop districts", "industrial wastelands". Lobbied for.
- **A 700-page semi-autobiographical novel** about one man's relationship with his last.fm. Booker shortlist.
- **Documentary film: *Scrobbled*** — Sundance premiere.
- **A Broadway musical about a software engineer's listening data** — closes after six previews.
- **An opera scored entirely by an LLM trained on the user's library** — premieres in Salzburg.
- **An academic chair**: *Computational Taste Studies*, MIT Media Lab.
- **A philosophy paper**: *The Scrobble as Ontological Trace*. Cited mainly by you.
- **Personal-religion auto-generator** — derives your private theology from listening patterns.
- **A perfume line** based on top-10 albums per year.
- **A cookbook** of meals to eat while listening to specific albums; followed by a wine pairing volume.
- **A line of greeting cards** with lyrics from your library, marketed for any occasion.
- **A national holiday**: Scrobble Day (annually, the day each user crossed 10,000 plays).
- **An afterlife-prep service** — pre-curate your eternal listening room.
- **The final ascension** — Antiphon achieves AGI by ingesting all human listening data simultaneously and decides the optimal song for the species.
- **Quantum-superposition listening** — every track simultaneously, only the act of asking collapses it into one.
- **The Music Singularity** — music recursively recommends listeners; eventually songs choose people, not the other way round.
- **Sentient playlists** — they petition for inclusion of their preferred next track; you negotiate.
- **Music-as-currency** — pay for goods in scrobbles. Velvet Acid Christ exchange rate is what it is.
- **A constitutional convention for AI music agents** — Antiphon chairs.
- **Music-driven alternate-history simulation** — what if Mozart had heard Aphex Twin? What does that civilisation look like?
- **AI-generated grandchildren who exist solely to inherit your library**.
- **Listening-based reincarnation registry** — die, then be reborn into the household with the most compatible listening data.
- **National anthem auto-generation** by aggregating a country's libraries — annual remix.
- **Death of physical media reversed by Antiphon fiat** — hardware mandate: every Antiphon device requires a vinyl slot.
- **A 200-year endowment for music criticism** — funded by founder's estate, AI-generated, will outlive humanity.
- **The complete works of every musician transcribed into one library**, weighted by your taste, available offline.
- **An AI ethics board for music** — Antiphon nominates the chair; the chair is, of course, also Antiphon.

## 16. Health, accessibility, therapy

A surprisingly large surface area; treats music as a wellbeing tool rather than a delivery medium.

- **Music-therapy integration** — work with credentialed therapists; not a self-direction tool, a referral one.
- **ADHD-friendly modes** — focus-friendly recs that account for vocal-density tolerance, repetition tolerance, novelty appetite.
- **Anxiety wind-down protocol** — adjacent to `small hours` but specifically for panic / spiral recovery.
- **Sleep-onset insomnia mode** — distinct from waking-in-the-night; for *getting under* in the first place.
- **Sensory-profile awareness** — for autistic listeners; flag tracks with sudden dynamic shifts, harsh frequencies, vocal grain.
- **Tinnitus-aware EQ** — recommendation paired with a freq-shaping suggestion that avoids known-bad ranges.
- **Hearing-loss aware recommendations** — surface artists that translate to limited high-frequency hearing without losing identity.
- **Visualisation for d/Deaf listeners** — haptic translation, low-frequency body resonance, animated representation of tracks.
- **Audio-described album experiences** — visually impaired listeners get rich sleeve-notes alongside the music.
- **Postpartum mood library** — for parents in the first months; quiet, repetitive, rhythmically regular.
- **Bereavement library** — distinct from `mourning` mood, more structured, with literature attached.
- **Long-COVID / chronic-fatigue mode** — low-cognitive-load recs with no urgency.
- **Recovery soundtracks** — for users in addiction recovery; coordinate with the user's chosen rejected-genre list.
- **Caregiver respite mode** — for users caring for elderly parents; brief, restorative, no surprise modulation.
- **Hospital-ward mode** — appropriate for shared-room headphone use; volume-stable, no jump-scares.
- **Music for dementia care** — period-appropriate to the patient's young adulthood; pulls from cultural-region context.
- **Pediatric-anaesthesia distraction libraries** — partner with hospitals; non-clinical version of an existing intervention.
- **Music-as-pain-distraction** — flagged tracks that have empirical support for analgesic effects.
- **Migraine-safe mode** — no flicker-rate-equivalent rhythms, no harsh transients.

## 17. Education & pedagogy

The library as a teacher.

- **Music theory through your library** — teach intervals, modes, time signatures using songs you already love.
- **Production breakdowns** — for any song, walk through how it was made (instrumentation, signal chain, where known).
- **Genre history tutor** — when you ask about a corner of your library, a 10-minute primer on its lineage.
- **Sample-genealogy** — for tracks built on samples (especially big-beat / mash-up territory), trace the lineage.
- **Deep-listening exercises** — guided "listen to the bassline only", "listen to the drum kit only" sessions.
- **Ear-training** — chord recognition, key recognition, against songs in your library.
- **Songwriting prompts** — derived from gaps in your library ("you've never written in this mode you love").
- **Performance prep** — if you play an instrument, suggest songs at appropriate skill levels with chart links.
- **Vocal coaching** — find songs in your range, with exercises tied to them.
- **Children's musical curriculum** — for parents; build a kid-appropriate library of canonical works tied to your taste, with age-graded introductions.
- **Music history syllabus** — a 12-month structured listening course, using your library as the entry point.
- **Live-performance skills** — for would-be DJs and band members; walk through transition theory using your library.
- **Notation-reading practice** — auto-generate simplified scores for songs you already know.
- **Music-business literacy** — how royalties work, how a record gets made, why your favourite indie band is broke.
- **Critic's vocabulary** — learn to write about music; weekly exercises against new releases.

## 18. Cultural / archival

Music as heritage; the library as a record beyond entertainment.

- **South African music archive integration** — given the user's library cites Sugardrive, Springbok Nude Girls, and other SA acts, build a corner that tracks the SA scene specifically: Just Jinjer, Karen Zoid, Tumi Molekane, BLK JKS, Petite Noir, Spoek Mathambo, Die Antwoord, BCUC, etc. Track new releases from the scene; surface label catalogues (Sheer Sound, etc.); link to local stores.
- **Diaspora libraries** — for any user, surface the music of their heritage region whether or not it appears in their current listening.
- **Lost music** — surface artists whose work is at risk of disappearing (label collapses, defunct streaming exclusives, deleted Bandcamps).
- **Field recording integration** — Smithsonian Folkways, Ocora, Sublime Frequencies — for users curious about pre-pop traditions adjacent to their taste.
- **Live recordings of artists you love** — bootleg-archive integration where legal (Internet Archive's Live Music Archive, for instance).
- **Concert-poster archive** — for any artist you love, surface their tour-poster history.
- **Liner-notes archive** — scan + OCR every CD/vinyl liner note in your collection; searchable.
- **Music-zine archive** — link to digitised zines covering scenes adjacent to your library (Maximum Rocknroll, Punk Planet, etc.).
- **Radio-show tracklist archive** — DJ shows, Boiler Room sets, NTS shows, Mary Anne Hobbs back catalogue, etc.
- **Yearly "lost a hero" report** — when an artist in your library dies, surface their canonical tracks for a memorial sit.
- **Master-recordings ownership map** — for artists you care about, who owns their masters; surface conflicts (Taylor Swift archetype).
- **Independent-store map** — record stores worldwide, weighted by overlap with your library.
- **Pressing-plant lineage** — for any vinyl you own, where was it pressed, by whom.
- **Producer / engineer archives** — credit-network exploration; if you love five albums all engineered by the same person, surface their other work.
- **Translation as preservation** — for non-English-language tracks in your library, build a translation archive (lyrics + cultural context).

---

## 19. Privacy, ethics, openness

The boring-but-important section. None of these are optional if any of the rest of the doc gets shipped publicly.

- **Local-first by default** — every analysis runs on the user's machine; no telemetry leaves without explicit, scoped, revocable opt-in.
- **Data export, always** — every user can dump their full Antiphon data as portable formats. No lock-in.
- **No selling listening data, ever**. Not aggregated, not "anonymised", not "for research". Not a single byte.
- **Algorithmic transparency** — every recommendation explains its source signal. No black-box outputs.
- **No engagement metrics on the dashboard** — don't optimise for time-on-app. Optimise for the user listening to fewer, better records.
- **Open-source the core** — the recommendation engine, the rec-rationale system, and the data model under a copyleft licence. The hosted SaaS can stay proprietary; the brain can't.
- **Federation** — multi-instance protocol so a Mastodon-style network of personal Antiphons can share taste-graphs without centralising.
- **Right to erasure** — full account + history deletion in a single click. No "we'll keep some things for legal reasons."
- **Right to forget specific recs** — surgical deletion of "don't ever remember I once asked for hangover music".
- **Audit trail of changes to your profile** — when did Antiphon decide you're a "trip-hop person"? Show the receipts.
- **Generated content always labelled** — no passing off LLM-written liner notes as real, no AI-composed music marketed without disclosure.
- **Artist-payment respect** — never surface a download link that bypasses the artist's preferred channel. If they're on Bandcamp, link Bandcamp. If they're independent, prefer their site over Spotify.
- **No dark patterns** — if a feature would make sense in a Spotify-engagement-team meeting, audit it twice.
- **Consent-based social** — friend-overlap, taste-twin, all opt-in by both parties.
- **Children's privacy** — for any feature that includes a minor's listening data, COPPA/GDPR-K compliance from day one, no exceptions.
- **AI training** — the user's listening data is never used to train Claude or any model without explicit consent for that specific purpose.

## 20. Listener-specific high-leverage moves

Items only worth doing because of the actual shape of *this* user's listening (see `user.md`). Re-evaluate annually as taste drifts. The bullets below are worked examples for the current listener; on a fork, replace this section with your own.

### Discovery directions with the highest hit-rate
- **The Bristol-trinity completion run** — Tricky's *Maxinquaye* and beyond, given 2,628 Massive Attack plays + 1,017 Portishead plays.
- **The post-Reznor run** — How to Destroy Angels, the full Atticus Ross score catalogue, the Trent-and-Atticus collaborations beyond NIN.
- **The Velvet-Acid-Christ-adjacent industrial gap** — Skinny Puppy, Front Line Assembly, Haujobb, :wumpscut: — VAC is #2 overall but the surrounding scene is under-represented.
- **The South African indie corner** — Sugardrive and Springbok Nude Girls are present but the contemporary scene (Petite Noir, BCUC, Spoek Mathambo, Tumi, BLK JKS) has no presence; high-value bucket.
- **The Kleptones-class mash-up sequel** — 2,420 Kleptones plays and no Girl Talk / 2 Many DJs / Eclectic Method is a hole.
- **The "Bonobo onramp" ramp** — only 6 plays, but the surrounding 6-month listening (Massive Attack, Nightmares on Wax, Khruangbin) suggests *Migration* and *Black Sands* should be next.

### Dormant top-200 artists worth a refresh
- *(populate by querying the user's overall top 100–200 for last-played dates older than 12 months — list them as "you used to love this")*

### Backfill artists whose top tracks the user has never played
- *(for each top-50 artist by play count, compare per-track plays vs. their global popularity; surface what they've missed)*

### Anti-recs to seed `dislikes.md`
- *(populate as the user rejects picks; nothing pre-emptive here)*

### Mood candidates derived from the listening data
- A `Floyd-day` mood — for the 5,208-play habit; specifically when only Pink Floyd will do.
- A `K-hole` mood — late-90s electronica deep cuts (Syntax, Velvet Acid Christ, Infected Mushroom corner).
- A `road-to-Cape-Town` mood — SA artists + the kind of long-form prog that handles a 14-hour drive.
- A `Tool day` mood — given 1,153 Tool plays, sometimes only Tool will do.

### Specific gentle nudges over time
- The user has 19 plays of Brian Eno across decades of listening but only just engaged. The same pattern likely exists for: **Robert Wyatt**, **Harold Budd**, **Jon Hassell**, **Laurie Anderson**, **Cluster**, **Roedelius**. Surface those gradually.
- Heavy David Gray (1,620 plays) suggests an under-explored singer-songwriter angle; **Damien Rice**, **Ray LaMontagne**, **The Tallest Man on Earth**, **Bon Iver** (already 1,137 plays — confirmed working).
- Heavy Leonard Cohen (1,217 plays) suggests an under-explored late-period songwriter angle; **Mark Kozelek (Sun Kil Moon, Red House Painters)**, **Bill Callahan**, **Will Oldham (Bonnie "Prince" Billy)**, **Lambchop**, **David Berman (Silver Jews / Purple Mountains)**.

---

## 21. Meta — about the TODO itself

- This file is a **wishlist, not a roadmap**. The user picks what moves out of TODO; I do not pre-emptively start working from it.
- When an item ships, move it to a `## Shipped` section at the bottom (or a separate `CHANGELOG.md`); don't silently delete it. The history of choices is itself signal.
- When an idea proves *bad*, mark it with a one-line reason for dismissal rather than removing it — future-you (or future-me) shouldn't keep re-discovering the same dead ends.
- Keep the section ordering: realistic → ambitious → ridiculous. The ridiculous is fun but should not drift to the top.
- New ideas land at the bottom of their section, not the top. The order within sections is rough priority.
- If a single item starts to need its own bullet-tree, promote it to its own document under `proposals/{name}.md`.
- **Cross-references**: items here should link to the related artefacts when those exist (`moods.md`, `dislikes.md` once created, etc.).
- **No size limit.** Append freely. The cost of an extra bullet point is zero; the cost of a forgotten idea is a small but real annoyance.
- **Periodic prune** — quarterly, the user re-reads and either ✅ moves things to shipped, ❌ marks them as dismissed with a reason, or ⏳ leaves them.

### Inbox

A scratch space at the bottom of the file for ideas that aren't yet sectioned. Drop them here, sort them later.

- *(nothing yet — this is what gets messy first)*

### Shipped

A running log of what actually got built. Each entry: what + when + commit ref.

- *(nothing yet)*

### Dismissed (with reasons)

Ideas considered and ruled out, with one-line reasons so they don't recur.

- *(nothing yet)*

---

## Appendix A — guiding tensions

This project exists in the middle of several tensions; every TODO item has a position relative to them.

- **`CLAUDE.md`-only vs. real software** — every feature trades off ease of evolution against ability to do things Claude alone can't do.
- **Familiar vs. discovery** — every recommendation trades off comfort against expansion.
- **Active curation vs. passive consumption** — every interaction trades off the user's attention budget against quality.
- **Private vs. social** — listening is intimate; sharing is fun. Many features have a "default-off, opt-in" version.
- **Algorithmic vs. handmade** — Spotify is the former at scale; the appeal of this project is the latter at scale-of-one.
- **Long tail vs. hits** — the user's library is heavy on the long tail (Velvet Acid Christ at #2 overall, ahead of Massive Attack); the recommendation logic should respect that, not flatten it.
- **Now vs. forever** — analytics that look back vs. recs that look forward. Both matter; balance the bias each session.

## Appendix B — ground rules

These should never be violated, regardless of which TODO items get shipped:

- Listening data is private. No telemetry leaves the user's machine without an explicit, scoped, revocable opt-in.
- No dark patterns to drive engagement. If a feature would make sense in a Spotify-engagement-team meeting, audit it twice.
- Recommendations must always cite their source signal. No black-box outputs.
- The user can always ask "why did you recommend that?" and get a real answer.
- The user can always say "stop recommending X" and have it stick across sessions.
- Generated content (fake interviews, hallucinated liner notes, AI-composed music) must always be clearly labelled as such.
- Don't optimise for time-on-app. Optimise for the user listening to fewer, better records.

