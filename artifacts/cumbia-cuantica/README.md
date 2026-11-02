# Cumbia Cuántica

An avant-garde [cumbia](https://en.wikipedia.org/wiki/Cumbia) in A minor at 94 bpm, 88 bars (3:45 with its tail). The rhythm section is a
simplified Colombian cumbia, and the flute plays an original tune in the A minor pentatonic scale in the style of a
[gaita](https://en.wikipedia.org/wiki/Gaita_(Colombian_instrument)) melody. Over it, five circuits that were written in one session to show a
single Valis element each are used as instruments. The title is a pun on two of them, the quantiser and the codec. Nothing in it is taken from
another piece. The speech is the nursery-rhyme voice of [All Fall Down](../all-fall-down/README.md), whose rhymes are traditional and out of copyright.

**Measured, not heard.** Nothing here has been listened to.

## Structure

| Section | Bars | What happens |
|---|---|---|
| intro | 8 | Maracas and guacharaca fade in under a ghost pad. The flute plays the tune an octave down, then the band enters. |
| cumbia1 | 16 | The full rhythm section, the flute tune, and the surf guitar chopping eighths on the chord from bar 5. Chords Am Am Dm Dm E7 E7 Am E7. |
| quantise | 16 | A four-chord loop (Am G F E7). The arpeggio enters: sixteen scrambled notes forced into A minor pentatonic, in triplets against the bar. Fuzz stabs break the cumbia. |
| talk | 16 | The break. A talk box recites nursery rhymes over a drone and a thin llamador pulse. The last four bars move to E7. |
| fracture | 8 | Everything in threes against four: hard-clipped fuzz, a diode buzz, maracas every third sixteenth, a codec pad at 2.5 kHz bandwidth. |
| cumbia2 | 16 | The full band again with the flute tune louder, the diode buzz in thirds, and the arpeggio and talk box returning for the last four bars. |
| outro | 8 | The pad decays under the flute's reply, the talk box says its last lines, and the band stops on a bombo hit. |

## The parts and the circuits

The ten parts and one return are `../../../valis/circuits/*.ttl`, copied to `circuits/` so the track does not change if the originals do. A copy
that is set differently is described by the line `scripts/cumbia-cuantica/make.py` holds in its `CIRCUITS` table.

| Part | Circuit | Notes |
|---|---|---|
| shakers, guacha, hand | `latin-perc` | Maracas (note 70), guacharaca scrape (73 down, 74 up), bombo (36), llamador as a muted bongo (61), tambor alegre as congas (62 to 64). |
| guitarron | `guitarron` | Root and fifth, "three and one": the cumbia bass figure. |
| flute | `flute` | The gaita-style tune. Measured in tune from A3 to A5 (within 4 cents). |
| surf | `bassman-amp` | **New.** Input pushed to +14 dB so the valve breaks up, middle scooped to 0.25, treble 0.7. A plucked string through the tone stack of a Fender Bassman, in the manner of the [chicha](https://en.wikipedia.org/wiki/Chicha_music) guitar. A reverb return follows it. |
| fuzz | `distortion-bench` | **New.** Curve 0, a hard clip at threshold 0.25 with 24 dB of drive. |
| buzz | `distortion-bench` | **New.** Curve 3, a diode, on a square wave with 14 dB of drive, so even harmonics as well as odd. |
| ghost, ghostbreak | `lofi-codec` | **New.** A pad through a spectral gate and a codec. `ghost` is 7 kHz bandwidth, `ghostbreak` is 2.5 kHz with a coarser step, used in the fracture and the outro. |
| arp | `arp-quantiser` | **New.** Root A, pentatonic scale, a step of a third of a beat. Sixteen steps last 5 1/3 beats against four, so the pattern drifts across the bar and meets the bar again every 16 beats. |
| talkbox | `vocoder-speak` | **New.** The speech of All Fall Down, shaped onto a played sawtooth carrier by an LPC model. |

The arpeggio and the talk box are marked `val:recorded` in `song.ttl` and are rendered by the script rather than by `valis-song render`:
the arpeggio circuit has no notes (it follows the transport), so it is rendered whole and gated to its sections with short fades, and the
talk box needs the voice as audio input. `valis-song reaper --midi` does not write tracks for them.

## Files

* `mixes/cumbia-cu-ntica-v3.flac` (also `cumbia-cuantica-v3.flac`): the mix, from `valis-song mix --arc`. Integrated loudness -11.2 LUFS (target -11, the
  true-peak ceiling of -1 dBTP set the gain), loudness range 3.3 LU, section levels from -15.5 to -13.4. Versions 1 and 2 are kept as WAV and are
  not in git.
* `song.ttl`: the layout and the mix as data, written by the script. `midi/`: one file for each part, written by the script (the notes are generated
  Python and not a `val:Score`).
* `../../scripts/cumbia-cuantica/make.py` rebuilds everything: `python3 make.py` runs the circuits, the song, the score, the two recorded stems,
  the render and the mix. Each stage can be run alone (`circuits`, `song`, `score`, `recorded`, `render`, `mix`).

## What was measured

* Every note of every part is heard: `valis-song stems` found no problems in any of the 14 stems.
* No stem is clipped. After the `buzz` drive was reduced, only 0.01 to 0.5 per cent of the sounding samples of any stem are within 1.5 dB of
  full scale, and those are transients (counted, not read from the peak).
* **The neural ears do not hear the instruments as the real thing.** `valis-shot is` calls `hand` a conga drum (share 0.99) and `guitarron` a bass guitar
  (0.56), but reads `surf` as a synthesizer keyboard preset (0.63, an electric guitar scores 0.00), `flute` as a preset (0.996), and the talk box as
  a preset. It reads the pad as a synthesizer pad only at rank 2. These models are blunt on physical-model instruments, but the guitar is the one to
  listen to first.

## What to listen for

* Whether the surf guitar sounds like a guitar. The fix, if not, is the pick and the input drive, not the mix.
* Whether the talk box says words. Intelligibility is not measured. Raise the LPC order in `circuits/talkbox.ttl` (default 16) or change the Method
  to the channel vocoder if the words are lost.
* The triplet arpeggio against the bar. It should feel as if it is slipping, and land back on the bar every four bars. If it is only messy, change
  the step to a sixteenth in the `arp` entry of `CIRCUITS`.
* The fracture. It is meant to be uncomfortable, and eight bars may be too long.
* The cumbia pattern itself. It is a simplified one written from the usual description (the llamador on the offbeats, the bombo on the beat, the
  bass on "three and one"), not checked against a player's. A cumbia player will know what to move.

## Notes from making it

* **A follower cannot be louder than its leader's gain.** The maracas, guacharaca and hand drums first followed the guitarron with `val:follows`. A
  follower's level is an offset that cannot be above 0, so they came out 18 to 25 dB under the hand drums in v1. They are now levelled alone, as the
  guide in `docs/making-a-track.md` says to do for a sparse part that must be louder than its leader's gain would make it.
* The intro and talk sections sat about 6 dB under the drops in v1. Raising their section levels (+1.5 and +3.0 dB) brought the loudness range from 7.8 to 3.5 LU.
* The `buzz` stem was a clipped square wave (rms 0.64, 3 per cent of samples above 0.85) with 20 dB of diode drive, so the drive was lowered to 14 dB and
  the circuit's level by 12 dB.
* The arpeggio and the talk box could not be ordinary parts. This is a limit of the song format (a part is a circuit played by a MIDI file), noted in `TODO.md`.
