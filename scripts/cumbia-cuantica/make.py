# scripts/cumbia-cuantica/make.py
#
# "Cumbia Cuántica": an avant-garde cumbia in A minor at 94 bpm, played by Valis circuits. A simplified cumbia rhythm section
# (guacharaca, llamador, maracas, tambor alegre, bombo, guitarron) and a gaita-style flute carry it; the circuits written to
# show one element each are the avant-garde part:
#
#   bassman-amp.ttl     the guitar, a Fender Bassman tone stack and valve in front of a plucked string (psychedelic "chicha" cumbia)
#   distortion-bench    two copies, set to a hard clip (fuzz) and to a diode (buzz)
#   lofi-codec.ttl      a ghost pad, and a harder-set copy for the break
#   arp-quantiser.ttl   a scrambled sequence forced into A minor pentatonic, in triplets against the bar
#   vocoder-speak.ttl   a talk box: the nursery-rhyme speech of "All Fall Down" shapes a played carrier
#
#   python3 make.py circuits   copies and sets the circuits  -> artifacts/cumbia-cuantica/circuits/
#   python3 make.py song       writes song.ttl
#   python3 make.py score      writes one MIDI file for each part -> midi/
#   python3 make.py recorded   renders the arpeggio and the talk box -> wavs/ (they need no part of the song format)
#   python3 make.py render     renders every part
#   python3 make.py mix        mixes (--version=vN)
#   python3 make.py            circuits, song, score, recorded, render, mix
import os, re, sys, random, shutil, subprocess, wave
import numpy as np

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
sys.path.insert(0, os.path.join(VALIS, "scripts", "song"))
import midiw, songlib

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "cumbia-cuantica"))
BPM = 94
BEAT = 60.0 / BPM
RATE = 48000

SECTIONS = [("intro", 8), ("cumbia1", 16), ("quantise", 16), ("talk", 16), ("fracture", 8), ("cumbia2", 16), ("outro", 8)]
BARS = sum(n for _, n in SECTIONS)
TAIL = 10.0
SONG_SECONDS = BARS * 4 * BEAT + TAIL

# chord: (guitarron root, guitarron fifth, guitar tones, buzz tones)
CH = {
    "Am": (33, 40, (57, 60, 64), (57, 60, 64)),
    "Dm": (38, 33, (62, 65, 69), (62, 65, 69)),
    "E7": (40, 35, (64, 68, 74), (64, 68, 67)),
    "G":  (31, 38, (55, 59, 62), (59, 62, 67)),
    "F":  (29, 36, (53, 57, 60), (57, 60, 65)),
}
CUMBIA = ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "E7"]
ANDALUSIAN = ["Am", "G", "F", "E7"]
OUTRO = ["Am", "Dm", "E7", "Am"]

# The gaita tune, eight bars of A minor pentatonic (A C D E G), as (beat, length, note). It answers itself: bars 1-2 ask, 3-4 reply.
A, C, D, E, G = 69, 72, 74, 76, 79
TUNE = [[(0, 1, A), (1.5, .5, C), (2, 1, E), (3, 1, D)],
        [(0, 1.5, C), (1.5, .5, A), (2, 2, A)],
        [(0, 1, D), (1.5, .5, E), (2, 1, G), (3, 1, E)],
        [(0, 1, D), (1, 1, C), (2, 2, A)],
        [(0, 1, E), (1.5, .5, E), (2, 1, G), (3, 1, A + 12)],
        [(0, 1.5, G), (1.5, .5, E), (2, 2, D)],
        [(0, 1, C), (1, .5, D), (1.5, .5, E), (2, 1, D), (3, 1, C)],
        [(0, 3, A), (3, 1, 0)]]

# --- the circuits of the track: copies of the Valis ones, some with their panel set differently -------------------------------

def set_prop(ttl, node, prop, value):
    """Sets val:<prop> on the node `:<node>`, adding it if the node does not have it."""
    i = ttl.index("\n:%s a val:" % node) + 1
    j = ttl.index(" .\n", i)
    block = ttl[i:j]
    if re.search(r"val:%s " % prop, block):
        block = re.sub(r"(val:%s )[-0-9.e]+" % prop, lambda m: m.group(1) + str(value), block, count=1)
    else:
        block += " ;\n    val:%s %s" % (prop, value)
    return ttl[:i] + block + ttl[j:]


