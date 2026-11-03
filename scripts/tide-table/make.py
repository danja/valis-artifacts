# scripts/tide-table/make.py
#
# "Tide Table": a slow nocturnal instrumental in D minor at 78 bpm, played by Valis circuits. Bowed and plucked strings carry the tune,
# bells and a fading pad carry the memory of it, and a soft heartbeat and brushed shakers keep the time:
#
#   cello.ttl            the voice: a bowed string and a wooden body (val:Bow)
#   harp.ttl             eight plucked strings (val:Pluck into val:StiffString), arpeggios and, in the memory, the tune
#   free-bell.ttl        a small bell of eight hand-set partials (val:FreeModalBank)
#   dx7-epiano.ttl       an FM electric piano, off the beat
#   quadra-strings.ttl   a string-machine pad
#   emulator-choir.ttl   an "ah" held by a bit-reducer
#   lofi-codec.ttl       the pad of the memory, run through a spectral codec (val:SpectralCodec) so it sounds remembered
#   dub-bass.ttl         the sub, one note at a time
#   808-bd.ttl           a heartbeat
#   latin-perc.ttl       the maracas, brushed
#
#   python3 make.py circuits | song | score | render | mix (--version=vN)      with no argument, all of them
import os, re, sys, random

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
sys.path.insert(0, os.path.join(VALIS, "scripts", "song"))
import midiw, songlib

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "tide-table"))
BPM = 78
BEAT = 60.0 / BPM
SECTIONS = [("intro", 8), ("tide", 16), ("rise", 16), ("memory", 8), ("flood", 16), ("ebb", 8)]
BARS = sum(n for _, n in SECTIONS)

# chord: (sub root, harp/strings voicing, top note of the choir)
CH = {
    "Dm": (38, (50, 53, 57, 62), 69),
    "Bb": (34, (46, 50, 53, 58), 65),
    "F":  (41, (53, 57, 60, 65), 72),
    "C":  (36, (48, 52, 55, 60), 67),
    "Gm": (31, (55, 58, 62, 67), 70),
    "A":  (33, (57, 61, 64, 69), 69),
}
PROG_A = ["Dm", "Bb", "F", "C"]
PROG_B = ["Dm", "Gm", "Bb", "A"]

# the tune over PROG_A, two bars to a chord, as (beat in the bar, length, note); 0 is a rest
D4, F4, G4, A4, Bb3, C5, E4, D5 = 62, 65, 67, 69, 58, 72, 64, 74
TUNE = [[(0, 3, D4), (3, 1, F4)], [(0, 2, A4), (2, 2, G4)],
        [(0, 3, F4), (3, 1, D4)], [(0, 4, Bb3)],
        [(0, 2, A4), (2, 1, C5), (3, 1, A4)], [(0, 4, F4)],
        [(0, 2, G4), (2, 2, E4)], [(0, 3, D4)]]


def set_prop(ttl, node, prop, value):
    i = ttl.index("\n:%s a val:" % node) + 1
    j = ttl.index(" .\n", i)
    block = ttl[i:j]
    if re.search(r"val:%s " % prop, block):
        block = re.sub(r"(val:%s )[-0-9.e]+" % prop, lambda m: m.group(1) + str(value), block, count=1)
    else:
        block += " ;\n    val:%s %s" % (prop, value)
    return ttl[:i] + block + ttl[j:]


CIRCUITS = {
    "cello": ("cello", []), "harp": ("harp", []), "bell": ("free-bell", []), "epiano": ("dx7-epiano", []),
    "strings": ("quadra-strings", []), "choir": ("emulator-choir", []), "sub": ("dub-bass", []), "heart": ("808-bd", []),
    "shakers": ("latin-perc", []), "reverb-return": ("reverb-return", []),
    "ghost": ("lofi-codec", [("codec", "bandwidth", 5000.0), ("codec", "floor", 18.0), ("codec", "step", 8.0)]),
}


def make_circuits():
    os.makedirs(os.path.join(ART, "circuits"), exist_ok=True)
    for name, (source, edits) in CIRCUITS.items():
        ttl = open(os.path.join(VALIS, "circuits", source + ".ttl")).read()
        for node, prop, value in edits:
            ttl = set_prop(ttl, node, prop, value)
        ttl = ttl.replace("# circuits/%s.ttl" % source, "# circuits/%s.ttl (a copy of %s for \"Tide Table\", set as listed in scripts/tide-table/make.py)" % (name, source), 1)
        open(os.path.join(ART, "circuits", name + ".ttl"), "w").write(ttl)
    print("circuits:", len(CIRCUITS))


