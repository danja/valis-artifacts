# scripts/tide-table/vocal-guide.py
#
# The lyrics of "Tide Table", a guide melody with one MIDI note per syllable, and lyrics.md, which lays the words against the bars and
# says how to sing them. The bars are those of make.py (72 bars at 78 bpm, counted from 0 here and from 1 in the document).
# The guide is rendered by circuits/emulator-choir.ttl to wavs/vocal-guide.wav and is not in the mix.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.environ.get("VALIS", "/chalet/github/valis"), "scripts", "song"))
import midiw
ART = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "tide-table"))
BPM = 78

SCALE = [57, 58, 60, 62, 64, 65, 67, 69, 70, 72, 74]       # D natural minor, A3 to D5
NAMES = {57: "A3", 58: "Bb3", 60: "C4", 62: "D4", 64: "E4", 65: "F4", 67: "G4", 69: "A4", 70: "Bb4", 72: "C5", 74: "D5"}
CONTOUR = [0, 1, 0, -1, 0, 1, 2, 1, 0]                       # stays near one note and leans up at the end of a line

VERSE = ["The tide ta-ble's pinned be-side the door", "Soft at the folds from years of rain",
         "Low wa-ter at a quar-ter past", "High wa-ter when you used to call",
         "The boats lie o-ver on their sides", "Wait-ing for the sea to come a-gain",
         "I read the fig-ures like a psalm", "Of ev-ery-thing that must re-turn"]
BRIDGE = ["A-way a-way it draws a-way", "So far you could not call it lost",
          "And what the wa-ter takes it keeps", "Un-til the clock comes round"]
CHORUS_1 = ["Come in come in on the ris-ing tide", "Bring ev-ery-thing you took a-way",
            "I'll be here at the wa-ter's edge", "The sea has nev-er missed a day"]
CHORUS_2 = CHORUS_1[:3] + ["And nor have I not one sin-gle day"]
EBB = ["Low wa-ter at a quar-ter past", "High wa-ter will be here by dawn", "Come in come in"]

# (name, first bar, lines, anchor mode, velocity)
PLAN = [("Verse", 24, VERSE, "chord", 92), ("Bridge", 40, BRIDGE, "chord", 70),
        ("Chorus", 48, CHORUS_1, "tune", 100), ("Chorus", 56, CHORUS_2, "tune", 100), ("Ebb", 64, EBB, "chord", 62)]

# the chord of each bar, as in make.py, and the tune's first note of each bar of the chorus
PROG_A = ["Dm", "Bb", "F", "C"]
PROG_B = ["Dm", "Gm", "Bb", "A"]
ANCHOR_OF = {"Dm": 65, "Bb": 62, "F": 69, "C": 67, "Gm": 62, "A": 69}      # a chord tone in the singing range
TUNE_START = [62, 69, 65, 58, 69, 65, 67, 62]                             # the cello's first note of bars 1 to 8 of the tune


def chord_at(bar):
    sec_start = {"rise": 24, "memory": 40, "flood": 48, "ebb": 64}
    if 24 <= bar < 40: return PROG_B[((bar - 24) // 2) % 4]
    if 48 <= bar < 56: return PROG_B[((bar - 48) // 2) % 4]
    return PROG_A[((bar - 40) // 2) % 4] if bar >= 40 else "Dm"


def nearest(note):
    return min(range(len(SCALE)), key=lambda i: abs(SCALE[i] - note))


ASK = [0, 1, 0, 1, 2, 1, 2, 3, 2]                            # a line that asks leans up
ANSWER = [2, 1, 1, 0, 1, 0, -1, 0, -1]                       # a line that answers settles down


def line_notes(bar, text, mode, vel, first_bar, index):
    syllables = text.replace("-", " ").split()
    here = TUNE_START[(bar - first_bar) % 8] if mode == "tune" else ANCHOR_OF[chord_at(bar)]
    there = TUNE_START[(bar + 1 - first_bar) % 8] if mode == "tune" else ANCHOR_OF[chord_at(bar + 1)]
    base = nearest(here)
    shape = ASK if index % 2 == 0 else ANSWER
    step = 0.6 if len(syllables) > 5 else 0.9
    out = []
    for k, _ in enumerate(syllables):
        last = k == len(syllables) - 1
        deg = nearest(there) if last else min(max(base + shape[k % len(shape)] - (1 if index % 2 else 0), 0), len(SCALE) - 1)
        out.append((bar * 4.0 + 0.5 + k * step, (2.4 if last else step * 0.8), SCALE[deg], vel + (6 if k % 2 == 0 else 0)))
    return out


notes, doc = [], []
for name, first, lines, mode, vel in PLAN:
    for n, text in enumerate(lines):
        bar = first + n * 2
        got = line_notes(bar, text, mode, vel, first, n)
        notes += got
        doc.append((name, bar + 1, text.replace("-", ""), " ".join(NAMES[p] for _, _, p, _ in got), len(got)))
os.makedirs(os.path.join(ART, "midi"), exist_ok=True)
midiw.write(os.path.join(ART, "midi", "vocal.mid"), sorted(notes), BPM)
print(len(notes), "syllables,", len(doc), "lines")

import json
json.dump(doc, open(os.path.join(HERE, "lines.json"), "w"))
