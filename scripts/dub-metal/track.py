# scripts/dub-metal/track.py
#
# "dub-metal" (working title): dub reggae foundations with industrial metal-bashing on top, played by the circuits in
# the Valis repository (dub-bass.ttl, 909.ttl, tonewheel-organ.ttl, metal-clang.ttl, free-bell.ttl) and sent through
# dub-delay.ttl. The brief is in sources/dub-metal/prompt.md.
#
#   python3 track.py score    write one MIDI file per part to artifacts/dub-metal/midi/
#   python3 track.py render   render every part, and the echo returns, to artifacts/dub-metal/wavs/
#   python3 track.py mix      mix the stems to artifacts/dub-metal/mixes/ (--version=vN, --lufs=N, --arc for a level per section)
#   python3 track.py          all three
#
# C Phrygian Dominant (C Db E F G Ab Bb), 85 bpm, 72 bars (about 3:23). The harmony is a vamp on C and Db, so the half
# step above the tonic and the augmented second Db to E, which are what the scale sounds like, are always in the bass.
import os, sys, random

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
sys.path.insert(0, os.path.join(VALIS, "scripts", "song"))
import midiw, songlib

# The tempo, the sections and the mix are data in song.ttl (checked by the read_song tool). This file keeps the score.
HERE = os.path.dirname(os.path.abspath(__file__))
SONG = songlib.load(os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "dub-metal", "song.ttl")))
BPM = SONG.tempo
SECTIONS = [(s.name, s.bars) for s in SONG.sections]
BARS = SONG.bars
PARTS = [p.name for p in SONG.parts]
MIDI = SONG.midi_dir

# Eight bars, round again: C C Db C | C C Fm Db. (name, bass root, bass pickup into the next bar, stab chord)
CHORDS = {"C":  (36, 37, (60, 64, 67)),     # the pickup is the half step above, the bII
          "Db": (37, 40, (61, 65, 68)),     # Db to E, the augmented second
          "Fm": (41, 37, (60, 65, 68))}
VAMP = ["C", "C", "Db", "C", "C", "C", "Fm", "Db"]

# Which parts play in which section.
PLAN = {"intro":  {"kit": "hats", "bass": "plain"},
        "groove": {"kit": "onedrop", "bass": "plain", "stabs": "light"},
        "bash":   {"kit": "onedrop", "bass": "plain", "stabs": "skank", "metal": "cycle"},
        "dub":    {"bass": "plain", "stabs": "lone", "bell": "toll", "metal": "anvil"},
        "peak":   {"kit": "steppers", "bass": "heavy", "stabs": "skank", "metal": "cycle"},
        "outro":  {"kit": "hats", "bass": "plain", "stabs": "lone", "bell": "toll"}}


def build():
    rng = random.Random(85)
    parts = {p: [] for p in PARTS}
    bar0 = 0
    for name, n in SECTIONS:
        plan = PLAN[name]
        for i in range(n):
            bar = bar0 + i
            b = bar * 4.0
            chord = VAMP[i % 8]
            root, pickup, stab = CHORDS[chord]
            last = i == n - 1

            # -- bass: the root held through the first beat and a half, then a push before beat three and a pickup
            style = plan.get("bass")
            if style:
                parts["bass"] += [(b, 1.4, root, 118), (b + 2.5, 0.4, root, 104), (b + 3.5, 0.4, pickup, 100)]
                if style == "heavy":
                    parts["bass"].append((b + 1.75, 0.2, root + 12, 90))   # an octave up between the two

            # -- kit: one-drop (the kick and the rim on beat three), or a steady pulse in the peak
            style = plan.get("kit")
            if style:
                for k in range(8):
                    parts["kit"].append((b + k * 0.5, 0.2, 42, 62 if k % 2 == 0 else 84))
                if style in ("onedrop", "steppers"):
                    parts["kit"] += [(b + 2.0, 0.25, 36, 124), (b + 2.0, 0.25, 37, 104)]
                if style == "steppers":
                    parts["kit"] += [(b, 0.25, 36, 118), (b + 1.0, 0.25, 36, 96), (b + 3.0, 0.25, 36, 96)]
                if style == "onedrop" and i % 2 == 1:
                    parts["kit"].append((b + 3.5, 0.3, 46, 76))
                if last and name in ("groove", "bash"):
                    parts["kit"] += [(b + 3.0, 0.25, 43, 100), (b + 3.5, 0.25, 41, 112)]

            # -- stabs: offbeat chords on the and of two and the and of four
            style = plan.get("stabs")
            if style == "skank":      # every offbeat, the second and fourth louder: the chop that bubbles
                spots = [0.5, 1.5, 2.5, 3.5]
            elif style == "light":    # the and of two and the and of four
                spots = [1.5, 3.5]
            elif style == "sparse":
                spots = [1.5, 3.5] if i % 2 == 0 else [3.5]
            elif style == "lone":
                spots = [1.5] if i % 4 == 0 else []
            else:
                spots = []
            for s in spots:
                velocity = 100 if s in (1.5, 3.5) else 78
                parts["stabs"] += [(b + s, 0.12, p, velocity) for p in stab + (stab[0] + 12,)]

            # -- metal: a cycle five sixteenths long, against the bar of sixteen
            style = plan.get("metal")
            if style == "cycle":
                tones = [48, 49, 52, 48, 55, 49, 53, 60]     # C3 to C4, a Phrygian Dominant set, struck hard
                for cycle, period, lead in ((0, 1.25, 0.0), (1, 0.75, 0.5)):    # five sixteenths against three
                    for k in range(int(4 / period) + 1):
                        start = lead + k * period + (bar % 5) * 0.25 * (1 - cycle)
                        if start < 4.0 and rng.random() < (0.8 if cycle == 0 else 0.5):
                            parts["metal"].append((b + start, 0.1, tones[(bar * 3 + k + cycle) % len(tones)],
                                                   rng.choice((90, 110, 127))))
            elif style == "anvil" and i % 2 == 0:
                parts["metal"].append((b, 0.2, 36, 124))

            # -- bell: one low toll at the head of a section and every fourth bar after it
            if plan.get("bell") == "toll" and i % 4 == 0:
                parts["bell"].append((b, 3.0, 60, 100))
        bar0 += n

    # A little timing and level variation per part, from a fixed seed, never starting before 0.
    for part, notes in parts.items():
        hum = random.Random(sum(map(ord, part)))
        parts[part] = [(max(0.0, s + (hum.random() - 0.5) * (0.0 if part == "metal" else 0.03)), l, p,
                        max(1, min(127, v + hum.randint(-6, 6)))) for s, l, p, v in notes]
    return parts


def score():
    os.makedirs(MIDI, exist_ok=True)
    for part, notes in build().items():
        if notes:
            midiw.write("%s/%s.mid" % (MIDI, part), notes, BPM)
            print("%-6s %4d notes" % (part, len(notes)))


if __name__ == "__main__":
    args = sys.argv[1:]
    steps = [a for a in args if not a.startswith("--")] or ["score", "render", "mix"]
    option = lambda name, default=None: next((a.split("=", 1)[1] for a in args if a.startswith(name + "=")), default)
    for s in steps:
        if s == "score":
            score()
        elif s == "render":
            only = option("--only")
            songlib.render(SONG, only.split(",") if only else None, workers=4)
        elif s == "mix":
            lufs = option("--lufs")
            songlib.mix(SONG, option("--version", "v1"), float(lufs) if lufs else None, arc="--arc" in args,
                        overwrite="--overwrite" in args)
