# Lights On, Nobody Home (Latin punk)

An original song for a Latin band of acoustic-sounding instruments, about 2:53, made with
[Valis](https://github.com/valis). The verses are bright and upbeat in the manner of mariachi and son
([La Bamba](https://en.wikipedia.org/wiki/La_Bamba_(song)) and the [Macarena](https://en.wikipedia.org/wiki/Macarena_(song))
were the starting points for the mood): a nylon guitar, a vihuela, a guitarron, a harp, trumpets in thirds and hand
percussion, in C major. The chorus jumps a whole step up into D Hungarian minor
(D E F G# A Bb C#, https://en.wikipedia.org/wiki/Hungarian_minor_scale) and turns punk: eighth-note downstrokes,
a snare, a floor tom and a crash, with a chanted "blank, blank, blank, blank".

The words are a run of slang for someone who is not very bright ("the lights are on but nobody's home"), in
[`docs/lyrics.md`](docs/lyrics.md). They contain swearing. The vocals are left to be recorded.

128 bpm, 92 bars, a regular pop form:

| Bars | Section |
|---|---|
| 1 to 8 | Intro: guitar and claves, then the band, with the trumpets playing the verse tune |
| 9 to 24 | Verse 1 |
| 25 to 28 | Pre-chorus: F G Bb A7, a snare roll, a harp run up |
| 29 to 36 | Chorus 1 (key change) |
| 37 to 52 | Verse 2: picked guitar and violins join |
| 53 to 64 | Pre-chorus, Chorus 2 |
| 65 to 72 | Bridge: a trumpet solo in thirds over a harp |
| 73 to 88 | Chorus 3, sixteen bars |
| 89 to 92 | Outro: back in C, one last hit |

## Parts

| Part | Circuit (in the Valis repository) |
|---|---|
| shakers | `examples/latin-perc.ttl`: maracas, cabasa, guiro, claves, cowbell |
| congas | `examples/latin-perc.ttl`: congas, bongos |
| kit | `examples/latin-perc.ttl`: bass drum, snare, floor tom, crash |
| guitarron | `examples/guitarron.ttl` |
| vihuela | `examples/nylon-guitar.ttl`, played high and strummed |
| guitar | `examples/nylon-guitar.ttl`, played in the middle and picked |
| harp | `examples/harp.ttl` |
| trumpets | `examples/trumpets.ttl`: four lip-reed voices |
| violins | `examples/violins.ttl`: four bowed-string voices and a violin body |

The guitars, the guitarron and the harp are a plucked-string exciter (`val:Pluck`, new for this song) driving a
physical model of a string (`val:StiffString`), with the pluck harder or softer and nearer the bridge or the middle
as the instrument needs. The trumpets are a physical model of a lip-reed brass instrument (`val:Brass`), and the
violins are bowed-string physical models (`val:Bow`) behind a violin body; both start their vibrato after the note
has begun, as a player does. The drums, congas, bongos, claves, cowbell and crash are struck modal resonators
(`val:ModalBank`: a circular membrane, wooden bars, a plate), and the maracas, cabasa and guiro are `val:Shaker`,
which models particles colliding in a shell. Every part is played with small random variations in timing and
loudness, and the mix has a synthetic room.

## Layout

* `docs/lyrics.md` words, with the bar numbers
* `docs/vocal-guide.md` the notes to sing, one per syllable, with bar, beat and length; also `midi/vocal-guide.mid`
* `midi/` one file per part
* `wavs/` one stem per part, about 70 MB each, so they are not in git: rebuild them with the command below
* `mixes/lights-on-nobody-home-v3.flac` the latest reference mix (24-bit FLAC, 38 MB), made by number rather than by ear
* `mixes/lights-on-nobody-home-v3-with-guide.mp3` the same mix with the guide voice added, for learning the tune
* `mixes/...-v2...` the previous version, kept for comparison. v3 lets plucked notes ring after the finger lifts, gives
  the strings a body and damps their high harmonics faster than the low ones, and gives the guitarron a fuller tone

Rebuild with `python3 scripts/lights-on-nobody-home/track.py`, and the vocal guide with
`python3 scripts/lights-on-nobody-home/vocal-guide.py` (both need a built Valis, `VALIS=/path/to/valis`).

## Status

Measured, not heard. Every stem has no NaN and plays where the score says. Over the notes the song uses, the guitars,
guitarron and trumpets are within 15 cents of the note asked, and the violins within 1 cent for most notes and 13
cents at the top. The harp is about 10 cents sharp above C5. In the trumpets, a harder blow gives a brighter tone
(measured: 835 Hz to 1025 Hz spectral centroid at 262 Hz, 1238 Hz to 1616 Hz at 440 Hz), which a filter on a saw wave
did not do. Every percussion note is silent before it is played. In the mix the choruses are about 3.5 dB louder than
the verses, and the chorus has G# where the verse has none, which is the key change.

Not yet done: the whole needs listening to. The balance, the punk feel of the chorus and how convincing the
trumpets, violins and percussion are all unheard, and the user judged the first version to sound like a keyboard
preset, so this version may still fall short. No sleeve has been made.