CIRCUITS = {   # name: (source circuit, [(node, property, value)])
    "latin-perc": ("latin-perc", []),
    "guitarron": ("guitarron", []),
    "flute": ("flute", []),
    "reverb-return": ("reverb-return", []),
    # a Bassman with the input pushed, so the valve breaks up
    "surf": ("bassman-amp", [("input", "gain", 14.0), ("preamp", "bias", -2.5), ("power", "gain", 2.5), ("stack", "middle", 0.25),
                             ("stack", "treble", 0.7), ("pick", "hardness", 0.75)]),
    # curve 0, a hard clip at a low threshold: fuzz
    "fuzz": ("distortion-bench", [("curve", "a", 0.0), ("drive", "gain", 24.0), ("hard", "threshold", 0.25)]),
    # curve 3, a diode: lopsided, so even harmonics too
    "buzz": ("distortion-bench", [("curve", "a", 3.0), ("drive", "gain", 14.0), ("osc", "shape", 2), ("level", "gain", -12.0)]),
    "ghost": ("lofi-codec", [("codec", "bandwidth", 7000.0), ("codec", "floor", 22.0), ("codec", "step", 5.0)]),
    "ghostbreak": ("lofi-codec", [("codec", "bandwidth", 2500.0), ("codec", "floor", 14.0), ("codec", "step", 12.0), ("hissLvl", "gain", -22.0)]),
    # A minor pentatonic (root A is 9, scale 6), a step of a third of a beat: sixteen steps last 5 1/3 beats against four
    "arp": ("arp-quantiser", [("quant", "root", 9.0), ("quant", "scale", 6.0), ("seqRef", "division", 0.3333), ("seqPlay", "division", 0.3333),
                              ("seqRef", "gatelength", 0.5), ("seqPlay", "gatelength", 0.5), ("midi", "velocity", 0.8)]),
    "talkbox": ("vocoder-speak", []),
}


def make_circuits():
    os.makedirs(os.path.join(ART, "circuits"), exist_ok=True)
    for name, (source, edits) in CIRCUITS.items():
        ttl = open(os.path.join(VALIS, "circuits", source + ".ttl")).read()
        for node, prop, value in edits:
            ttl = set_prop(ttl, node, prop, value)
        ttl = ttl.replace("# circuits/%s.ttl" % source, "# circuits/%s.ttl (a copy of %s for \"Cumbia Cuántica\", set as listed in scripts/cumbia-cuantica/make.py)" % (name, source), 1)
        open(os.path.join(ART, "circuits", name + ".ttl"), "w").write(ttl)
    print("circuits:", len(CIRCUITS))


# --- the plan -------------------------------------------------------------------------------------------------------------------

def locate(bar):
    start = 0
    for name, n in SECTIONS:
        if bar < start + n:
            return name, bar - start, n
        start += n


def first_bar(section):
    start = 0
    for name, n in SECTIONS:
        if name == section:
            return start
        start += n


def chord_of(sec, i):
    if sec in ("cumbia1", "cumbia2"):
        return CUMBIA[i % 8]
    if sec == "quantise":
        return ANDALUSIAN[i % 4]
    if sec == "talk":
        return "E7" if i >= 12 else "Am"
    if sec == "fracture":
        return "E7"
    if sec == "intro":
        return "Am" if i < 4 else CUMBIA[i - 4]
    return OUTRO[i % 4]


PARTS = [  # name, circuit, level dB (rms where it plays), pan, highpass, follows
    ("shakers", "latin-perc", -26, 0.25, 250, None),
    ("guacha", "latin-perc", -25, -0.3, 200, None),
    ("hand", "latin-perc", -22, 0.0, 70, None),
    ("guitarron", "guitarron", -21, 0.0, 0, None),
    ("flute", "flute", -23, 0.1, 150, None),
    ("surf", "surf", -23, -0.35, 120, None),
    ("fuzz", "fuzz", -24, 0.0, 70, None),
    ("buzz", "buzz", -27, 0.3, 140, None),
    ("ghost", "ghost", -31, -0.15, 90, None),
    ("ghostbreak", "ghostbreak", -29, 0.2, 90, None),
]
RECORDED = [("arp", -27, 0.4, 150), ("talkbox", -24, 0.0, 120)]
RETURNS = [("surfverb", "surf", -30, 0.4), ("flutehall", "flute", -32, -0.4)]
SECTION_LEVEL = {"intro": 1.5, "cumbia1": 0.0, "quantise": 0.0, "talk": 3.0, "fracture": 0.0, "cumbia2": 0.5, "outro": 1.0}


