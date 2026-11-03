# scripts/ilkley-allegretto/make.py
#
# "Ilkley Allegretto": "On Ilkla Moor Baht 'at" (the Methodist hymn tune Cranbrook, Thomas Clark, 1805) played over the repeating
# rhythm of the second movement of Beethoven's Seventh Symphony (1812). Both are out of copyright. 76 bpm, A minor and A major.
#
# The melodies were read from sheet music, not from memory:
#   Ilkla Moor     https://nigelgatherer.com/tunes/tunes/zWorld/MNO/OnIlk/OnIlk.pdf (D major, 4/4; here moved down a fifth to A)
#   Beethoven      the top line of the opening of the Allegretto, from a cello trio arrangement,
#                  https://www.8notes.com/scores/36821.asp (A minor, 2/4), checked against the opening chords on
#                  https://en.wikipedia.org/wiki/Symphony_No._7_(Beethoven). The chords of its bars 3 to 10 are the arrangement's;
#                  the chords under its bars 11 to 18 are chosen here.
#
# Beats are quarter notes and a bar of this song is four of them, so one bar of Beethoven's 2/4 is half a bar here.
#
#   python3 make.py circuits | song | score | render | mix (--version=vN)      with no argument, all of them
import os, sys, random

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
sys.path.insert(0, os.path.join(VALIS, "scripts", "song"))
import midiw, songlib

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "ilkley-allegretto"))
BPM = 76
SECTIONS = [("intro", 2), ("theme", 8), ("ilkla", 21), ("dialogue", 21), ("finale", 8), ("outro", 6)]
BARS = sum(n for _, n in SECTIONS)
START = {}
_b = 0
for _n, _l in SECTIONS:
    START[_n] = _b
    _b += _l

# --- Ilkla Moor ---------------------------------------------------------------------------------------------------------------------

# In D major, one entry for each bar of four beats: (length in beats, MIDI note; 0 is a rest). A pickup is the last beat of the bar before
# its line. Two entries are longer than a bar because of a tie, and the entry after each is empty.
D4, E4, Fs4, G4, A4, B4, Cs5, D5, E5, Fs5 = 62, 64, 66, 67, 69, 71, 73, 74, 76, 78
ILKLA = [
    [(2, D5), (1.5, A4), (.5, B4)],                  # 0   Where hast thou been
    [(1, A4), (1, G4), (1, Fs4), (1, E4)],           # 1   sin' ah saw
    [(3, D4), (1, A4)],                              # 2   thee, and the pickup "On"
    [(1, D5), (1, Cs5), (1, B4), (1, A4)],           # 3   Il-kla Moor baht
    [(1, B4), (1, A4), (1, G4), (1, Fs4)],           # 4
    [(2, Fs4), (2, E4)],                             # 5   'at
    [(2, A4), (1.5, A4), (.5, B4)],                  # 6   Where hast thou been
    [(1, Cs5), (1, A4), (1, B4), (1, Cs5)],          # 7   sin' ah saw
    [(4, D5)],                                       # 8   thee
    [(2, E5), (1.5, E5), (.5, D5)],                  # 9   Where hast thou been
    [(1, Cs5), (1, E5), (1, B4), (1, E5)],           # 10  sin' ah saw
    [(6, A4), (1, 0), (1, A4)],                      # 11  thee: a whole note tied to a half, a rest, the pickup (two bars)
    [],                                              # 12
    [(1.5, D5), (.5, D5), (1, D5), (1, A4)],         # 13  On Il-kla Moor baht
    [(3, D5), (1, E5)],                              # 14  'at, on
    [(1.5, Fs5), (.5, Fs5), (1, Fs5), (1, E5)],      # 15  Il-kla Moor baht
    [(3, Fs5), (1, Fs5)],                            # 16  'at, on
    [(2, E5), (2, D5)],                              # 17  Il-kla
    [(2, D5), (2, Cs5)],                             # 18  Moor baht
    [(8, D5)],                                       # 19  'at (a whole note tied to a whole note, two bars)
    [],                                              # 20
]

