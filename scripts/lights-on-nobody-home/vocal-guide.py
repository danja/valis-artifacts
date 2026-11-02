# scripts/lights-on-nobody-home/vocal-guide.py
#
# The notes that would ideally be sung in "Lights On, Nobody Home": one note per syllable, written out by hand
# so each line fits the chord under it. The bars are those of track.py. Writes
#   artifacts/lights-on-nobody-home/midi/vocal-guide.mid   the notes
#   artifacts/lights-on-nobody-home/docs/vocal-guide.md    the same, as a table of syllables, notes and bars
#   artifacts/lights-on-nobody-home/wavs/vocal-guide.wav   the guide voice alone      (render)
#   artifacts/lights-on-nobody-home/mixes/lights-on-nobody-home-with-guide.mp3   the mix with the guide (mix)
#
#   python3 vocal-guide.py score | render | mix     (no argument: all three)
#
# A token is  syllable/length/note.  The length is in eighth notes, and eight of them make a bar. A syllable
# written "_" is a rest. A line is two bars (16 eighths) unless it is a one-bar chant line.
import os, sys, subprocess

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "lights-on-nobody-home"))
sys.path.insert(0, os.path.join(VALIS, "scripts", "song"))
import midiw

BPM = 128
# Release is several times faster and renders the same samples; fall back to Debug when only that is built.
RENDER = next((p for p in (os.path.join(VALIS, d, "valis_render_artefacts", c, "valis_render")
                           for d, c in (("build-release", "Release"), ("build", "Debug"))) if os.path.exists(p)),
              os.path.join(VALIS, "build", "valis_render_artefacts", "Debug", "valis_render"))
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    n = NAMES[name[0]]
    rest = name[1:]
    while rest and rest[0] in "#b":
        n += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + n


# ---- the verses: eight lines of two bars each, over  C F | C G7 | C F | G7 C  (the chord bar by bar in the comment)
VERSE_1 = [
    "The/1/E4 lights/2/G4 are/1/G4 on/2/A4 but/1/G4 no/1/E4 bo/1/F4 dy's/2/A4 home/5/A4",                  # C F
    "The/1/E4 lift/2/G4 does/1/G4 n't/1/A4 go/1/G4 to/1/E4 the/1/D4 top/2/D4 floor/3/F4 mate/3/G4",        # C G7
    "He's/1/E4 a/1/E4 sand/2/G4 wich/1/A4 short/1/G4 of/1/E4 a/1/D4 pic/2/F4 nic/6/A4",                    # C F
    "Not/1/D4 the/1/D4 sharp/2/F4 est/1/G4 tool/3/B4 in/1/G4 the/1/E4 shed/6/E4",                          # G7 C
    "Ay/1/G4 que/1/G4 bur/1/A4 ro/1/G4 que/1/G4 bur/1/A4 ro/2/C5 que/2/A4 bur/2/C5 ro/4/A4",               # C F
    "Does/1/E4 n't/1/E4 know/2/G4 his/1/A4 left/2/G4 from/1/E4 his/2/D4 right/6/G4",                       # C G7
    "Dim/1/E4 as/1/E4 a/1/G4 Toc/1/A4 H/1/G4 lamp/2/E4 a/1/G4 bit/1/A4 slow/1/A4 on/1/C5 the/1/A4 draw/4/F4",   # C F
    "Brain's/1/D4 gone/1/F4 off/1/G4 for/1/B4 a/1/G4 Bur/1/F4 ton/2/D4 thick/1/E4 as/1/G4 a/1/E4 door/5/C4",     # G7 C
]
VERSE_2 = [
    "He's/1/E4 a/1/G4 few/2/G4 cards/2/A4 short/1/G4 of/1/E4 a/1/F4 full/2/A4 deck/5/A4",
    "Two/1/E4 fries/2/G4 short/1/G4 of/1/A4 a/1/G4 Hap/2/E4 py/2/D4 Meal/6/G4",
    "A/1/E4 lost/1/E4 cause/2/G4 a/1/A4 mup/1/G4 pet/2/E4 a/1/F4 plon/2/A4 ker/5/A4",
    "All/1/D4 hat/1/D4 and/2/F4 no/1/G4 cat/3/B4 tle/1/G4 my/1/E4 friend/6/E4",
    VERSE_1[4],
    "Yes/1/E4 he's/1/E4 a/2/G4 pil/1/A4 lock/2/G4 a/1/E4 numpt/1/D4 y/1/F4 a/1/D4 drip/5/G4",
    "Dumb/1/E4 as/1/E4 a/1/G4 box/1/A4 of/1/G4 rocks/2/E4 thick/1/G4 as/1/A4 pig/2/C5 shit/5/A4",
    "A/1/D4 com/1/F4 plete/1/G4 and/1/B4 ut/1/G4 ter/1/F4 tit/2/D4 and/1/E4 he's/1/G4 proud/2/E4 of/1/D4 it/3/C4",
]

