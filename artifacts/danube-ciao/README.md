# Danube Ciao

A 3/4 folk-orchestral waltz at 126 bpm, bringing the rising D-major figure of
"The Blue Danube" together with the traditional "Bella Ciao", transposed to
B minor. The bass-and-chord waltz pulse ties the two themes together. 48 bars,
about 1:09. Measured, not heard.

* [`mixes/danube-ciao-v1.flac`](mixes/danube-ciao-v1.flac): 24-bit/48 kHz
  lossless reference mix, -14.0 LUFS integrated, 5.2 LU loudness range and
  -2.4 dBTP true peak.
* `midi/`: the separate MIDI parts for the lead themes, chords, bass, kick and
  shakers.
* `circuits/`: the Valis instruments used for the parts and reverb return.
* `song.ttl`: arrangement, sections and mix settings.
* `danube-ciao-midi.rpp`: an editable REAPER project with the six MIDI parts.
* Made reproducibly by [`../../scripts/danube-ciao/make.py`](../../scripts/danube-ciao/make.py);
  the arrangement brief is in [`../../sources/danube-ciao/brief.md`](../../sources/danube-ciao/brief.md).

## Shape

| Bars | Section | What happens |
|---|---|---|
| 1-4 | intro | The Danube's rising triad opens over the waltz pulse. |
| 5-12 | Bella Ciao | The refrain takes the lead in B minor. |
| 13-20 | Blue Danube | The Danube figure answers in D major. |
| 21-28 | crossing | Four-bar call-and-response between the themes. |
| 29-32 | break | A quieter Bella Ciao phrase. |
| 33-44 | finale | The Danube leads, then Bella Ciao joins over the same harmony. |
| 45-48 | coda | The music settles on D. |

## Instruments

| Part | Circuit |
|---|---|
| blue | `violins` |
| ciao | `clarinet` |
| chords | `nylon-guitar` |
| bass | `dub-bass` |
| kick | `808-bd` |
| shakers | `latin-perc` |
| blue-hall | `reverb-return` |

## Mix

The reference mix is targeted at -14 LUFS. All seven rendered stems were
checked against their MIDI notes with no reported problems. The generated
stems and intermediate WAV mix are reproducible with the score script; listen
to the result in a DAW before treating the arrangement or balance as finished.