# the chord under each beat of each bar, in A major (the chords of the original moved down a fifth)
CH_MAJOR = [["A"] * 4, ["E7"] * 4, ["A"] * 4, ["D"] * 4, ["Bm"] * 4, ["E7"] * 4, ["E7"] * 4, ["E7"] * 4, ["A"] * 4,
            ["B"] * 4, ["E7", "E7", "B7", "B7"], ["E7"] * 4, ["E7"] * 4,
            ["A", "A", "A", "E7"], ["A", "A", "A", "E7"], ["A", "A", "A", "E7"], ["A"] * 4,
            ["Bm", "Bm", "A", "A"], ["D", "D", "E7", "E7"], ["A"] * 4, ["A"] * 4]
# the same in A minor: each major chord is replaced by a minor one or by the dominant
MINOR_OF = {"A": "Am", "E7": "E7", "D": "Dm", "Bm": "E7", "B": "E7", "B7": "E7"}


def ilkla_events(minor):
    """[(beat, length, note)] for the whole tune from beat 0, moved down a fifth, and with the third and sixth lowered for the minor."""
    out, beat = [], 0.0
    for items in ILKLA:
        for ln, note in items:
            if note:
                n = note - 5
                if minor and n % 12 in (1, 6):
                    n -= 1                               # C# to C and F# to F
                out.append((beat, ln, n))
            beat += ln
    return out


# --- Beethoven ----------------------------------------------------------------------------------------------------------------------

E3, Fs3, G3, Gs3, A3, B3, C4 = 52, 54, 55, 56, 57, 59, 60
# bars 3 to 10 and 11 to 18 of the Allegretto, as (beat in 32, length, note): the top line of the arrangement
BEETHOVEN = [
    (0, 1, E3), (1, .5, E3), (1.5, .5, E3), (2, 1, E3), (3, 1, E3),
    (4, 1, E3), (5, .5, E3), (5.5, .5, E3), (6, 1, E3), (7, 1, E3),
    (8, 1, E3), (9, .5, E3), (9.5, .5, Fs3), (10, 1, G3), (11, 1, G3),
    (12, 1, B3), (13, .5, A3), (13.5, .5, B3), (14, 2, C4),
    (16, 1, G3), (17, .5, G3), (17.5, .5, A3), (18, 1, B3), (19, 1, B3),
    (20, 1, Fs3), (21, .5, Fs3), (21.5, .5, Gs3), (22, 1, A3), (23, 1, A3),
    (24, 1, E3), (25, .5, E3), (25.5, .5, E3), (26, 1, E3), (27, 1, E3),
    (28, 1, E3), (29, .5, Fs3), (29.5, .5, Gs3), (30, 2, A3),
]
# the chord under each bar of Beethoven's 2/4 (two beats), bars 3 to 18
BEETHOVEN_CHORDS = ["Am", "E", "E", "Am", "Am", "C", "G", "C", "C", "G", "Bm", "Am", "Am", "E", "E", "Am"]
# a bar of 2/4 is a quarter and two eighths, then two quarters; the last bar of each eight is a half note
HITS_A, HITS_B, HITS_LAST = [(0, .9), (1, .45), (1.5, .45)], [(0, .9), (1, .9)], [(0, 1.9)]

VOICING = {   # chord: (guitar notes, sub root)
    "A": ((57, 61, 64), 33), "Am": ((57, 60, 64), 33), "E": ((56, 59, 64), 40), "E7": ((56, 59, 62, 64), 40),
    "D": ((57, 62, 66), 38), "Dm": ((57, 62, 65), 38), "Bm": ((54, 59, 62), 35), "B": ((54, 59, 63), 35), "B7": ((54, 59, 63, 69), 35),
    "C": ((55, 60, 64), 36), "G": ((55, 59, 62), 31),
}

# --- circuits ---------------------------------------------------------------------------------------------------------------------

CIRCUITS = {
    "cello": "cello", "trumpets": "trumpets", "flute": "flute", "guitar": "nylon-guitar", "strings": "violins",
    "horns": "horn-section", "sub": "dub-bass", "kick": "808-bd", "shakers": "latin-perc", "reverb-return": "reverb-return",
}