def song_ttl():
    lines = ['# song.ttl', '#',
             '# "Cumbia Cuántica": the layout and the mix as data. The notes are in midi/, played by the circuits in circuits/;',
             '# the arpeggio and the talk box are rendered by scripts/cumbia-cuantica/make.py (recorded) because one has no notes and the',
             '# other is shaped by a voice. See README.md.', '',
             '@prefix val:  <http://purl.org/stuff/valis/> .', '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
             '@prefix :     <urn:valis-artifacts:cumbia-cuantica#> .', '',
             ':song a val:Song ;', '    val:title "Cumbia Cuántica" ;', '    val:tempo %d ;' % BPM, '    val:loudness -11 ;',
             '    val:fadeSeconds 6 ;', '    val:roomAmount 0.12 ;', '    val:roomDecay 0.35 ;', '    val:roomLowpass 5000 ;', '    val:drive 1.4 ;',
             '    val:hasSection ' + " , ".join(":" + n for n, _ in SECTIONS) + " ;",
             '    val:hasPart ' + " , ".join(":" + p[0] for p in PARTS) + " , " + " , ".join(":" + r[0] for r in RECORDED) + " ;",
             '    val:hasReturn ' + " , ".join(":" + r[0] for r in RETURNS) + " .", '']
    for i, (n, bars) in enumerate(SECTIONS, 1):
        lines.append(":%s a val:Section ; val:index %d ; val:bars %d ; val:level %s ." % (n, i, bars, SECTION_LEVEL[n]))
    lines.append("")
    k = 1
    for name, circuit, level, pan, hp, follows in PARTS:
        extra = " ; val:follows :%s" % follows if follows else ""
        lines.append(':%s a val:Part ; val:index %d ; val:circuit "circuits/%s.ttl" ; val:level %s ; val:pan %s ; val:highpass %s%s .'
                     % (name, k, circuit, level, pan, hp, extra))
        k += 1
    for name, level, pan, hp in RECORDED:
        lines.append(':%s a val:Part ; val:index %d ; val:recorded true ; val:level %s ; val:pan %s ; val:highpass %s .' % (name, k, level, pan, hp))
        k += 1
    lines.append("")
    for i, (name, source, level, pan) in enumerate(RETURNS, 1):
        lines.append(':%s a val:Return ; val:index %d ; val:source :%s ; val:circuit "circuits/reverb-return.ttl" ; val:level %s ; val:pan %s .'
                     % (name, i, source, level, pan))
    open(os.path.join(ART, "song.ttl"), "w").write("\n".join(lines) + "\n")
    print("song.ttl:", BARS, "bars,", "%.1f s" % (BARS * 4 * BEAT))


# --- the score ------------------------------------------------------------------------------------------------------------------

