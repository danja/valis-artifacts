# Asturias Industrial

An industrial dubstep take on Isaac Albéniz's "Asturias (Leyenda)", 140 bpm in E minor, 64 bars (1:50),
for the heavy side of the year 2000's idea of the future. The Asturias arpeggio survives as a fast top-note
line and a fuzz lead over a wobble bass, an industrial kick, a 909 kit, metal percussion and a nylon guitar
that quotes the theme. The harmony nods to the original (`Em B7 Em C B7 Em`); the material is new. The brief
is in [`../../sources/asturias-industrial/prompt.md`](../../sources/asturias-industrial/prompt.md).

Everything here is **measured, not heard**. What still needs a listener is listed at the end.

* [`mixes/asturias-industrial-v9.flac`](mixes/asturias-industrial-v9.flac): the mix. -10.0 LUFS integrated,
  loudness range 9.1 LU, true peak -3.8 dBTP, no clipped or non-finite samples.
* `midi/`: `kick`, `kit`, `bass`, `lead`, `arp`, `guitar`, `metal`, `riser`.
* `circuits/`: ten circuits, all copied from the Valis examples (`nursery-humpty-kick`, `909`, `halloween-bass`,
  `fuzz-lead`, `sh101`, `nylon-guitar`, `metal-clang`, `nursery-wind-up-riser`, `reverb-return`, `dub-delay`).
* `wavs/`: the stems and the two effect returns (not in git).
* Made by [`../../scripts/asturias-industrial/make.py`](../../scripts/asturias-industrial/make.py).

## Shape

| Bars | Time | Section | What plays |
|---|---|---|---|
| 1-8 | 0:00 | intro | kick on the one, the Asturias arpeggio as a top-note line, the nylon guitar quoting the theme |
| 9-16 | 0:14 | build | kick, arpeggio, metal hits, a riser climbing for the whole section |
| 17-32 | 0:28 | **drop 1** | kick, kit, wobble bass, fuzz lead, arpeggio, metal |
| 33-40 | 0:55 | break | guitar and arpeggio only, no kick, no bass |
| 41-48 | 1:09 | build 2 | as build |
| 49-56 | 1:23 | **drop 2** | as drop 1 |
| 57-64 | 1:37 | outro | guitar and arpeggio thinning, then a 6 s fade |

Two drops, two risers. The drop lands on a four-to-the-floor kick with the wobble bass on the one.

## The material

* Harmony: `Em B7 Em C B7 Em`, a chord a bar, repeated. The arpeggio line follows the top note of each chord.
* Asturias arpeggio: the top note of each chord, played in sixteenths, is the surviving trace of the original
  tremolo figure.
* Bass: the root of each chord, on the one, with a wobble LFO on the filter cutoff.
* Lead: the top note, on the one of each bar, with a glide.
* Metal: one hit on the last sixteenth of every bar.
* Guitar: the chord voicing, an octave up, on the one of every other bar.

## The instruments

| Circuit | What it is |
|---|---|
| `nursery-humpty-kick.ttl` | A kick named for Humpty Dumpty's fall: a sine and a six-mode drumhead resonator fall together from a high pitch. |
| `909.ttl` | The TR-909 kit from the Valis examples, unchanged. |
| `halloween-bass.ttl` | Three bass layers on one voice: a sine sub an octave below, detuned saws through a wobbling ladder filter, and a clipped wavetable growl. Written for dubstep half-time. |
| `fuzz-lead.ttl` | A monophonic lead: saw and sharp square through a resonant ladder, vibrato, then a heavy fuzz. |
| `sh101.ttl` | The Roland SH-101 model, used for the fast arpeggio line. |
| `nylon-guitar.ttl` | A six-voice nylon-string guitar. |
| `metal-clang.ttl` | Metal bashing: a damped sheet and a hammer, for an industrial clang. |
| `nursery-wind-up-riser.ttl` | A riser on a 5 s envelope: a guiro that speeds up to a buzz, noise through a ladder whose cutoff climbs, a saw rising from A2 to A6. |
| `reverb-return.ttl` | The Valis reverb return, unchanged. |
| `dub-delay.ttl` | The Valis dub echo, at its 85 bpm setting. |

## The mix

`valis-song mix song.ttl --version v9 --arc`. Earlier working mixes are v1 to v8.

| | |
|---|---|
| Integrated loudness | -10.0 LUFS (target -10, reached without leaning on the limiter) |
| Loudness range | 9.1 LU |
| True peak | -3.8 dBTP |
| Peak / RMS | -3.83 dBFS / -12.42 dB |
| Clipped samples / non-finite | 0 / 0 |
| Stereo correlation | 0.966, median width -17.8 dB, balance +0.37 dB |
| Spectral centroid | 408 Hz; 2.7% of the power above 2 kHz |

Section levels as mixed: intro -13.9, build -15.0, drop 1 -10.5, break -13.2, build 2 -14.9, drop 2 -10.0,
outro -17.6 dB.

Stem checks (`valis-song stems`): all ten found, every bar that the score gives notes has sound, no problems
reported. Playing rms of the stems before levelling: kick -16.3, kit -17.1, bass -23.8, arp -12.3, lead -28.2,
guitar -31.5, metal -27.8, riser -29.6 dB. The kit peaks at 1.000 on its limiter.

## Measured and not heard

* The tempo detector reads 140.06 bpm (strength high). The track is at 140 bpm, so this confirms the pulse.
* The key detector reads F# major (0.77). The track is in E minor; the detector is unreliable on industrial
  material, and the wobble bass and metal percussion pull it away from the harmony.
* All instrument stems are mono (correlation 1.000). The width in the mix comes only from pan and from the
  effect returns, which is why the whole mix correlates at 0.966. This is narrower than a commercial record.

## What to listen for

* Does the Asturias arpeggio read as the original, or as a generic top-note line?
* Is the wobble bass heavy enough for the genre, or does it want more drive?
* Does the break hold with no kick and no bass for eight bars?
* Is the metal clang a colour, or does it fight the kick?
* Is the nylon guitar audible against the arpeggio, or buried?

## Notes from making it

* The riser is silent unless it is given a held note for the whole build: the score's single long note did not
  sustain (the envelope needs a gate held for the climb), so the riser MIDI is written by hand with one 32-beat
  note per build.
* The first mix was peak-limited at -11.24 LUFS with a loudness range of 13.3 LU, because the break sat 13 LU
  under the drop and the crest factor was too high. Raising the break section level, lowering the kit and the
  kick, and raising the drive to 3.0 let v6 reach -10.0 with a range of 7.8 LU.
* The lead was inaudible in v6: it played one short note per beat at -22 dB. In v8 it plays two sustained notes per bar
  (length 3, gate 0.9) at -18 dB, so the Asturias top line sits above the wobble bass and the arpeggio. The lead's
  playing rms fell to -25.9 dB and the overall gain dropped 2.4 dB to hold -10 LUFS.
* The first render's arpeggio was a single top note repeated in sixteenths, which sounded like a held chord rather
  than the Asturias figure. It is now generated as a real arpeggio: 16 sixteenths per bar cycling through the
  chord's tones (`Em`: E3 G3 B3, `B7`: B3 D#4 F#4, `C`: C3 E3 G3). The guitar, which played full chord voicings,
  was dropped from the intro and the drops so the arpeggio is the top line.
