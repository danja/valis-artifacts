# Tide Table

A slow instrumental in D minor at 78 bpm, 72 bars, about 3 min 45 s. Every sound is a Valis circuit, played from MIDI files written by
`scripts/tide-table/make.py`. It was measured and not heard.

## Structure

| Section | Bars | What happens |
|---|---|---|
| intro | 8 | A cello drone, sparse harp and single bell notes. A faint heartbeat arrives in the last two bars. |
| tide | 16 | The cello plays the tune over a two-bar-a-chord loop (Dm, Bb, F, C). Harp arpeggios, bell droplets, a slow kick and brushed maracas. |
| rise | 16 | The loop changes to Dm, Gm, Bb, A. The kick plays four to the bar, the sub moves, an electric piano plays off the beat and a string pad holds each chord. |
| memory | 8 | The band drops out. The harp plays the tune alone, answered by bells and a pad played through a spectral codec so it sounds remembered. |
| flood | 16 | Everything returns, with a choir on the top note of each chord. The second half goes back to the first loop. |
| ebb | 8 | The heartbeat and sub leave, the pad and the codec pad stay, and the cello plays the tune once more. |

## Circuits

| Part | Circuit | Notes |
|---|---|---|
| cello | `cello` | A bowed string with a wooden body. It plays one note at a time. |
| harp | `harp` | Eight plucked strings; arpeggios, and the tune in the memory. |
| bell | `free-bell` | A bell made from eight hand-set partials. Mono. |
| epiano | `dx7-epiano` | FM electric piano. |
| strings | `quadra-strings` | A string-machine pad. |
| choir | `emulator-choir` | A held "ah" through a bit-reducer. |
| ghost | `lofi-codec` | Bandwidth 5 kHz, floor 18 dB, step 8 dB. |
| sub | `dub-bass` | Roots and a pickup note. |
| heart | `808-bd` | A bass drum at low velocity. |
| shakers | `latin-perc` | Maracas, note 70. |
| harphall, cellohall | `reverb-return` | Reverb sends from the harp and the cello. |

## Mixes

`mixes/tide-table-v1.flac` is -14.0 LUFS, true peak -2.0 dBTP, loudness range 11.4 LU, no clipped samples (measured). The range is wide on
purpose: the memory is 2.5 dB under the tide and the flood 2.5 dB over it. `tide-table-midi.rpp` opens the ten MIDI parts in Reaper with the
mix's volumes and pans; the two reverb returns are not tracks.

## Voice

No vocal is recorded. [`lyrics.md`](lyrics.md) has the words laid against the bars, the pitch of every syllable, and notes on how to sing them.
`wavs/vocal-guide.wav` is a guide melody (one note per syllable, played by `emulator-choir`) and `guide/tide-table-v1-with-guide.flac` is the mix with
the guide on top, to sing along to. The guide is not in the mix. Made by `scripts/tide-table/vocal-guide.py`; measured, not heard.

## Notes

* The cello stem clipped when the tune was played an octave lower in the ebb (bar 66, A3 then G3), and in the first render of the intro. Moving the tune
  back up removed it. The cause is not looked at; the single notes C3 to C5 rendered alone were clean.
* The stems are large and are not in git; run `python3 scripts/tide-table/make.py` to make them.