def locate(bar):
    start = 0
    for name, n in SECTIONS:
        if bar < start + n:
            return name, bar - start, n
        start += n


def chord_of(sec, i):
    k = (i // 2) % 4
    if sec == "rise":
        return PROG_B[k]
    if sec == "flood":
        return PROG_B[k] if i < 8 else PROG_A[k]
    return PROG_A[k]


PARTS = [  # name, circuit, rms level dB where it plays, pan, highpass
    ("heart", "heart", -22, 0.0, 0),
    ("sub", "sub", -23, 0.0, 0),
    ("shakers", "shakers", -31, 0.3, 300),
    ("cello", "cello", -22, -0.1, 60),
    ("harp", "harp", -24, 0.2, 100),
    ("bell", "bell", -29, 0.35, 300),
    ("epiano", "epiano", -28, -0.3, 150),
    ("strings", "strings", -30, 0.0, 150),
    ("choir", "choir", -31, 0.0, 200),
    ("ghost", "ghost", -29, -0.2, 120),
]
RETURNS = [("harphall", "harp", -30, 0.4), ("cellohall", "cello", -31, -0.4)]
SECTION_LEVEL = {"intro": -1.0, "tide": 0.0, "rise": 1.5, "memory": -2.5, "flood": 2.5, "ebb": 0.0}


def song_ttl():
    lines = ['# song.ttl', '#', '# "Tide Table": the layout and the mix as data. The notes are in midi/, played by the circuits in circuits/.', '',
             '@prefix val:  <http://purl.org/stuff/valis/> .', '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
             '@prefix :     <urn:valis-artifacts:tide-table#> .', '',
             ':song a val:Song ;', '    val:title "Tide Table" ;', '    val:tempo %d ;' % BPM, '    val:loudness -14 ;',
             '    val:fadeSeconds 8 ;', '    val:roomAmount 0.2 ;', '    val:roomDecay 0.5 ;', '    val:roomLowpass 6000 ;', '    val:drive 1.2 ;',
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
    print("song.ttl:", BARS, "bars,", "%.1f s" % (BARS * 4 * BEAT))


def score():
    rnd = random.Random(1973)
    notes = {p[0]: [] for p in PARTS}

    def beat(part, bar, b, length, note, vel, gate=0.9, loose=0.012):
        if note > 0:
            start = max(0.0, bar * 4 + b + rnd.uniform(-loose, loose))
            notes[part].append((start, max(0.1, length * gate), note, max(1, min(127, int(vel)))))

    for bar in range(BARS):
        sec, i, n = locate(bar)
        name = chord_of(sec, i)
        root, tri, top = CH[name]
        two = i // 2 % 4               # which chord of the loop
        tune_bar = TUNE[(i % 8)] if sec in ("tide", "flood", "ebb", "memory", "intro") else None
        last = i == n - 1

        # ---- the heartbeat: low and slow, then four to the bar
        if sec in ("tide", "memory") and sec != "memory":
            beat("heart", bar, 0, 1, 36, 70)
            beat("heart", bar, 2.5, 0.5, 36, 52)
        if sec in ("rise", "flood"):
            for b in range(4):
                beat("heart", bar, b, 0.5, 36, 72 if b == 0 else 58)
        if sec == "ebb" and i < 4:
            beat("heart", bar, 0, 1, 36, 60)
        if sec == "intro" and i >= 6:
            beat("heart", bar, 0, 1, 36, 44)

        # ---- the sub: the root, with the kick, and a pickup into the next chord
        if sec in ("tide", "rise", "flood") or (sec == "ebb" and i < 4):
            beat("sub", bar, 0, 2.5 if sec != "rise" and sec != "flood" else 1.5, root, 88)
            if sec in ("rise", "flood"):
                beat("sub", bar, 2, 1, root, 76)
                beat("sub", bar, 3.5, 0.5, root + 7 if rnd.random() < 0.5 else root + 12, 70)

        # ---- the maracas: brushed eighths, the weak ones softer
        if sec in ("tide", "rise", "flood"):
            for k in range(8):
                beat("shakers", bar, k * 0.5, 0.4, 70, (62 if k % 2 == 0 else 40) + rnd.randint(-6, 6), loose=0.01)
            if sec == "flood":
                for k in range(8):
                    beat("shakers", bar, k * 0.5 + 0.25, 0.2, 70, 30 + rnd.randint(-4, 4), loose=0.01)

        # ---- the cello: a drone in the intro, the tune in the tide and the flood, a pedal under the rise, the tune once more in the ebb
        if sec == "intro":
            if i % 2 == 0:
                beat("cello", bar, 0, 8, root + 24 if root < 36 else root + 12 - 12 + 12, 48, gate=0.98, loose=0.02)
        elif sec in ("tide", "flood", "ebb") and tune_bar is not None:
            for b, ln, nt in tune_bar:
                beat("cello", bar, b, ln, nt, (60 if sec != "ebb" else 44) + rnd.randint(-5, 5), gate=0.96, loose=0.02)
        elif sec == "rise":
            if i % 2 == 0:
                beat("cello", bar, 0, 8, tri[1] + 12 - 12, 52, gate=0.98, loose=0.02)

        # ---- the harp: arpeggios; in the memory it plays the tune alone
        pattern = (0, 1, 2, 3, 2, 1, 2, 3)
        if sec == "intro" and i >= 2 and i % 2 == 1:
            for k, idx in enumerate((0, 2, 3)):
                beat("harp", bar, k * 1.0, 3, tri[idx] + 12, 62 + rnd.randint(-4, 4), gate=1.0)
        if sec in ("tide", "rise", "flood", "ebb"):
            if sec != "ebb" or i < 6:
                for k, idx in enumerate(pattern):
                    up = 12 if (sec in ("rise", "flood") and k >= 4 and i % 2 == 1) else 0
                    beat("harp", bar, k * 0.5, 1.2, tri[idx] + 12 + up, 70 + (10 if k % 4 == 0 else 0) + rnd.randint(-6, 6), gate=1.0)
        if sec == "memory":
            for b, ln, nt in TUNE[i % 8]:
                beat("harp", bar, b, ln * 1.5, nt + 12, 78 + rnd.randint(-4, 4), gate=1.0)

        # ---- the bell: droplets from the chord, high and not on the beat
        if sec in ("intro", "tide", "memory", "ebb") or (sec == "flood" and i % 2 == 1):
            drops = {"intro": 1, "tide": 2, "memory": 3, "ebb": 1, "flood": 1}[sec]
            for _ in range(drops):
                b = rnd.choice((0.5, 1.5, 2.5, 3.5, 1.0, 3.0)) if sec != "memory" else rnd.choice((1.5, 3.5))
                beat("bell", bar, b, 1.6, rnd.choice(tri) + rnd.choice((24, 36)), 60 + rnd.randint(-8, 8), gate=1.0)
        if last and sec in ("tide", "rise", "flood"):
            beat("bell", bar, 3.0, 1.0, 86, 74)

        # ---- the electric piano: off the beat, the chord's inner voices
        if sec in ("rise", "flood"):
            for b in (1.5, 3.0 if sec == "flood" else 3.5):
                for nt in (tri[1] + 12, tri[2] + 12):
                    beat("epiano", bar, b, 0.5, nt, 62 + rnd.randint(-5, 5), gate=0.9, loose=0.008)

        # ---- the pad: whole-bar chords, held
        if sec in ("rise", "flood") or (sec == "ebb" and i >= 2):
            for nt in tri[:3]:
                beat("strings", bar, 0, 4, nt + 12, 72 if sec != "ebb" else 56, gate=0.98, loose=0.015)

        # ---- the choir: two bars on the top note of the chord
        if sec in ("flood",) and i % 2 == 0:
            beat("choir", bar, 0, 8, top, 76, gate=0.98, loose=0.02)
        if sec == "ebb" and i == 0:
            beat("choir", bar, 0, 16, 62, 64, gate=0.98, loose=0.02)

        # ---- the remembered pad: one slow note a bar on a thin codec
        if sec == "memory":
            beat("ghost", bar, 0, 4, tri[(i % 3)] + 12, 84, gate=1.0)
        if sec == "ebb" and i >= 4:
            beat("ghost", bar, 0, 4, tri[0] + 12, 66, gate=1.0)

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
