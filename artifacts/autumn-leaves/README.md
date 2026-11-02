# Autumn Leaves (acid rock)

An original acid rock / psychedelic arrangement of the chord changes of "Autumn Leaves", about 5:12 long,
made with [Valis](https://github.com/danja/valis). The reference file `sources/autumn-leaves/Autumn-Leaves.mid`
supplied the key (G minor) and the cycle of chords. The call lines are new and do not use its melody.
The brief is in `sources/autumn-leaves/prompt.md`.

Key G minor, 112 bpm, 144 bars. Two bars to a chord, sixteen bars to a cycle:
Cm7, F7, Bbmaj7, Ebmaj7, Am7b5, D7, Gm, Gm.

| Section | Bars | Content |
|---|---|---|
| intro | 8 | drums and percussion come in, organ drone on G |
| verse | 16 | kick, kit, bass, held organ chords (rotating speaker slow) |
| call | 16 | horn stabs and the fuzz lead's call lines join |
| jam | 32 | organ chugs with the speaker fast, the lead stops after 16 bars to leave room for a guitar |
| break | 8 | kit and bass drop out, organ and one long lead note in the echo |
| return | 32 | everything again, speaker fast and lead an octave up for the second cycle |
| climax | 16 | horns every bar, lead answers itself |
| outro | 16 | strip back to a drone and a fading kit |

## Parts

| Part | Circuit (in the Valis repository) | Notes |
|---|---|---|
| kick | `circuits/dmx.ttl` | its own stem |
| drums | `circuits/dmx.ttl` | hats, snare, toms and fills |
| perc | `circuits/dmx.ttl` | shaker, tambourine, wood block |
| bass | `circuits/psych-bass.ttl` | saw and sub square, ladder filter, fuzz |
| organ | `circuits/tonewheel-organ.ttl`, then `circuits/leslie.ttl` | the rotating speaker's speed is `midi/leslie-speed.mid` |
| horns | `circuits/horn-section.ttl` | stabs |
| lead | `circuits/fuzz-lead.ttl` | fuzz, glide, dotted-eighth echo; gaps left for a guitar |

## Layout

* `midi/` one file per part, plus `leslie-speed.mid`
* `wavs/` one stem per part, including `organ.wav` (dry) and `organ-leslie.wav`. About 90 MB each, so they are not in
  git: rebuild them with the command below.
* `mixes/autumn-leaves.flac` a reference mix (24-bit FLAC, 60 MB), made by number rather than by ear

Rebuild with `python3 scripts/autumn-leaves/track.py` (needs a built Valis, `VALIS=/path/to/valis`).

## Status

Measured, not heard. The stems have no NaN and no silence where a part plays, the pitched parts are within a few
cents of the note asked (the lead sits 10 cents sharp because its second oscillator is detuned on purpose),
and the rotating speaker's horn rotor was measured at 0.8 Hz slow and 6.8 Hz fast. The mix balance, the fuzz
levels and the Leslie speed changes still need listening to. The speaker's speed changes were not
checked against the drum rotor, which takes about five seconds to reach full speed.