def score():
    rnd = random.Random(1948)
    notes = {p[0]: [] for p in PARTS}
    notes["talkbox"] = []

    def add(part, bar, step, length_steps, note, vel, shift=0.0, gate=0.85):
        start = max(0.0, (bar * 16 + step) * 0.25 + shift)
        notes[part].append((start, max(0.05, length_steps * 0.25 * gate), note, max(1, min(127, int(vel)))))

    def beat(part, bar, b, length, note, vel):
        if note > 0:
            notes[part].append((bar * 4 + b + rnd.uniform(0, 0.012), max(0.1, length * 0.92), note, int(vel)))

    for bar in range(BARS):
        sec, i, n = locate(bar)
        name = chord_of(sec, i)
        root, fifth, tones, buzz = CH[name]
        full = sec in ("cumbia1", "cumbia2", "quantise", "talk", "outro") or (sec == "intro" and i >= 2)
        groove = sec in ("cumbia1", "cumbia2", "quantise", "outro") or (sec == "intro" and i >= 4)
        last = i == n - 1
        fill = last and sec not in ("outro",)

        # ---- maracas: steady eighths, the offbeat accented
        if full and not (sec == "outro" and i == 7):
            for st in range(0, 16, 2):
                add("shakers", bar, st, 1, 70, (92 if st % 4 == 2 else 62) + rnd.randint(-5, 5))
            if sec in ("cumbia2", "fracture") and bar % 2 == 1:
                for st in range(1, 16, 2):
                    add("shakers", bar, st, 1, 70, 40 + rnd.randint(-4, 4))
        elif sec == "fracture":
            for st in range(0, 16, 3):                       # sixteen steps in threes: the bar does not divide
                add("shakers", bar, st, 1, 70, 90)

        # ---- guacharaca: the scrape, down on the beat and up between
        if (full and sec != "talk") and not (sec == "outro" and i == 7):
            for st, nt, v in ((0, 73, 78), (2, 74, 56), (3, 74, 60), (4, 73, 80), (6, 74, 56), (7, 74, 60),
                              (8, 73, 78), (10, 74, 56), (11, 74, 60), (12, 73, 80), (14, 74, 56), (15, 74, 60)):
                add("guacha", bar, st, 1, nt, v + rnd.randint(-5, 5))
        if sec == "talk" and i % 2 == 0:
            for st in (0, 4, 8, 12):
                add("guacha", bar, st, 1, 73, 54)

        # ---- hand drums: the bombo on the beat, the llamador between, the alegre improvising
        if groove or sec == "talk":
            for st, nt, v in ((0, 36, 96), (8, 36, 88)):
                add("hand", bar, st, 1, nt, v)
            for st in (2, 6, 10, 14):                            # llamador: a muted high bongo
                add("hand", bar, st, 1, 61, 70 + rnd.randint(-5, 5))
        if groove and sec != "intro":
            alegre = [((3, 64, 80), (7, 63, 70), (11, 64, 84), (13, 62, 100)),
                      ((3, 64, 80), (5, 63, 66), (9, 63, 70), (11, 64, 84), (14, 62, 96)),
                      ((1, 63, 64), (3, 64, 80), (7, 63, 70), (10, 63, 70), (12, 64, 90), (15, 62, 100))][bar % 3]
            for st, nt, v in alegre:
                add("hand", bar, st, 1, nt, v + rnd.randint(-4, 4))
        if fill and sec in ("cumbia1", "quantise", "cumbia2"):
            for k, st in enumerate(range(8, 16)):
                add("hand", bar, st, 1, (64, 63, 64, 63, 62, 63, 62, 62)[k], 64 + k * 6)
        if sec == "fracture":
            for k, st in enumerate((0, 1, 3, 4, 6, 9, 10, 12, 13, 15)):
                add("hand", bar, st, 1, (62, 63, 64)[k % 3], 88 + rnd.randint(-6, 6))
            add("hand", bar, 0, 1, 36, 110)
        if sec == "outro" and i == 7:
            add("hand", bar, 0, 1, 36, 110)

        # ---- guitarron: root and fifth, three and one
        if (groove or sec == "talk") and not (sec == "outro" and i == 7):
            for half in (0, 8):
                for st, nt, v in ((0, root, 108), (3, fifth, 86), (4, root, 96), (7, fifth, 84)):
                    add("guitarron", bar, half + st, 2, nt, v - (14 if sec == "talk" else 0), gate=0.8)
        if sec == "outro" and i == 7:
            add("guitarron", bar, 0, 12, root, 110)

        # ---- the flute: the tune, and a drone-like reply in the break
        if sec in ("intro",) and i >= 4:
            for b, ln, nt in TUNE[i - 4]:
                beat("flute", bar, b, ln, nt - 12, 76)
        if sec in ("cumbia1", "cumbia2"):
            for b, ln, nt in TUNE[i % 8]:
                beat("flute", bar, b, ln, nt, 92 if sec == "cumbia2" else 84)
        if sec == "quantise" and i % 4 in (0, 2):
            beat("flute", bar, 0, 3.5, root + 36 if root + 36 <= 81 else root + 24, 80)
        if sec == "outro" and i < 4:
            for b, ln, nt in TUNE[i + 4]:
                beat("flute", bar, b, ln, nt - 12, 70)

        # ---- the surf guitar: chicha, tremolo-picked eighths on the chord, stabs in the break
        if sec in ("cumbia1", "cumbia2") and i >= 4:
            for k, st in enumerate(range(0, 16, 2)):
                nt = tones[(0, 1, 2, 1, 0, 1, 2, 1)[k]] + (12 if sec == "cumbia2" and i % 2 else 0)
                add("surf", bar, st, 2, nt, (96 if k % 4 == 0 else 78) + rnd.randint(-5, 5), shift=rnd.uniform(-0.005, 0.005), gate=0.9)
        if sec == "quantise" and i >= 8:
            for st in (0, 3, 6, 10):
                add("surf", bar, st, 3, tones[0] + 12, 100, gate=0.9)
        if sec == "outro" and i < 4:
            add("surf", bar, 0, 14, tones[0], 90)

        # ---- fuzz: low hard-clipped stabs that break the cumbia, whole in the fracture
        if sec == "quantise" and i >= 4:
            for st in (0, 3, 6, 10) if i % 2 == 0 else (0, 4, 7, 11, 14):
                add("fuzz", bar, st, 2, root + 12, 108, gate=0.7)
        if sec == "fracture":
            for k, st in enumerate((0, 2, 3, 6, 8, 9, 12, 14, 15)):
                add("fuzz", bar, st, 1, root + 12 + (0, 7, 12)[k % 3], 112, gate=0.6)
        if sec == "cumbia2" and i >= 8:
            add("fuzz", bar, 0, 3, root + 12, 100, gate=0.8)

        # ---- buzz: the diode, a thin line in thirds over the cumbia
        if sec == "cumbia2" and i >= 2:
            for k, st in enumerate((0, 2, 4, 7, 8, 10, 12, 15)):
                add("buzz", bar, st, 2, buzz[(0, 1, 2, 1, 0, 2, 1, 0)[k]], 92 + rnd.randint(-6, 6), gate=0.7)
        if sec == "fracture":
            for k, st in enumerate(range(0, 16, 3)):
                add("buzz", bar, st, 2, buzz[k % 3] + 12, 100, gate=0.6)

        # ---- the ghost pad: long notes on the root and fifth, a slow drift
        if sec in ("intro", "quantise", "talk"):
            add("ghost", bar, 0, 15, root + 12 if sec != "talk" else root + 24, 80 if sec != "intro" else 64, gate=1.0)
        if sec == "outro":
            add("ghost", bar, 0, 15, root + 12, 70, gate=1.0)
        if sec == "fracture":
            add("ghostbreak", bar, 0, 15, root + 24 if i % 2 == 0 else fifth + 24, 100, gate=1.0)
        if sec == "outro" and i >= 4:
            add("ghostbreak", bar, 0, 15, root + 24, 78, gate=1.0)

        # ---- the carrier of the talk box: the root held, in the sections where the voice is
        if sec in ("talk", "fracture") or (sec == "cumbia2" and i >= 12) or (sec == "outro" and i < 4):
            add("talkbox", bar, 0, 16, root + 12, 100, gate=0.98)

    os.makedirs(os.path.join(ART, "midi"), exist_ok=True)
    for part, lst in notes.items():
        if not lst:
            continue
        lst.sort()
        midiw.write(os.path.join(ART, "midi", part + ".mid"), lst, BPM)
        print("%-11s %4d notes" % (part, len(lst)))