# the cello circuit has no limiter and its level varies with the note (G3 peaks at 0.75 with the output at -34 dB, B3 at 0.31), so the copy is turned down
EDITS = {"cello": [(":level a val:Gain ; val:gain -34.0 .", ":level a val:Gain ; val:gain -41.0 .")]}


def make_circuits():
    os.makedirs(os.path.join(ART, "circuits"), exist_ok=True)
    for name, source in CIRCUITS.items():
        ttl = open(os.path.join(VALIS, "circuits", source + ".ttl")).read()
        for old, new in EDITS.get(name, []):
            assert old in ttl, (name, old)
            ttl = ttl.replace(old, new, 1)
        ttl = ttl.replace("# circuits/%s.ttl" % source, "# circuits/%s.ttl (a copy of %s for \"Ilkley Allegretto\")" % (name, source), 1)
        open(os.path.join(ART, "circuits", name + ".ttl"), "w").write(ttl)
    print("circuits:", len(CIRCUITS))


PARTS = [  # name, circuit, rms level dB where it plays, pan, highpass
    ("kick", "kick", -24, 0.0, 0),
    ("sub", "sub", -23, 0.0, 0),
    ("shakers", "shakers", -31, 0.3, 300),
    ("cello", "cello", -22, -0.2, 60),
    ("guitar", "guitar", -25, 0.25, 100),
    ("strings", "strings", -29, 0.0, 150),
    ("trumpets", "trumpets", -24, 0.0, 150),
    ("flute", "flute", -28, 0.15, 250),
    ("horns", "horns", -28, -0.25, 150),
]
RETURNS = [("brasshall", "trumpets", -30, 0.4), ("cellohall", "cello", -31, -0.4)]
SECTION_LEVEL = {"intro": 0.0, "theme": 0.0, "ilkla": 1.0, "dialogue": 0.0, "finale": 2.5, "outro": -1.5}


def song_ttl():
    lines = ['# song.ttl', '#', '# "Ilkley Allegretto": the layout and the mix as data. The notes are in midi/, played by the circuits in circuits/.', '',
             '@prefix val:  <http://purl.org/stuff/valis/> .', '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
             '@prefix :     <urn:valis-artifacts:ilkley-allegretto#> .', '',
             ':song a val:Song ;', '    val:title "Ilkley Allegretto" ;', '    val:tempo %d ;' % BPM, '    val:loudness -14 ;',
             '    val:fadeSeconds 6 ;', '    val:roomAmount 0.18 ;', '    val:roomDecay 0.45 ;', '    val:roomLowpass 6000 ;', '    val:drive 1.2 ;',
             '    val:hasSection ' + " , ".join(":" + n for n, _ in SECTIONS) + " ;",
             '    val:hasPart ' + " , ".join(":" + p[0] for p in PARTS) + " ;",
             '    val:hasReturn ' + " , ".join(":" + r[0] for r in RETURNS) + " .", '']
    for i, (n, bars) in enumerate(SECTIONS, 1):
        lines.append(":%s a val:Section ; val:index %d ; val:bars %d ; val:level %s ." % (n, i, bars, SECTION_LEVEL[n]))
    lines.append("")
    for k, (name, circuit, level, pan, hp) in enumerate(PARTS, 1):
        lines.append(':%s a val:Part ; val:index %d ; val:circuit "circuits/%s.ttl" ; val:level %s ; val:pan %s ; val:highpass %s .'
                     % (name, k, circuit, level, pan, hp))
    lines.append("")
    for i, (name, source, level, pan) in enumerate(RETURNS, 1):
        lines.append(':%s a val:Return ; val:index %d ; val:source :%s ; val:circuit "circuits/reverb-return.ttl" ; val:level %s ; val:pan %s .'
                     % (name, i, source, level, pan))
    open(os.path.join(ART, "song.ttl"), "w").write("\n".join(lines) + "\n")
    print("song.ttl:", BARS, "bars,", "%.1f s" % (BARS * 4 * 60.0 / BPM))


# --- the score --------------------------------------------------------------------------------------------------------------------

