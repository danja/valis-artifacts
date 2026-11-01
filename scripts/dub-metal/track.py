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
MIDI = SONG.midi_dir

# Which sections the metal plays in. The kit, bass, stabs and bell are patterns, chords and a plan in score.ttl
# (`valis-song score` writes them); the metal is a seeded random cycle, so it stays here.
PLAN = {"bash": "cycle", "dub": "anvil", "peak": "cycle"}


def build():
    rng = random.Random(85)
    metal = []
    bar0 = 0
    for name, n in SECTIONS:
        style = PLAN.get(name)
        for i in range(n):
            bar = bar0 + i
            b = bar * 4.0
            # -- metal: a cycle five sixteenths long, against the bar of sixteen
            if style == "cycle":
                tones = [48, 49, 52, 48, 55, 49, 53, 60]     # C3 to C4, a Phrygian Dominant set, struck hard
                for cycle, period, lead in ((0, 1.25, 0.0), (1, 0.75, 0.5)):    # five sixteenths against three
                    for k in range(int(4 / period) + 1):
                        start = lead + k * period + (bar % 5) * 0.25 * (1 - cycle)
                        if start < 4.0 and rng.random() < (0.8 if cycle == 0 else 0.5):
                            metal.append((b + start, 0.1, tones[(bar * 3 + k + cycle) % len(tones)],
                                          rng.choice((90, 110, 127))))
            elif style == "anvil" and i % 2 == 0:
                metal.append((b, 0.2, 36, 124))
        bar0 += n

    # The metal is struck exactly; only its velocity varies, from a fixed seed. The unused draw keeps the velocities the
    # same as in the versions before the timing was dropped.
    hum = random.Random(sum(map(ord, "metal")))
    struck = []
    for start, length, pitch, velocity in metal:
        hum.random()
        struck.append((start, length, pitch, max(1, min(127, velocity + hum.randint(-6, 6)))))
    return {"metal": struck}


def score():
    os.makedirs(MIDI, exist_ok=True)
    songlib.score(SONG)                 # the parts in score.ttl
    for part, notes in build().items():  # the parts that are generated here
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
