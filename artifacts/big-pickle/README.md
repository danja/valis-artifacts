# Big Pickle

Driving [techno](https://en.wikipedia.org/wiki/Techno) at 138 bpm in A minor, 140 bars (4:03), for the year
2000's idea of the future. The palette is the one that year imagined: a machine waking to a held chord and a
bleep arpeggio running like data on a phone line, a [supersaw](https://en.wikipedia.org/wiki/Supersaw) pad
and chord stabs over chrome and bubble plastic, a hard four-to-the-floor kick, and long reverb tails. The
material is new. The brief is in [`../../sources/big-pickle/prompt.md`](../../sources/big-pickle/prompt.md).

Everything here is **measured, not heard**. What still needs a listener is listed at the end.

* [`mixes/big-pickle-v5.flac`](mixes/big-pickle-v5.flac): the mix. -10.0 LUFS integrated, loudness range
  8.1 LU, true peak -1.6 dBTP, no clipped or non-finite samples.
* `midi/`: `kick`, `kit`, `bass`, `stab`, `pad`, `arp`, `lead`, `riser`.
* `circuits/`: the ten circuits that played it (five written for the track, two adapted from Valis
  examples, three copied).
* `wavs/`: the stems and the three effect returns (not in git).
* Made by [`../../scripts/big-pickle/make.py`](../../scripts/big-pickle/make.py), which writes the circuits,
  `score.ttl` and `song.ttl` from one table.

## Shape

| Bars | Time | Section | What plays |
|---|---|---|---|
| 1-16 | 0:00 | intro | a rim click, one held pad chord and a slow bleep arpeggio, which goes to sixteenths at bar 5; the kick arrives at bar 9, the bass at bar 13 |
| 17-24 | 0:28 | build 1 | kick, offbeat bass, a promise of the hook, hats to sixteenths, a snare roll and a riser |
| 25-48 | 0:42 | **drop 1** | sub boom, then full kick, rolling bass, offbeat stabs and the arpeggio |
| 49-64 | 1:23 | break 1 | kick out, sustained stabs and the break hook (Dm E F G), a riser in the last four bars |
| 65-72 | 1:51 | build 2 | as build 1 |
| 73-96 | 2:05 | **drop 2** | as drop 1, with the hook in the lead |
| 97-104 | 2:47 | break 2 | stabs, pad and arpeggio with no kick and no bass, a riser |
| 105-112 | 3:01 | build 3 | as build 1 |
| 113-128 | 3:15 | **drop 3** | the hook an octave up, everything in |
| 129-140 | 3:43 | outro | the groove thins to hats, rim and a final chord, then a 6 s fade |

Three drops and four risers. A build ends in a sixteenth-note snare roll with the last beat empty, so the
drop lands on a gap.

## The material

* Harmony: `Am F C G`, a chord a bar, four bars round. The breaks move to `Dm E F G`.
* Hook: a four-bar phrase, original, reaching the sixth and the ninth and falling back. The lead promises it
  in build 1, carries break 1 as the break hook, and plays it through drop 2 and drop 3 (an octave up in
  drop 3, to MIDI 96). Drop 1 has no lead.
* Break hook: the same shape over `Dm E F G`, with the tension of the minor dominant.
* Bass: the offbeat eighth on the root, rolling sixteenths in the drops.
* Arpeggio: four notes a beat, root, lowest chord tone, top chord tone, and the lowest an octave up, which
  gives the wide digital leap the motif needs.
* Pad: one held chord a bar.
* Stabs: the chord on the offbeat of beats 2 and 4 in the drops, sustained through the breaks.

## The instruments

| Circuit | What it is |
|---|---|
| `y2k-kick.ttl` | A sine falling from 190 Hz to A1 (55 Hz) in 45 ms with a short noise click on the attack, and a long sub boom on key 35 for the first beat of each drop. |
| `y2k-bass.ttl` | A saw at the played pitch and a square an octave below into a resonant ladder filter opened by an envelope on every note, a tanh and a DC blocker. Monophonic. |
| `y2k-lead.ttl` | Five saws (one at pitch, three detuned, one an octave up), a glide and a chorus, into a ladder filter with an envelope. |
| `y2k-bleep.ttl` | A square and a sine an octave up through a [bit and sample-rate reducer](https://en.wikipedia.org/wiki/Bitcrusher) at 9 bits, the grain of a 2000 game console. |
| `y2k-riser.ttl` | Noise through a band-pass that opens from a rumble to a hiss, a saw climbing under it and a square whistle an octave up, all on a 6.4 s envelope, which is four bars at 138 bpm. |
| `y2k-stab.ttl` | Eight voices of two detuned saws from `circuits/prophet-5.ttl`, with a faster envelope, more detune and a chorus. |
| `y2k-pad.ttl` | Eight voices of three saws from `circuits/quadra-strings.ttl`, with a 900 ms attack, a 900 ms release and a darker filter. |
| `909.ttl` | The [TR-909](https://en.wikipedia.org/wiki/Roland_TR-909) kit from the Valis examples, unchanged. |
| `reverb-return.ttl` | The Valis reverb return, unchanged, one for the stabs and one for the pad. |
| `dub-delay.ttl` | The Valis dub echo, with the delay retimed to a dotted eighth at 138 bpm (326 ms) and the feedback reduced. |

## The mix

`valis-song mix song.ttl --version v5 --arc`, then `ffmpeg` to FLAC. Earlier working mixes v1 to v4 are
kept as WAVs, which are not in git.

| | |
|---|---|
| Integrated loudness | -10.0 LUFS (the song asks for -10; reached without leaning on the limiter) |
| Loudness range | 8.1 LU |
| True peak | -1.6 dBTP |
| Peak / RMS | -1.60 dBFS / -12.21 dB |
| Clipped samples / non-finite | 0 / 0 |
| Stereo correlation | 0.950, median width -15.8 dB, balance +0.46 dB |
| Spectral centroid | 570 Hz; 4.6% of the power above 2 kHz |

Section levels as mixed: intro -19.4, build 1 -13.1, drop 1 -11.4, break 1 -15.1, build 2 -13.1, drop 2
-10.2, break 2 -13.8, build 3 -13.0, drop 3 -9.5, outro -16.4 dB.

Balance over drop 2 (2:05 to 2:47, each stem's rms with its mix gain applied):

| Stem | rms | | Stem | rms |
|---|---|---|---|---|
| kick | -14.3 dB | | arp echo | -24.9 dB |
| bass | -18.5 dB | | pad | -28.1 dB |
| lead | -21.6 dB | | pad reverb | -28.2 dB |
| stab | -23.4 dB | | stab reverb | -29.4 dB |
| arpeggio | -23.7 dB | | | |
| kit | -24.0 dB | | | |

Stem checks (`valis-song stems`): all eleven found, every bar that the score gives notes has sound, no problems
reported. The kick peaks at -1.0 dBFS, on its limiter, but 0.0008% of its samples are above 0.85, so it touches
the ceiling on transients rather than sitting on it. The kit peaks at -1.0 dBFS too, with no sample above 0.85.
Playing rms of the stems before levelling: kick -11.7, bass -18.3, stab -20.3, arpeggio -21.4, pad -24.6, kit
-25.1, lead -26.1, riser -27.8 dB.

## Measured and not heard

* The tempo detector reads 69.0 bpm (strength 0.90); 138.0 is its third candidate (0.73). A four-to-the-floor
  kick with a backbeat on 2 and 4 is usually read at half time, so this is expected, but it is a measurement,
  not a confirmation that the groove sits right.
* The key detector reads C major (0.81). The progression is A minor, its relative major, so that is also
  expected.
* Every instrument stem is mono (correlation 1.000). The width in the mix comes only from pan and from the
  effect returns, which is why the whole mix correlates at 0.950. This is in line with the other Valis mixes
  ("Street Hammer" measures 0.982), but it is narrower than a commercial record of the period.
* `valis-shot is mixes/big-pickle-v5.wav "driving techno with a hard kick and risers"` answers yes, with a
  share of 0.572, first of 21 candidates (next: "a synthesizer keyboard preset" at 0.223). That is the
  neural ears' judgement against twenty rival descriptions, not a listener's.

## What to listen for

* The riser sits at -28 dB, about 14 dB under the kick across a build, and its own peak is high. Does it build,
  or is it only a hiss?
* The pad is at -28.5 dB in the drops. Is the supersaw bed far enough forward?
* Break 2 has no kick and no bass for eight bars. Does the drop-out work, or does the track lose its drive?
* The hook reaches MIDI 96 (C7) in drop 3. Is that bright or piercing?
* The master soft clip runs at a drive of 1.5. Is the kick hard enough for the genre, or does it want more?

## Notes from making it

* The hook was first written as eight bars of notes declared as an eight-bar pattern, so the lead rested for
  four bars of every phrase. `valis-song stems` showed bars 53 to 56 silent while the pattern played, and the
  MIDI ticks confirmed it. The pattern is now a true four-bar phrase, and the lead went from 220 to 380 notes.
* Mix v1 was peak-limited at -11.1 LUFS: the band could not be made louder without more drive. Raising the
  master drive and the section arc let v5 reach -10.0.
* In v1, break 2 sat 13.5 LU under drop 3, which took the loudness range to 13.0 LU. Its section level went
  from -6 to +2, and the range is now 8.1 LU.
* The first mix had the hats, bleep and returns too far back: its top end was 3.5 dB darker than a
  pink-noise tilt and its correlation was 0.969. Lifting the kit and the arpeggio and spreading the three
  returns to +/-0.55 and 0.60 raised the 8 kHz band of drop 2 by 0.8 dB and moved the correlation to 0.950.
  The top is still 3.1 dB darker than a pink-noise tilt.