def score():
    rnd = random.Random(1812)
    notes = {p[0]: [] for p in PARTS}

    def put(part, beat, length, note, vel, gate=0.92, loose=0.008):
        if note > 0:
            notes[part].append((max(0.0, beat + rnd.uniform(-loose, loose)), max(0.08, length * gate), note, max(1, min(127, int(vel)))))

    def chord_hits(part, beat, name, length, vel, strum=True, gate=0.9):
        for i, nt in enumerate(VOICING[name][0]):
            put(part, beat + (i * 0.012 if strum else 0), length, nt, vel + rnd.randint(-4, 4), gate=gate, loose=0.006)

    def ostinato(part, beat0, chord_at, vel):
        """One bar of four beats of the rhythm, a quarter, two eighths, two quarters; chord_at(beat in the bar) names the chord."""
        for b, ln in ((0, .9), (1, .45), (1.5, .45), (2, .9), (3, .9)):
            chord_hits(part, beat0 + b, chord_at(int(b)), ln, vel + (8 if b == 0 else (-6 if b % 1 else 0)))

    def beethoven_chords(part, beat0, which, vel, strum=True):
        """Beethoven's eight bars of 2/4, bars 3 to 10 (which 0) or 11 to 18 (which 1), as chords on his rhythm."""
        for i in range(8):
            name = BEETHOVEN_CHORDS[which * 8 + i]
            hits = HITS_LAST if i == 7 else (HITS_A if i % 2 == 0 else HITS_B)
            for b, ln in hits:
                chord_hits(part, beat0 + i * 2 + b, name, ln, vel + (6 if b == 0 else -5), strum=strum)

    def beethoven_melody(part, beat0, which, vel):
        for b, ln, nt in BEETHOVEN:
            if which * 16 <= b < which * 16 + 16:
                put(part, beat0 + b - which * 16, ln, nt, vel + (6 if b % 1 == 0 else -2) + rnd.randint(-4, 4), gate=0.96, loose=0.012)

    def beethoven_sub(beat0, which, vel):
        for i in range(8):
            put("sub", beat0 + i * 2, 1.8, VOICING[BEETHOVEN_CHORDS[which * 8 + i]][1], vel)

    def kick_bar(beat0, vel):
        put("kick", beat0, 1, 36, vel)
        put("kick", beat0 + 2, 1, 36, vel - 8)

    def sub_bar(beat0, chord_at, vel):
        for b in (0, 2):
            put("sub", beat0 + b, 1.8, VOICING[chord_at(b)][1], vel)

    def ilkla_at(part, beat0, minor, vel, first=0.0, last=1e9, shift=0, gate=0.94):
        """The tune's notes from tune beat `first` to `last`, placed so that `first` falls on `beat0`."""
        for b, ln, nt in ilkla_events(minor):
            if first <= b < last:
                put(part, beat0 + b - first, ln, nt + shift, vel + (5 if b % 1 == 0 else -3) + rnd.randint(-4, 4), gate=gate, loose=0.01)

    def tune_chord(minor):
        def f(tune_beat):
            name = CH_MAJOR[min(int(tune_beat // 4), len(CH_MAJOR) - 1)][int(tune_beat % 4)]
            return MINOR_OF[name] if minor else name
        return f

    # ---- intro: the opening chord, held and let go
    t = START["intro"] * 4
    for nt in (57, 60, 64):
        put("strings", t, 4, nt, 96, gate=1.0)
        put("strings", t + 4, 4, nt, 56, gate=1.0)
    put("sub", t, 8, 33, 70, gate=0.98)

    # ---- theme: Beethoven's melody in the cello over his chords on the guitar; the second half adds the sub and the strings
    t = START["theme"] * 4
    for which in (0, 1):
        base = t + which * 16
        beethoven_melody("cello", base, which, 58 + which * 6)
        beethoven_chords("guitar", base, which, 60 + which * 4)
        if which == 1:
            beethoven_sub(base, which, 76)
            for nt in VOICING[BEETHOVEN_CHORDS[8]][0]:
                put("strings", base, 16, nt, 52, gate=0.98)

    # ---- ilkla: the tune on trumpets in A major over the rhythm, joined by the strings, then by the flute an octave up
    t = START["ilkla"] * 4
    f = tune_chord(False)
    ilkla_at("trumpets", t, False, 84)
    for bar in range(21):
        tb = bar * 4
        ostinato("guitar", t + tb, lambda b, tb=tb: f(tb + b), 66)
        sub_bar(t + tb, lambda b, tb=tb: f(tb + b), 78)
        kick_bar(t + tb, 60 + (10 if bar >= 9 else 0))
        if bar >= 9:
            for nt in VOICING[f(tb)][0]:
                put("strings", t + tb, 4, nt, 58, gate=0.98)
    ilkla_at("flute", t + 36, False, 62, first=36.0, shift=12)

    # ---- dialogue: Beethoven's melody in the cello, answered by Ilkla Moor in A minor on the trumpets (84 beats in all)
    t = START["dialogue"] * 4
    fm = tune_chord(True)
    pos = 0.0
    for which, (lo, hi) in ((0, (0.0, 24.0)), (1, (24.0, 52.0))):
        beethoven_melody("cello", t + pos, which, 66)
        beethoven_chords("guitar", t + pos, which, 64)
        beethoven_sub(t + pos, which, 74)
        for bar in range(4):
            kick_bar(t + pos + bar * 4, 56)
        pos += 16
        ilkla_at("trumpets", t + pos, True, 88, first=lo, last=hi)
        for bar in range(int(hi - lo) // 4):
            tb = lo + bar * 4
            ostinato("guitar", t + pos + bar * 4, lambda b, tb=tb: fm(tb + b), 66)
            sub_bar(t + pos + bar * 4, lambda b, tb=tb: fm(tb + b), 78)
            kick_bar(t + pos + bar * 4, 64)
        pos += hi - lo

    # ---- finale: Beethoven's melody in the cello and his rhythm in the horns, Ilkla Moor over the top in A minor
    t = START["finale"] * 4
    for which, lo in ((0, 51.0), (1, 67.0)):
        base = t + which * 16
        beethoven_melody("cello", base, which, 70)
        beethoven_chords("guitar", base, which, 66)
        beethoven_chords("horns", base, which, 70, strum=False)
        beethoven_sub(base, which, 82)
        for nt in VOICING[BEETHOVEN_CHORDS[which * 8]][0]:
            put("strings", base, 16, nt, 62, gate=0.98)
        for bar in range(4):
            kick_bar(base + bar * 4, 72)
            for e in range(8):
                put("shakers", base + bar * 4 + e * 0.5, 0.4, 70, (62 if e % 2 == 0 else 40) + rnd.randint(-6, 6), loose=0.01)
        ilkla_at("trumpets", base, True, 94, first=lo, last=lo + 16 if which == 0 else 1e9)
        ilkla_at("flute", base, True, 70, first=lo, last=lo + 16 if which == 0 else 1e9, shift=12)

    # ---- outro: the rhythm on a single chord, thinning, over a held E and A
    t = START["outro"] * 4
    for bar in range(4):
        ostinato("guitar", t + bar * 4, lambda b, bar=bar: "Am" if bar < 3 else "E", 58 - bar * 8)
    put("cello", t, 8, E3, 52, gate=0.98)
    put("cello", t + 8, 16, 57, 46, gate=0.98)
    for nt in (57, 60, 64):
        put("strings", t, 16, nt, 52, gate=0.98)
    put("sub", t, 16, 33, 66, gate=0.98)
    put("kick", t, 1, 36, 50)

    os.makedirs(os.path.join(ART, "midi"), exist_ok=True)
    for part, lst in notes.items():
        if lst:
            lst.sort()
            midiw.write(os.path.join(ART, "midi", part + ".mid"), lst, BPM)
        print("%-9s %4d notes" % (part, len(lst)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=") for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    todo = args or ["circuits", "song", "score", "render", "mix"]
    os.makedirs(ART, exist_ok=True)
    if "circuits" in todo: make_circuits()
    if "song" in todo: song_ttl()
    if "score" in todo: score()
    song = None
    if "render" in todo or "mix" in todo:
        song = songlib.load(os.path.join(ART, "song.ttl"))
    if "render" in todo: songlib.render(song)
    if "mix" in todo: songlib.mix(song, opts.get("version", "v1"), arc=True)


if __name__ == "__main__":
    main()