# ---- the pre-chorus: one bar per phrase over F  G  Bb  A7
PRE_1 = ["Is/1/F4 a/1/A4 ny/1/C5 one/1/A4 in/4/F4", "Is/1/G4 a/1/B4 ny/1/D5 one/1/B4 in/4/G4",
         "Knock/1/Bb4 knock/1/Bb4 knock/1/Bb4 on/1/D5 his/1/D5 head/3/F5", "Noth/1/E5 ing/1/D5 noth/1/C#5 ing/1/D5 there/4/A4"]
PRE_2 = PRE_1[:3] + ["Not/1/E5 a/1/D5 soul/1/C#5 no/1/D5 bo/1/C#5 dy/1/D5 home/2/A4"]

# ---- the chorus, one bar per line over  Dm Bb A A | Dm Bb A A. BLANK is shouted on the beat.
CHORUS = ["BLANK/2/A4 Blank/2/A4 Blank/2/A4 Blank/2/A4",
          "BLANK/2/Bb4 Blank/2/Bb4 Blank/2/Bb4 Blank/2/Bb4",
          "No/1/E5 bo/1/D5 dy/1/C#5 home/1/A4 No/1/E5 bo/1/D5 dy/1/C#5 home/1/A4",
          "BLANK/2/C#5 Blank/2/C#5 Blank/2/C#5 Blank/2/C#5",
          "BLANK/2/A4 Blank/2/A4 Blank/2/A4 Blank/2/A4",
          "No/1/F5 bo/1/D5 dy/1/Bb4 home/1/F4 No/1/F5 bo/1/D5 dy/1/Bb4 home/1/F4",
          "Lights/1/C#5 on/1/A4 lights/1/C#5 on/1/A4 lights/1/C#5 on/1/A4 _/2/A4",
          "No/1/E5 bo/1/D5 dy/1/C#5 home/5/A4"]

# ---- the bridge is spoken, flat, on one low note: the rhythm is what matters
BRIDGE = ["I/2/G3 asked/2/G3 him/2/G3 a/2/G3 ques/2/G3 tion/6/G3", "Wait/2/G3 ed/2/G3 a/2/G3 week/10/G3",
          "The/2/G3 lights/4/G3 were/4/G3 on/6/G3"]

# ---- the outro: the happy key again, over  C  F  G7  C
OUTRO = [VERSE_1[4].rsplit(" que/2/A4", 1)[0], "que/2/A4 bur/2/C5 ro/4/A4", "que/2/B4 bur/2/D5 ro/4/B4", "Ay/4/G4"]

# section name, first bar (counting from 0), the lines and how many bars each line takes
PLAN = [("Verse 1", 8, VERSE_1, 2), ("Pre-chorus 1", 24, PRE_1, 1), ("Chorus 1", 28, CHORUS, 1),
        ("Verse 2", 36, VERSE_2, 2), ("Pre-chorus 2", 52, PRE_2, 1), ("Chorus 2", 56, CHORUS, 1),
        ("Bridge (spoken)", 66, BRIDGE, 2), ("Chorus 3, first time", 72, CHORUS, 1), ("Chorus 3, second time", 80, CHORUS, 1),
        ("Outro", 88, OUTRO, 1)]


def parse(line):
    out = []
    for token in line.split():
        text, units, name = token.split("/")
        out.append((text, int(units), midi(name), name))
    return out


def notes_and_rows():
    notes, rows = [], []
    for section, first, lines, bars_per_line in PLAN:
        for k, line in enumerate(lines):
            bar = first + k * bars_per_line
            beat = bar * 4.0
            units_total = 0
            for text, units, pitch, name in parse(line):
                if text != "_":
                    held = units >= 4
                    length = units * 0.5 - (0.12 if held else 0.07)
                    shout = text.isupper() and len(text) > 1
                    notes.append((beat + units_total * 0.5, length, pitch, 112 if shout else 96 if units_total % 4 == 0 else 86))
                    rows.append((section, bar + 1, units_total / 2.0 + 1, text, name, units / 2.0))
                units_total += units
            assert units_total <= bars_per_line * 8, "%s line %d is %d eighths" % (section, k + 1, units_total)
    return notes, rows


