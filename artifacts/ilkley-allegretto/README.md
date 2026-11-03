# Ilkley Allegretto

"On Ilkla Moor Baht 'at" played over the repeating rhythm of the slow movement of Beethoven's Seventh Symphony. 76 bpm, 66 bars, about 3 min 30 s, in A minor and A major. Every sound comes from a Valis circuit, played from the MIDI files that `scripts/ilkley-allegretto/make.py` writes. It was measured and not heard.

Both tunes are out of copyright. The Ilkla Moor tune is the Methodist hymn tune Cranbrook, by Thomas Clark (1805), and the symphony is from 1812.

## Why these two fit

The Allegretto is built on one rhythm: a quarter note, two eighths, then two quarters, repeated over a slowly moving set of chords. Ilkla Moor is a hymn tune in D major with a plain, singable shape. Moved down a fifth it lands in A major, and the Allegretto's middle section is in A major too. So Ilkla Moor sits on Beethoven's rhythm, and the same notes with the third and sixth lowered sit in his A minor.

## Where the notes come from

I read both tunes off sheet music and did not work from memory.

* **Ilkla Moor**: [Nigel Gatherer's page](https://nigelgatherer.com/tunes/tunes/zWorld/MNO/OnIlk.html), whose PDF has the tune and chords in D major. Here it is moved down a fifth.
* **Beethoven**: the top line of the opening, read from a [cello trio arrangement on 8notes](https://www.8notes.com/scores/36821.asp), then checked against the opening chords on [Wikipedia](https://en.wikipedia.org/wiki/Symphony_No._7_(Beethoven)). The chords under his bars 3 to 10 are the arrangement's. The chords under his bars 11 to 18 are my own, because I couldn't read them reliably, so check them against a full score if it matters to you.

## Structure

One bar here is four beats, so one bar of Beethoven's 2/4 is half a bar.

| Section | Bars | What happens |
|---|---|---|
| intro | 2 | The opening chord of the movement, A minor, struck and let go. |
| theme | 8 | Beethoven's melody in the cello over his chords on a nylon guitar. The sub and strings join for the second half. |
| ilkla | 21 | Ilkla Moor on trumpets in A major over the rhythm, with a soft kick. The strings come in halfway, and the flute joins an octave up for the second half. |
| dialogue | 21 | The cello plays Beethoven's melody, then the trumpets answer with Ilkla Moor in A minor, twice. |
| finale | 8 | Both at once. The cello and horns play Beethoven's melody and rhythm while the trumpets and flute play Ilkla Moor in A minor over the top. |
| outro | 6 | The rhythm thins out on a single chord over a held E and A. |

## Circuits

| Part | Circuit |
|---|---|
| cello | `cello` (turned down 7 dB, see Notes) |
| trumpets | `trumpets` |
| flute | `flute` |
| guitar | `nylon-guitar` |
| strings | `violins` |
| horns | `horn-section` |
| sub | `dub-bass` |
| kick | `808-bd` |
| shakers | `latin-perc` |
| brasshall, cellohall | `reverb-return` |

## Mix

`mixes/ilkley-allegretto-v1.flac` measures -14.0 LUFS, true peak -1.8 dBTP, loudness range 6.9 LU, no clipped samples. `ilkley-allegretto-midi.rpp` opens the nine MIDI parts in Reaper with the mix's volumes and pans. The two reverb returns aren't tracks.

## Notes

The cello circuit has no limiter, and its level changes with the note: G3 peaks at 0.75 and B3 at 0.31 with the output at -34 dB. The stem clipped on G3 to B3 runs, so the copy in this song is 7 dB quieter. "Tide Table" had cello clipping on the same notes, and may have the same cause. I haven't checked.

`valis-shot` reads the trumpet's pitch as 7 to 19 cents flat, and fails above A4. The loudest peak in the spectrum is within 2 cents of the right note from E4 to C#5, so I think the pitch tracker is wrong, not the circuit. I haven't looked at why.
