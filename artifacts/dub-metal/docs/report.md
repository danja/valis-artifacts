# dub-metal: how it was made, what worked and what did not

Everything below is **measured, not heard**. Nobody listened to any of it while it was made. The numbers say what is
in the files, not whether it is good. Three mixes are kept so they can be compared by ear: `dub-metal-v1`, `v2`, `v3`
(`v3` is the latest).

## The brief

`sources/dub-metal-prompt.md`: C Phrygian Dominant, 85 bpm, dub reggae foundations (heavy electric bass, sparse keyboard
offbeat stabs with delay), upper layers from industrial (metal bashing), minimally melodic, more feeling than
intellect. (The brief sits in `sources/` and not in `sources/dub-metal/` as `docs/dir-layout.md` asks. I left it where
it was put.)

## The plan, in numbers first

* 72 bars at 85 bpm, about 3:23. Sections: intro 8, groove 16, bash 16, dub 8, peak 16, outro 8.
* An eight-bar vamp on C and Db with Fm in bar seven: `C C Db C | C C Fm Db`. The scale is C Db E F G Ab Bb, so the
  bass always has the half step above the tonic and the Db to E augmented second, which are what Phrygian Dominant sounds
  like. Stab chords are the triads that stay inside the scale (C major, Db major, F minor).
* The melody is the bass: a held root, a push before beat three and a pickup into the next bar. Nothing else carries a tune.
* One part, one circuit, one MIDI file: `bass`, `kit`, `stabs`, `metal`, `bell`. Which part plays in which section is a
  table (`PLAN` in `scripts/dub-metal/track.py`), so an alternate arrangement is a change of table.
* Seeded: the same run gives the same MIDI.

## The circuits

| Part | Circuit | Why |
|---|---|---|
| bass | `dub-bass.ttl` (new) | `psych-bass.ttl` was tried first and read as "a synthesizer keyboard preset" at 59% (`valis-shot is`, "a heavy electric bass guitar", 1.8%). `dub-bass.ttl` is `six-string-bass.ttl` with a dark soft pick, a low pickup, more drive and no chorus. |
| kit | `909.ttl` | One-drop: kick and rim together on beat three, closed hats on every eighth, an open hat now and then; a steady four-beat pulse in the peak. |
| stabs | `tonewheel-organ.ttl` | Short chords on the "and" of two and four. Sent to the echo. |
| echo | `dub-delay.ttl` (new) | A dotted eighth (529 ms) bucket-brigade delay, wet only, low-cut. Used as a send for the stabs and the metal. |
| metal | `metal-bash.ttl` | A five-sixteenth cycle played against the bar of sixteen, so it drifts across the groove. A low "anvil" hit in the dub section. |
| bell | `free-bell.ttl` | A low toll on C at the head of the dub section and the outro. The bell's hum is C5, so it only fits the tonic. |

## Process, and which tools did what

1. **Plan and score** in Python (`scripts/dub-metal/track.py score`), one MIDI file per part.
2. **Load, lint and render each circuit** with the Valis MCP tools (`load_file`, `lint`, `render` with `midi`, `tempo`,
   `rolling`) on a short slice of the score, and read `measure` before building on it. Lint was clean for every circuit.
3. **Full-length stems** with `valis_render` on the command line (`track.py render`), four at a time, then the two
   echo returns by feeding a stem to `dub-delay.ttl` with `-i`.
4. **Check every stem** with `valis-shot measure`: peaks, clipping, where it first sounds, pitch.
5. **Mix** in Python (`track.py mix`): each stem is set to a level by its playing rms, panned, high-passed, summed with a
   synthetic room, soft-clipped and brought to -14 LUFS with a true peak under -1 dBTP (`scripts/shot/lufs.py`).
6. **Check the mix** by section (level, share of energy below 150 Hz and above 2 kHz), with `compare` between versions and
   with `listen` (neural tags and sentence shares).

## What worked

* The whole chain ran: score, seven stems, mix and loudness target, with a fixed seed. Each stage has a command and can be
  rerun alone (`render --only=metal`).