def score():
    os.makedirs(OUTDIR + "/midi", exist_ok=True)
    os.makedirs(OUTDIR + "/docs", exist_ok=True)
    notes, rows = notes_and_rows()
    midiw.write(OUTDIR + "/midi/vocal-guide.mid", sorted(notes), BPM)
    with open(OUTDIR + "/docs/vocal-guide.md", "w") as f:
        f.write(DOC_HEAD)
        section = None
        for sec, bar, beat, text, name, length in rows:
            if sec != section:
                f.write("\n### %s\n\n| Bar | Beat | Syllable | Note | Beats |\n|---|---|---|---|---|\n" % sec)
                section = sec
            f.write("| %d | %g | %s | %s | %g |\n" % (bar, beat, text, name, length))
    print(len(notes), "syllables")


DOC_HEAD = """# Vocal guide

The notes that would ideally be sung in "Lights On, Nobody Home", one note per syllable. The same notes are in
`midi/vocal-guide.mid`, and the mix with the guide voice added is `mixes/lights-on-nobody-home-with-guide.mp3`.
The words are in [lyrics.md](lyrics.md). Bars count from 1 at the start of the song. The tempo is 128 beats per
minute with four beats to a bar.

**Range.** The verses sit between C4 (middle C) and C5; the pre-chorus climbs to F5; the shouted chorus lives around
A4 to E5. A lower voice can drop the whole song an octave. Sung at the pitches written here, a baritone will find
the pre-chorus and the chorus high, and may prefer to go down a fourth or a fifth.

**Verses** are in C major, and each line has two bars, over `C F | C G7 | C F | G7 C`. The tune is simple on purpose:
it stays within a sixth, falls at the end of each line, and lands on C at the end of the verse.

**Chorus** is in D Hungarian minor (D E F G# A Bb C#). The shouted word BLANK is on the beat, one to a beat, on a
note that follows the chord: A over D minor, Bb over Bb, C# over A. The jump from Bb to C# is the augmented second
that gives the scale its sound, so it is worth singing it a little hard. The words "nobody home" start high and fall
through the scale: E D C# A over A major.

**Bridge** is spoken, flat, in the rhythm written; the note shown (G3) is only the pitch of the guide.

Capital letters are shouted. A "Beats" of 0.5 is an eighth note.
"""


def render():
    os.makedirs(OUTDIR + "/wavs", exist_ok=True)
    seconds = 92 * 4 * 60 / BPM + 8
    r = subprocess.run([RENDER, "circuits/vocal-guide.ttl", "--midi", OUTDIR + "/midi/vocal-guide.mid", "--tempo", str(BPM),
                        "--rolling", "--seconds", "%.1f" % seconds, "-o", OUTDIR + "/wavs/vocal-guide.wav"],
                       cwd=VALIS, capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:])


def mix():
    import numpy as np
    from scipy.io import wavfile
    rate, song = wavfile.read(OUTDIR + "/mixes/lights-on-nobody-home.wav")
    _, guide = wavfile.read(OUTDIR + "/wavs/vocal-guide.wav")
    song = song.astype(np.float64) / 2.0 ** 31
    guide = guide.astype(np.float64) / 2.0 ** 31
    guide = guide if guide.ndim == 2 else np.stack([guide, guide], axis=1)
    n = min(len(song), len(guide))
    live = np.abs(guide[:n].mean(axis=1))
    # the guide at the level that the singer would sing: about 3 dB over the song's own rms while it plays
    w = rate // 10
    e = np.sqrt((guide[:n // w * w, 0].reshape(-1, w) ** 2).mean(axis=1))
    played = e[e > 1.0e-3]
    guide_db = 20 * np.log10(np.sqrt((played ** 2).mean()))
    song_db = 20 * np.log10(np.sqrt((song ** 2).mean()))
    gain = 10 ** ((song_db + 3.0 - guide_db) / 20)
    mixed = song[:n] + guide[:n] * gain
    mixed = mixed / max(1.0, np.max(np.abs(mixed)) / 0.9)
    tmp = OUTDIR + "/mixes/with-guide.wav"
    wavfile.write(tmp, rate, (mixed * 8388607).astype(np.int32) << 8)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-b:a", "192k", OUTDIR + "/mixes/lights-on-nobody-home-with-guide.mp3"], check=True)
    os.remove(tmp)
    print("guide mixed at %+.1f dB over the song" % (guide_db + 20 * np.log10(gain) - song_db))


if __name__ == "__main__":
    steps = [a for a in sys.argv[1:] if not a.startswith("--")] or ["score", "render", "mix"]
    for s in steps:
        {"score": score, "render": render, "mix": mix}[s]()
