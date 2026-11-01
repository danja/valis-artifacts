# Interstate Rain

An instrumental in the manner of a late-1960s rock band with a jazz rhythm section and a storm outside: E Dorian,
100 bpm in a slow triplet feel, 80 bars (3:12). Original material; the brief, which names the record it is in the
style of, is in [`../../sources/interstate-rain/prompt.md`](../../sources/interstate-rain/prompt.md).

* [`mixes/interstate-rain-v1.flac`](mixes/interstate-rain-v1.flac): the mix, -14 LUFS, true peak -1.8 dBTP, a level for each
  section. **Measured, not heard.**
* `midi/`: `epiano`, `bass`, `guitar`, `kit`, `rain` (one held note) and `thunder`.
* `circuits/`: copies of the circuits that played it: `dx7-epiano`, `dx7-bass`, `halloween-guitar` (echo set to 450 ms, a
  dotted eighth at 100 bpm), `drum-machine` (the sampler kit), `rain`, `thunder` and `reverb-return`.
* `wavs/`: the stems and the two reverb returns (not in git).
* Made by [`../../scripts/interstate-rain/track.py`](../../scripts/interstate-rain/track.py).

## Shape

| Bars | Section | What plays |
|---|---|---|
| 1-8 | intro | rain, a thunder roll, a sustained electric piano chord; a pedal hi-hat from bar 5 |
| 9-24 | verse A | bass, comping piano with a rippling run every fourth bar, a loping ride-and-chick kit |
| 25-40 | verse B | the same with a clean guitar figure into the echo |
| 41-48 | bridge | G major 7, F# half-diminished and B7 into E minor; held bass, piano pads, a building kit |
| 49-64 | solo | electric piano lines built from a seeded motif, the guitar answering |
| 65-72 | verse C | back to the verse |
| 73-80 | outro | pads, a held bass, a fading kit, more thunder |

Harmony: the verse is Em7 Em7 A7 A7 Em7 Em7 Dmaj7 A7. The bridge is Gmaj7 Gmaj7 F#m7b5 B7 Em7 Em7 A7 A7.

## End-to-end test notes

* The kit is `examples/drum-machine.ttl` from the Valis repository: eleven CC0 recordings played by `val:Sampler` with
  velocity layers, a hi-hat choke group and a stereo pan for each drum. This track plays it softly (mostly velocities 34 to 70).
* The rain and thunder are also `val:Sampler`: the rain is a 69 s recording looped between 4 s and 66 s with a 3 s
  crossfade under one held note, and the thunder is three one-shot sounds on keys 60, 62 and 64.
* The rain, thunder and kit sounds were found and downloaded over MCP with `freesound_search` and `freesound_download`.
* Checks run: every stem free of NaN, per-bar rms against the score (no silence where there are notes), the pitch of each
  instrument on one note, the mix's loudness and stereo image, and the neural ears (`listen`), which tag the mix "Rain" and
  "Music" and match "a slow rock song with electric piano and rain" best. None of this is listening.
