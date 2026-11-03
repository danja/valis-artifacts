# Tide Table

A slow instrumental in D minor at 78 bpm. 72 bars, about 3 min 45 s. Every sound comes from a Valis circuit, played from the MIDI files that `scripts/tide-table/make.py` writes. I measured it and haven't listened to it.

## Structure

| Section | Bars | What happens |
|---|---|---|
| intro | 8 | A cello drone, a sparse harp and single bell notes. A faint heartbeat comes in for the last two bars. |
| tide | 16 | The cello plays the tune over a loop of Dm, Bb, F, C, two bars to a chord. Harp arpeggios, bell droplets, a slow kick and brushed maracas. |
| rise | 16 | The loop becomes Dm, Gm, Bb, A. The kick plays four to the bar, the sub moves, an electric piano plays off the beat and a string pad holds each chord. |
| memory | 8 | The band drops out. The harp plays the tune alone, with bells and a pad that goes through a spectral codec so it sounds remembered. |
| flood | 16 | Everything comes back, with a choir on the top note of each chord. The second half returns to the first loop. |
| ebb | 8 | The heartbeat and sub go. The pad and the codec pad stay, and the cello plays the tune once more. |

## Circuits

| Part | Circuit | Notes |
|---|---|---|
| cello | `cello` | A bowed string with a wooden body. One note at a time. |
| harp | `harp` | Eight plucked strings. Arpeggios, and the tune in the memory. |
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

`mixes/tide-table-v1.flac` measures -14.0 LUFS, true peak -2.0 dBTP, loudness range 11.4 LU, no clipped samples. The range is wide on purpose. The memory sits 2.5 dB under the tide and the flood 2.5 dB over it.

`tide-table-midi.rpp` opens the ten MIDI parts in Reaper with the mix's volumes and pans. The two reverb returns aren't tracks.

## Voice

There's no recorded vocal. [`lyrics.md`](lyrics.md) has the words against the bars, the pitch of every syllable, and notes on how to sing them. `wavs/vocal-guide.wav` is a guide melody with one note per syllable, played by `emulator-choir`. `guide/tide-table-v1-with-guide.flac` is the mix with the guide on top, to sing along to. The guide isn't in the mix. `scripts/tide-table/vocal-guide.py` makes it. Also measured, not heard.

## Notes

The cello stem clipped when I played the tune an octave lower in the ebb (bar 66, A3 then G3). Moving the tune back up fixed it. I haven't looked at why. Single notes from C3 to C5 rendered alone were clean.

The stems are big and not in git. `python3 scripts/tide-table/make.py` makes them.