# --- the arpeggio and the talk box ----------------------------------------------------------------------------------------------

def read_wav(path):
    w = wave.open(path)
    raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.uint8)
    ch, sw = w.getnchannels(), w.getsampwidth()
    a = raw.reshape(-1, sw)
    v = a[:, 0].astype(np.int64) | (a[:, 1].astype(np.int64) << 8) | ((a[:, 2].astype(np.int64) << 16) if sw == 3 else 0)
    v = np.where(v >= 1 << (8 * sw - 1), v - (1 << (8 * sw)), v) / float(1 << (8 * sw - 1))
    return v.reshape(-1, ch).mean(axis=1), w.getframerate()


def write_wav(path, x, rate=RATE):
    w = wave.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    w.close()


def speech_windows(voice, lengths):
    """Non-overlapping windows of the speech that have the most speech in them, in seconds: one (start, length) for each length asked."""
    block = int(0.25 * RATE)
    env = np.array([np.sqrt((voice[i:i + block] ** 2).mean()) for i in range(0, len(voice) - block, block)])
    active = env > 0.02
    used, out = np.zeros(len(active), dtype=bool), []
    for length in lengths:
        w = int(length / 0.25)
        best, at = -1, 0
        for s in range(0, len(active) - w):
            if used[s:s + w].any():
                continue
            score = active[s:s + w].mean()
            if score > best:
                best, at = score, s
        used[at:at + w] = True
        out.append((at * 0.25, length))
    return out


