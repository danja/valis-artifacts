# dub-metal (working title)

C Phrygian Dominant, 85 bpm, 3:23. Dub reggae foundations (a heavy electric bass, a one-drop kit, offbeat organ
stabs into a dotted-eighth echo, sparse in the groove and on every offbeat in the heavier sections) with industrial metal-bashing on top and a low bell in the breakdown. Brief:
`../../sources/dub-metal/prompt.md`.

* `mixes/dub-metal-v5.wav`: v4 with a level for each section (`--arc`): intro and breakdown about 9 dB under the peak. Same stems, same
  -14 LUFS. Measured, not heard.
* `mixes/dub-metal-v4.wav`: the latest mix, -14 LUFS, made after listening feedback (the stabs did not bubble and the metal
  was heard only as bells). v1 to v3 are kept to compare. Measured, not heard.
* `midi/`: bass, kit, stabs, metal, bell.
* `circuits/`: copies of the six circuits that played the piece (`dub-bass`, `909`, `tonewheel-organ`, `metal-clang`,
  `free-bell`, `dub-delay`), as they were when v4 was made. The live versions are in the Valis repository's `circuits/`.
* `wavs/`: the stems and the two echo returns.
* `docs/report.md`: how it was made, what worked, what did not.
* Made by `../../scripts/dub-metal/track.py` with circuits from the Valis repository.