* **`render` with `midi`, `tempo` and `rolling` over MCP** (added earlier in this work) played a MIDI part with the
  transport running, which the dub bass and the kit needed. Off-grid notes fell on their own samples.
* **Lint** caught nothing because nothing was wrong, but it ran in one call per circuit and cost nothing.
* **`measure` found two real faults at once**: the first `free-bell` clipped at +18 dBFS earlier in this work, and here the
  909 stem clips four samples (true peak +1.16 dBTP). The first is fixed; the second is handled by the mix but left in
  the stem.
* **The LUFS target**: v1 to v3 all land on -14.0 LUFS with true peaks of -2.4 to -2.6 dBTP, so the versions compare at the
  same loudness.
* **`compare`** said v1 and v2 differ by 0.72 dB of spectral distance: raising the metal changed little overall.
* The new circuits (`dub-bass`, `dub-delay`) and the existing ones all pass the examples lint test.

## What did not work, or is not known

* **No MCP tools at the start.** The Valis server was started after the session, so its tools were not attached. A
  restart fixed it. (The MCP config could say so more plainly.)
* **MCP `render`, `compare` and `measure` time out on anything heavy.** The tool waits 5 seconds for the app's message
  thread. The organ (342 nodes) timed out at 6 to 40 seconds of audio, and `compare` of two 213-second files timed out.
  After a timeout the thread stays busy and the next calls fail too. `render` is also limited to 60 seconds. So the
  MCP tools were used for short checks and the command line for full-length work.
* **`sounds_like` is not available in the app build** (`VALIS_WITH_ONNX` is off there). The command line has it only in an
  older Debug build, where one call took about ten minutes (model load and a 3-minute file in Debug). The Release
  `valis_shot` is stale and was built without the neural models. Neural checks were therefore thin:
  * the dub bass was not checked by `is` (the run never finished);
  * `listen` on mix v1 gave AudioSet tags of Music, Piano, Keyboard, Electric piano, Synthesizer (the organ stabs read as
    piano), and sentence shares of **industrial music 79%, a pop song 10%, a drum and bass track 6%, dub reggae 5%**,
    heavy metal 0%. By that model the upper layer is plain but the dub foundation is not showing.
* **The mix is dark.** Under 2% of the energy in any section is above 2 kHz (0.2% in the dub section). The metal layer was
  low in pitch (a spectral centroid of 232 Hz) so it was moved up two octaves (v2) and raised (v3). The result is still
  about 1% above 2 kHz. The industrial layer is likely too quiet and too soft, but only a listener can say.
* **Little dynamic arc.** The sections differ by only 3 to 4 dB in rms (intro -18.3, groove -16.8, bash -15.7, dub -17.5,
  peak -14.4 dB in v3), because every stem is levelled by its own playing rms. Dub mixing is mostly dropping parts in and
  out, which this does at the part level but flattens at the level of the whole.
* **The organ is a heavy voice for a light job.** It is slower than real time in a Debug build and was the reason for the
  MCP timeouts, to play three-note chords a few times a bar.
* **Only one industrial source** (`metal-bash.ttl`) is used. Nothing machine-like (a gated noise loop, a clanking
  sequence) beyond the five-sixteenth cycle.
* The app reports `sampleRate` 8000 in `get_diagnostics` while renders use 48000 (already in `TODO.md`).

## Not decided: needs a listener

* Is the dub bass heavy enough, and does it read as a bass guitar?
* Do the stabs bubble on the offbeat, and does the delay feel like dub or like an echo effect?
* Is the metal layer present at all? Is it bashing or just a tuned plate?
* Does the vamp give "feeling" or is it a loop? Does the breakdown (bars 41 to 48) work with only bass, echoes, the bell
  and the anvil?

## Files

* `midi/`: the five parts. `wavs/`: the seven stems (not in git). `mixes/`: `dub-metal-v1.wav`, `v2`, `v3` (not in git).
* `scripts/dub-metal/track.py` in this repository; circuits `dub-bass.ttl`, `dub-delay.ttl` in the Valis repository.
* Tasks that follow from this report are in the Valis repository's `TODO.md`, under "From the dub-metal piece".