def window_mask(sections, seconds, fade=0.08):
    """A gain curve, 1 inside the named (section, first bar, bars) windows and 0 outside, with short fades."""
    m = np.zeros(int(seconds * RATE))
    for name, first, bars in sections:
        s = (first_bar(name) + first) * 4 * BEAT
        e = s + bars * 4 * BEAT
        m[int(s * RATE):int(e * RATE)] = 1.0
    k = max(1, int(fade * RATE))
    return np.convolve(m, np.ones(k) / k, mode="same")


def render_tool():
    for p in ("build-release/valis_render_artefacts/Release/valis_render", "build/valis_render_artefacts/Debug/valis_render"):
        if os.path.exists(os.path.join(VALIS, p)):
            return os.path.join(VALIS, p)
    sys.exit("valis_render is not built")


def recorded():
    tool = render_tool()
    os.makedirs(os.path.join(ART, "wavs"), exist_ok=True)
    tmp = os.path.join(ART, "wavs", "_work")
    os.makedirs(tmp, exist_ok=True)

    # the arpeggio: the circuit runs from the transport, so it is rendered whole and then gated to the sections where it plays
    raw = os.path.join(tmp, "arp-raw.wav")
    subprocess.run([tool, os.path.join(ART, "circuits", "arp.ttl"), "--seconds", str(SONG_SECONDS), "--rolling", "--tempo", str(BPM), "-o", raw],
                   cwd=VALIS, check=True, capture_output=True)
    x, rate = read_wav(raw)
    mask = window_mask([("quantise", 0, 16), ("fracture", 0, 8), ("cumbia2", 8, 8), ("outro", 0, 2)], len(x) / rate)
    write_wav(os.path.join(ART, "wavs", "arp.wav"), x * mask[:len(x)], rate)
    print("arp: %.1f s" % (len(x) / rate))

    # the talk box: the speech of "All Fall Down" placed in the sections where the carrier is played, then shaped by the circuit
    voice, vrate = read_wav(os.path.expanduser("~/github/valis-artifacts/artifacts/all-fall-down/wavs/voice.wav"))
    assert vrate == RATE
    plan = [("talk", 0, 16), ("fracture", 0, 8), ("cumbia2", 12, 4), ("outro", 0, 4)]
    windows = speech_windows(voice, [bars * 4 * BEAT for _, _, bars in plan])
    track = np.zeros(int(SONG_SECONDS * RATE))
    for (name, first, bars), (start, length) in zip(plan, windows):
        seg = voice[int(start * RATE):int((start + length) * RATE)].copy()
        seg *= 0.12 / max(np.sqrt((seg ** 2).mean()), 1e-4)                   # an even level into the circuit
        at = int((first_bar(name) + first) * 4 * BEAT * RATE)
        track[at:at + len(seg)] += seg
        print("voice: %6.1f s of speech into %s" % (start, name))
    write_wav(os.path.join(tmp, "voice-in.wav"), track)
    out = os.path.join(ART, "wavs", "talkbox.wav")
    r = subprocess.run([tool, os.path.join(ART, "circuits", "talkbox.ttl"), "-i", os.path.join(tmp, "voice-in.wav"),
                        "--midi", os.path.join(ART, "midi", "talkbox.mid"), "--tempo", str(BPM), "--rolling", "-o", out],
                       cwd=VALIS, capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
    shutil.rmtree(tmp)


# --- main -----------------------------------------------------------------------------------------------------------------------

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=") for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    todo = args or ["circuits", "song", "score", "recorded", "render", "mix"]
    os.makedirs(ART, exist_ok=True)
    if "circuits" in todo:
        make_circuits()
    if "song" in todo:
        song_ttl()
    if "score" in todo:
        score()
    if "recorded" in todo:
        recorded()
    song = None
    if "render" in todo or "mix" in todo:
        song = songlib.load(os.path.join(ART, "song.ttl"))
    if "render" in todo:
        songlib.render(song)
    if "mix" in todo:
        songlib.mix(song, opts.get("version", "v1"), arc=True)


if __name__ == "__main__":
    main()
