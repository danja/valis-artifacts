# scripts/big-pickle/make.py
#
# "Big Pickle": driving techno at 138 bpm in A minor, 140 bars (about 4:03), for the year 2000's idea
# of the future. A machine wakes to a held chord and a slow bleep arpeggio that opens into sixteenths,
# running like data on a phone line, supersaw chord stabs open over bubble-plastic chrome, and a rolling
# bass drives three drops.
# The material is new. The palette is the one the year 2000 imagined: a bright digital arpeggio, wide
# detuned saws, a hard four-to-the-floor kick and long reverb tails.
#
#   python3 make.py            write circuits/, score.ttl and song.ttl under artifacts/big-pickle/
#
# Then, with the Valis tools built (`cmake --build build-release --target valis_song valis_render valis_shot`):
#   valis-song score  artifacts/big-pickle/song.ttl
#   valis-song render artifacts/big-pickle/song.ttl
#   valis-song stems  artifacts/big-pickle/song.ttl
#   valis-song mix    artifacts/big-pickle/song.ttl --version v1 --arc
#
# The arrangement is a table (SECTIONS and PLAN), so a changed plan is a changed table. The circuits
# are generated here too, because a Turtle file with one block per connection is long to write by hand.
import os, shutil

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "big-pickle"))

TEMPO = 138
STEPS = 16
TITLE = "Big Pickle"

SECTIONS = [  # name, bars, section level dB
    ("intro",  16, -5.0),
    ("build1",  8, -2.0),
    ("drop1",  24,  0.0),
    ("break1", 16, -2.0),
    ("build2",  8, -2.0),
    ("drop2",  24,  1.0),
    ("break2",  8,  2.0),
    ("build3",  8, -2.0),
    ("drop3",  16,  2.0),
    ("outro",  12, -4.0),
]
BARS = dict((n, b) for n, b, _ in SECTIONS)

# Parts: name, circuit, level dB (playing rms), pan, highpass Hz.
PARTS = [
    ("kick",  "y2k-kick.ttl",  -14,  0.00,  30),
    ("kit",   "909.ttl",       -24.5, 0.00, 130),
    ("bass",  "y2k-bass.ttl",  -20,  0.00,  30),
    ("stab",  "y2k-stab.ttl",  -22.5, 0.10, 220),
    ("pad",   "y2k-pad.ttl",   -28.5, -0.10, 180),
    ("arp",   "y2k-bleep.ttl", -26,  0.25, 500),
    ("lead",  "y2k-lead.ttl",  -22,  0.05, 260),
    ("riser", "y2k-riser.ttl", -28,  0.00, 300),
]

# Returns: name, source, circuit, level dB, pan, highpass Hz.
RETURNS = [
    ("stab-verb", "stab", "reverb-return.ttl", -28.5,  0.55, 350),
    ("pad-verb",  "pad",  "reverb-return.ttl", -28.5, -0.55, 250),
    ("arp-echo",  "arp",  "dub-delay.ttl",     -28,    0.60, 600),
]

# -- the plan: part -> section -> list of (pattern, first bar, last bar) ------------------------------
PLAN = {}


def play(part, section, pattern, first=1, last=None):
    PLAN.setdefault(part, {}).setdefault(section, []).append((pattern, first, last or BARS[section]))


def lay(part, section, groove, fills=(), first=1, last=None):
    """A groove over the section with one-bar replacements (fills) at the given bars."""
    last = last or BARS[section]
    marks = sorted(b for b, _ in fills)
    where = dict(fills)
    at = first
    for b in marks:
        if b > last:
            break
        if b > at:
            play(part, section, groove, at, b - 1)
        play(part, section, where[b], b, b)
        at = b + 1
    if at <= last:
        play(part, section, groove, at, last)


# kick: four to the floor, a boom on each drop, a fill where the section turns
play("kick", "intro", "kick4", 9, 15); play("kick", "intro", "kick-gap", 16, 16)
lay("kick", "build1", "kick4", [(7, "kick-fill"), (8, "kick-gap")])
play("kick", "drop1", "boom", 1, 1)
lay("kick", "drop1", "kick4", [(8, "kick-fill"), (16, "kick-fill"), (24, "kick-roll")], first=2)
lay("kick", "build2", "kick4", [(7, "kick-fill"), (8, "kick-gap")])
play("kick", "drop2", "boom", 1, 1)
lay("kick", "drop2", "kick4", [(8, "kick-fill"), (16, "kick-fill"), (24, "kick-roll")], first=2)
lay("kick", "build3", "kick4", [(7, "kick-fill"), (8, "kick-gap")])
play("kick", "drop3", "boom", 1, 1)
lay("kick", "drop3", "kick4", [(8, "kick-fill"), (16, "kick-roll")], first=2)
play("kick", "outro", "kick4", 1, 6); play("kick", "outro", "kick-gap", 7, 7)

# the 909: offbeat hats, clap on two and four, snare rolls where a drop is coming
play("kit", "intro", "rim", 1, 8)
play("kit", "intro", "hats", 9, 16)
play("kit", "build1", "kit-groove", 1, 4)
play("kit", "build1", "hats16", 5, 6)
play("kit", "build1", "roll8", 7, 7)
play("kit", "build1", "roll16-gap", 8, 8)
play("kit", "drop1", "kit-groove", 1, 24)
lay("kit", "drop1", "kit-groove", [(8, "tomfill"), (16, "tomfill"), (24, "roll16")])
play("kit", "break1", "rim", 1, 8)
play("kit", "break1", "hats", 9, 14)
play("kit", "break1", "roll8", 15, 15)
play("kit", "break1", "roll16-gap", 16, 16)
play("kit", "build2", "kit-groove", 1, 4)
play("kit", "build2", "hats16", 5, 6)
play("kit", "build2", "roll8", 7, 7)
play("kit", "build2", "roll16-gap", 8, 8)
play("kit", "drop2", "kit-groove", 1, 24)
lay("kit", "drop2", "kit-groove", [(8, "tomfill"), (16, "tomfill"), (24, "roll16")])
play("kit", "break2", "rim", 1, 4)
play("kit", "break2", "roll8", 7, 7)
play("kit", "break2", "roll16-gap", 8, 8)
play("kit", "build3", "kit-groove", 1, 4)
play("kit", "build3", "hats16", 5, 6)
play("kit", "build3", "roll8", 7, 7)
play("kit", "build3", "roll16-gap", 8, 8)
play("kit", "drop3", "kit-groove", 1, 16)
lay("kit", "drop3", "kit-groove", [(8, "tomfill"), (16, "roll16")])
play("kit", "outro", "kit-groove", 1, 4)
play("kit", "outro", "hats", 5, 8)
play("kit", "outro", "rim", 9, 12)

# the bass: offbeat eighths, then rolling sixteenths in the drops
play("bass", "intro", "bass-off", 13, 16)
play("bass", "build1", "bass-off", 1, 6)
play("bass", "drop1", "bass-off", 1, 8)
play("bass", "drop1", "bass-roll", 9, 24)
play("bass", "break1", "bass-break", 1, 8)
play("bass", "break1", "bass-off", 9, 16)
play("bass", "build2", "bass-off", 1, 6)
play("bass", "drop2", "bass-roll", 1, 24)
play("bass", "build3", "bass-off", 1, 6)
play("bass", "drop3", "bass-roll", 1, 16)
play("bass", "outro", "bass-off", 1, 6)

# the stab: a hint in the build, then the chord on the offbeat through each drop
play("stab", "build1", "stab-off", 5, 8)
play("stab", "drop1", "stab-off", 1, 24)
play("stab", "break1", "stab-long", 1, 16)
play("stab", "build2", "stab-off", 5, 8)
play("stab", "drop2", "stab-off", 1, 24)
play("stab", "break2", "stab-long", 1, 8)
play("stab", "build3", "stab-off", 5, 8)
play("stab", "drop3", "stab-hi", 1, 16)
play("stab", "outro", "stab-long", 1, 8)

# the pad: the bed under everything
play("pad", "intro", "pad-hold", 1, 16)
play("pad", "build1", "pad-hold", 1, 8)
play("pad", "drop1", "pad-hold", 1, 24)
play("pad", "break1", "pad-hold", 1, 16)
play("pad", "build2", "pad-hold", 1, 8)
play("pad", "drop2", "pad-hold", 1, 24)
play("pad", "break2", "pad-hold", 1, 8)
play("pad", "build3", "pad-hold", 1, 8)
play("pad", "drop3", "pad-hold", 1, 16)
play("pad", "outro", "pad-hold", 1, 12)

# the bleep arpeggio: the data motif
play("arp", "intro", "arp-slow", 1, 4)
play("arp", "intro", "arp-16", 5, 16)
play("arp", "build1", "arp-16", 1, 8)
play("arp", "drop1", "arp-16", 1, 24)
play("arp", "break1", "arp-slow", 1, 16)
play("arp", "build2", "arp-16", 1, 8)
play("arp", "drop2", "arp-16", 1, 24)
play("arp", "break2", "arp-slow", 1, 8)
play("arp", "build3", "arp-16", 1, 8)
play("arp", "drop3", "arp-16", 1, 16)
play("arp", "outro", "arp-slow", 1, 8)

# the lead: the hook arrives in the first break, then opens the second and third drops
play("lead", "build1", "hook", 5, 8)
play("lead", "break1", "break-hook", 1, 16)
play("lead", "build2", "hook", 5, 8)
play("lead", "drop2", "hook", 1, 24)
play("lead", "build3", "hook", 5, 8)
play("lead", "drop3", "hook-hi", 1, 16)
play("lead", "outro", "hook", 1, 8)

# risers: a held note whose envelope opens over four bars
play("riser", "build1", "riser4", 5, 8)
play("riser", "break1", "riser4", 13, 16)
play("riser", "break2", "riser4", 5, 8)
play("riser", "build3", "riser4", 5, 8)

# -- the harmony ---------------------------------------------------------------------------------------
PROGRESSION = "Am F C G"
BREAK_PROGRESSION = "Dm E F G"
SECTION_PROGRESSION = {"break1": BREAK_PROGRESSION, "break2": BREAK_PROGRESSION}

CHORDS = [  # name, bass root, bass pickup, treble tones (lowest first)
    ("Am", 33, 40, "60 64 69"),
    ("F",  29, 36, "60 65 69"),
    ("C",  36, 43, "60 64 67"),
    ("G",  31, 38, "59 62 67"),
    ("Dm", 38, 45, "62 65 69"),
    ("E",  28, 35, "59 64 68"),
]

# The hook: (step from the start of the four bars, MIDI note, length in steps). It rises to the
# sixth and the ninth and falls back, which is the bright, open shape the year 2000 liked.
HOOK = [
    # over Am
    (0, 76, 3), (3, 81, 5), (8, 79, 3), (11, 76, 1), (12, 74, 4),
    # over F
    (16, 72, 3), (19, 77, 5), (24, 76, 3), (27, 72, 1), (28, 69, 4),
    # over C
    (32, 79, 3), (35, 84, 5), (40, 83, 3), (43, 79, 1), (44, 76, 4),
    # over G
    (48, 74, 3), (51, 79, 3), (54, 83, 4), (58, 81, 2), (60, 79, 4),
]

# The break hook, over Dm Dm E E F F G G: the same shape with the tension of the minor dominant.
BREAK_HOOK = [
    # over Dm
    (0, 74, 3), (3, 81, 5), (8, 77, 3), (11, 74, 1), (12, 72, 4),
    # over E
    (16, 71, 3), (19, 76, 5), (24, 80, 3), (27, 76, 1), (28, 71, 4),
    # over F
    (32, 72, 3), (35, 77, 5), (40, 76, 3), (43, 72, 1), (44, 69, 4),
    # over G
    (48, 74, 3), (51, 79, 3), (54, 83, 4), (58, 81, 2), (60, 79, 4),
]


def grid(spec, bars=1):
    """A step string from a short spec: the characters are the steps, '|' is only for reading."""
    s = spec.replace(" ", "").replace("|", "")
    assert len(s) == bars * STEPS, (spec, len(s), bars * STEPS)
    return spec


def lane(steps, key=None, voice=None, vel=None, accent=None, length=None, gate=None, octave=None, transpose=None):
    parts = []
    if key is not None:
        parts.append("val:key %d" % key)
    if voice is not None:
        parts.append('val:voice "%s"' % voice)
    parts.append('val:steps "%s"' % steps)
    if vel is not None:
        parts.append("val:velocity %d" % vel)
    if accent is not None:
        parts.append("val:accent %d" % accent)
    if length is not None:
        parts.append("val:length %g" % length)
    if gate is not None:
        parts.append("val:gate %g" % gate)
    if octave is not None:
        parts.append("val:octave %d" % octave)
    if transpose is not None:
        parts.append("val:transpose %d" % transpose)
    return "[ " + " ; ".join(parts) + " ]"


def hook_lanes(notes, transpose=0):
    by = {}
    for step, note, length in notes:
        by.setdefault((note, length), []).append(step)
    lanes = []
    for (note, length), steps in sorted(by.items()):
        s = ["."] * (4 * STEPS)
        for st in steps:
            s[st] = "x"
        lanes.append(lane("".join(s), key=note, vel=100, length=length, gate=0.85,
                          transpose=transpose if transpose else None))
    return lanes


def patterns():
    """name -> (bars, lanes)"""
    P = {}
    # kick: X is an accent
    P["kick4"]     = (1, [lane(grid("X...|X...|X...|X..."), key=36, vel=112, accent=10)])
    P["kick-gap"]  = (1, [lane(grid("X...|X...|X...|...."), key=36, vel=112, accent=10)])
    P["kick-fill"] = (1, [lane(grid("X...|X...|X...|X.X."), key=36, vel=108, accent=16)])
    P["kick-roll"] = (1, [lane(grid("X...|X...|XxXx|XxXx"), key=36, vel=104, accent=22)])
    P["boom"]      = (1, [lane(grid("X...|....|....|...."), key=35, vel=118, length=14, gate=1.0)])
    # the 909: closed hats on the offbeat eighths, open hat on the and of each beat
    P["kit-groove"] = (1, [lane(grid(".x.x|.x.x|.x.x|.x.x"), key=42, vel=74),
                           lane(grid("..x.|..x.|..x.|..x."), key=46, vel=84),
                           lane(grid("....|X...|....|X..."), key=39, vel=96, accent=12)])
    P["hats"]       = (1, [lane(grid("x.x.|x.x.|x.x.|x.x."), key=42, vel=72)])
    P["hats16"]     = (1, [lane(grid("xxxx|xxxx|xxxx|xxxx"), key=42, vel=64)])
    P["rim"]        = (1, [lane(grid("....|..x.|....|..x."), key=37, vel=80)])
    P["roll8"]      = (1, [lane(grid("x.x.|x.x.|x.x.|x.x."), key=38, vel=90)])
    P["roll16"]     = (1, [lane(grid("xxxx|xxxx|xxxx|xxxx"), key=38, vel=108)])
    P["roll16-gap"] = (1, [lane(grid("xxxx|xxxx|xxxx|...."), key=38, vel=110)])
    P["tomfill"]    = (1, [lane(grid("....|....|x.x.|...."), key=50, vel=100),
                           lane(grid("....|....|....|x.x."), key=41, vel=104),
                           lane(grid("....|....|....|..x."), key=38, vel=98)])
    # the bass
    P["bass-off"]   = (1, [lane(grid("..x.|..x.|..x.|..x."), voice="root", vel=104, length=2, gate=0.9)])
    P["bass-roll"]  = (1, [lane(grid("..xx|..xx|..xx|..xx"), voice="root", vel=102, length=1, gate=0.8)])
    P["bass-break"] = (1, [lane(grid("x...|....|....|...."), voice="root", vel=96, length=12, gate=0.95)])
    # the chord stab
    P["stab-off"]   = (1, [lane(grid("....|..x.|....|..x."), voice="chord", vel=96, length=2, gate=0.45)])
    P["stab-hi"]    = (1, [lane(grid("....|..x.|....|..x."), voice="chord", vel=98, length=2, gate=0.45, octave=1)])
    P["stab-long"]  = (1, [lane(grid("x...|....|....|...."), voice="chord", vel=86, length=16, gate=0.98)])
    P["pad-hold"]   = (1, [lane(grid("x...|....|....|...."), voice="chord", vel=80, length=16, gate=1.0)])
    # the bleep arpeggio: root, third, fifth and octave, one note at a time
    P["arp-16"]     = (1, [lane(grid("x...|x...|x...|x..."), voice="root", octave=1, vel=92, length=1, gate=0.8),
                           lane(grid(".x..|.x..|.x..|.x.."), voice="low", octave=1, vel=88, length=1, gate=0.8),
                           lane(grid("..x.|..x.|..x.|..x."), voice="top", octave=-1, vel=90, length=1, gate=0.8),
                           lane(grid("...x|...x|...x|...x"), voice="low", octave=2, vel=86, length=1, gate=0.8)])
    P["arp-slow"]   = (1, [lane(grid("x...|x...|x...|x..."), voice="root", octave=1, vel=90, length=2, gate=0.8),
                           lane(grid("..x.|..x.|..x.|..x."), voice="top", octave=-1, vel=86, length=2, gate=0.8)])
    # the tunes
    P["hook"]       = (4, hook_lanes(HOOK))
    P["hook-hi"]    = (4, hook_lanes(HOOK, 12))
    P["break-hook"] = (4, hook_lanes(BREAK_HOOK))
    # a held note for a riser: four bars at 138 bpm is 6.96 s, and the riser opens over 6.4 s
    P["riser4"]     = (4, [lane("x" + "." * (4 * STEPS - 1), key=60, vel=100, length=62, gate=1.0)])
    return P


def turtle_score():
    P = patterns()
    used = sorted({p for part in PLAN.values() for sec in part.values() for p, _, _ in sec})
    out = []
    out.append("# score.ttl\n#\n# \"Big Pickle\": generated by scripts/big-pickle/make.py from its table. Play it with\n"
               "# `valis-song score song.ttl`. The kick, 909, bass, stab, pad, bleep arp, lead and riser are all here.\n")
    out.append("@prefix val: <http://purl.org/stuff/valis/> .\n@prefix :    <urn:valis-artifacts:big-pickle#> .\n")
    play_ids = []
    plays = []
    for part, secs in PLAN.items():
        for sec, items in secs.items():
            for k, (pat, a, b) in enumerate(items):
                pid = "%s-%s-%d" % (part, sec, k + 1)
                play_ids.append(":" + pid)
                prog = SECTION_PROGRESSION.get(sec)
                extra = ' ; val:progression "%s"' % prog if prog else ""
                plays.append(":%s a val:Play ; val:section \"%s\" ; val:part \"%s\" ; val:pattern :%s ; val:fromBar %d ; val:toBar %d%s ."
                             % (pid, sec, part, pat.replace("-", "_"), a, b, extra))
    chord_ids = [":" + c[0] for c in CHORDS]
    feel_ids = [":kick-feel", ":kit-feel", ":bass-feel", ":stab-feel", ":arp-feel", ":lead-feel"]
    out.append(":score a val:Score ; val:seed 2000 ;\n    val:progression \"%s\" ;\n    val:hasChord %s ;\n    val:hasPattern %s ;\n    val:hasFeel %s ;\n    val:hasPlay\n        %s .\n"
               % (PROGRESSION, " , ".join(chord_ids), " , ".join(":" + p.replace("-", "_") for p in used),
                  " , ".join(feel_ids), " ,\n        ".join(play_ids)))
    for name, root, pickup, tones in CHORDS:
        out.append(":%s a val:Chord ; val:root %d ; val:pickup %d ; val:tones \"%s\" ." % (name, root, pickup, tones))
    out.append("")
    for p in used:
        bars, lanes = P[p]
        out.append(":%s a val:Pattern ; val:bars %d ; val:hasLane\n    %s ." % (p.replace("-", "_"), bars, " ,\n    ".join(lanes)))
    out.append("")
    out.append(':kick-feel a val:Feel ; val:part "kick" ; val:timing 0.4 ; val:velocity 2 .')
    out.append(':kit-feel  a val:Feel ; val:part "kit"  ; val:timing 1.1 ; val:velocity 5 .')
    out.append(':bass-feel a val:Feel ; val:part "bass" ; val:timing 0.6 ; val:velocity 3 .')
    out.append(':stab-feel a val:Feel ; val:part "stab" ; val:timing 0.9 ; val:velocity 4 .')
    out.append(':arp-feel  a val:Feel ; val:part "arp"  ; val:timing 0.8 ; val:velocity 4 .')
    out.append(':lead-feel a val:Feel ; val:part "lead" ; val:timing 1.8 ; val:velocity 5 .')
    out.append("")
    out.extend(plays)
    return "\n".join(out) + "\n"


def turtle_song():
    out = []
    out.append("# song.ttl\n#\n# \"Big Pickle\": the layout and the mix as data. Generated by scripts/big-pickle/make.py;\n"
               "# the notes are in score.ttl, played by the circuits in circuits/.\n")
    out.append("@prefix val:  <http://purl.org/stuff/valis/> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix :     <urn:valis-artifacts:big-pickle#> .\n")
    out.append(":song a val:Song ;\n    val:title \"%s\" ;\n    val:tempo %d ;\n    val:score \"score.ttl\" ;\n    val:loudness -10 ;\n"
               "    val:tailSeconds 10 ;\n    val:fadeSeconds 6 ;\n    val:roomAmount 0.06 ;\n    val:roomDecay 0.35 ;\n"
               "    val:roomLowpass 5000 ;\n    val:drive 1.5 ;\n"
               "    val:hasSection %s ;\n    val:hasPart %s ;\n    val:hasReturn %s ." %
               (TITLE, TEMPO, " , ".join(":" + n for n, _, _ in SECTIONS), " , ".join(":" + p[0] for p in PARTS),
                " , ".join(":" + r[0] for r in RETURNS)))
    out.append("")
    for i, (n, bars, level) in enumerate(SECTIONS, 1):
        out.append(":%s a val:Section ; val:index %d ; val:bars %d ; val:level %g ." % (n, i, bars, level))
    out.append("")
    for i, (n, circuit, level, pan, hp) in enumerate(PARTS, 1):
        out.append(":%s a val:Part ; val:index %d ; val:circuit \"circuits/%s\" ; val:level %g ; val:pan %g ; val:highpass %d ." %
                   (n, i, circuit, level, pan, hp))
    out.append("")
    for i, (n, source, circuit, level, pan, hp) in enumerate(RETURNS, 1):
        out.append(":%s a val:Return ; val:index %d ; val:source :%s ; val:circuit \"circuits/%s\" ;\n"
                   "    val:level %g ; val:pan %g ; val:highpass %d ." % (n, i, source, circuit, level, pan, hp))
    return "\n".join(out) + "\n"


# -- circuits -------------------------------------------------------------------------------------------
HEADER = """@prefix val:   <http://purl.org/stuff/valis/> .
@prefix lv2:   <http://lv2plug.in/ns/lv2core#> .
@prefix units: <http://lv2plug.in/ns/extensions/units#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix trn:   <http://purl.org/stuff/transmissions/> .
@prefix :      <urn:valis-artifacts:big-pickle:%s#> .
"""


class Circuit:
    def __init__(self, ident, label, comment):
        self.ident, self.label, self.comment = ident, label, comment
        self.elements = []   # (name, class, props)
        self.arcs = []       # (kind, from, fromport, to, toport)

    def add(self, name, cls, **props):
        self.elements.append((name, cls, props))
        return name

    def audio(self, a, aport, b, bport):
        self.arcs.append(("Arc", a, aport, b, bport))

    def control(self, a, aport, b, bport):
        self.arcs.append(("ControlArc", a, aport, b, bport))

    def text(self):
        names = [n for n, _, _ in self.elements]
        ids = []
        blocks = []
        for kind, a, ap, b, bp in self.arcs:
            aid = "a_%s_%s__%s_%s" % (a, ap, b, bp)
            ids.append(":" + aid)
            blocks.append(":%s a val:%s ;\n    val:from [ val:node :%s ; val:port \"%s\" ] ;\n    val:to   [ val:node :%s ; val:port \"%s\" ] ." % (aid, kind, a, ap, b, bp))
        head = "# " + "\n# ".join(self.comment.strip().splitlines()) + "\n\n" + HEADER % self.ident
        head += "\n:%s a val:Circuit , trn:PluginProfile ;\n    trn:role trn:AudioInstrument ;\n    trn:accepts trn:Midi ;\n    trn:produces trn:Audio ;\n    rdfs:label \"%s\" ;\n    val:element %s ;\n    val:arc %s .\n" % (
            self.ident, self.label, " , ".join(":" + n for n in names), " ,\n        ".join(ids))
        body = []
        for name, cls, props in self.elements:
            if props:
                body.append(":%s a val:%s ;\n    %s ." % (name, cls, " ;\n    ".join("val:%s %s" % (k, v) for k, v in props.items())))
            else:
                body.append(":%s a val:%s ." % (name, cls))
        return head + "\n" + "\n\n".join(body) + "\n\n" + "\n\n".join(blocks) + "\n"


def y2k_kick():
    c = Circuit("y2kkick", "Y2K kick",
                "y2k-kick.ttl\n\nA driving techno kick, tuned to A1 (55 Hz). A sine falls from 190 Hz to the note in about 45 ms,\n"
                "its amplitude falls over 240 ms, and a short high noise click sits on the attack. Key 36 is the kick; key 35 is a\n"
                "long sub boom for the first beat of a drop.");
    c.add("kGate", "NoteGate", note=36)
    c.add("kPitchEnv", "Envelope", attack=0.2, decay=45.0, sustain=0.0, release=5.0)
    c.add("kPitch", "Scale", min=55.0, max=190.0)
    c.add("kOsc", "Oscillator", shape=0)
    c.add("kAmpEnv", "Envelope", attack=0.5, decay=240.0, sustain=0.0, release=30.0)
    c.add("kVca", "VCA")
    c.add("kDrive", "Tanh", gain=3.5)
    c.add("kClip", "HardClip", threshold=0.9)
    c.add("kLevel", "Gain", gain=-3.0)
    c.add("clickNoise", "Noise", colour=0.0)
    c.add("clickHp", "Biquad", mode=4, frequency=3200.0, q=0.7)
    c.add("clickEnv", "Envelope", attack=0.1, decay=6.0, sustain=0.0, release=2.0)
    c.add("clickVca", "VCA")
    c.add("clickLevel", "Gain", gain=-15.0)
    c.add("bGate", "NoteGate", note=35)
    c.add("bPitchEnv", "Envelope", attack=0.5, decay=350.0, sustain=0.0, release=20.0)
    c.add("bPitch", "Scale", min=41.0, max=115.0)
    c.add("bOsc", "Oscillator", shape=0)
    c.add("bAmpEnv", "Envelope", attack=4.0, decay=2200.0, sustain=0.0, release=500.0)
    c.add("bVca", "VCA")
    c.add("bLevel", "Gain", gain=-2.0)
    c.add("mix", "Mixer")
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("kGate", "gate", "kPitchEnv", "gate")
    c.control("kGate", "gate", "kAmpEnv", "gate")
    c.control("kGate", "gate", "clickEnv", "gate")
    c.control("kPitchEnv", "out", "kPitch", "in")
    c.control("kPitch", "out", "kOsc", "frequency")
    c.audio("kOsc", "out", "kVca", "in")
    c.control("kAmpEnv", "out", "kVca", "cv")
    c.audio("kVca", "out", "kDrive", "in")
    c.audio("kDrive", "out", "kClip", "in")
    c.audio("kClip", "out", "kLevel", "in")
    c.audio("kLevel", "out", "mix", "in")
    c.audio("clickNoise", "out", "clickHp", "in")
    c.audio("clickHp", "out", "clickVca", "in")
    c.control("clickEnv", "out", "clickVca", "cv")
    c.audio("clickVca", "out", "clickLevel", "in")
    c.audio("clickLevel", "out", "mix", "in")
    c.control("bGate", "gate", "bPitchEnv", "gate")
    c.control("bGate", "gate", "bAmpEnv", "gate")
    c.control("bPitchEnv", "out", "bPitch", "in")
    c.control("bPitch", "out", "bOsc", "frequency")
    c.audio("bOsc", "out", "bVca", "in")
    c.control("bAmpEnv", "out", "bVca", "cv")
    c.audio("bVca", "out", "bLevel", "in")
    c.audio("bLevel", "out", "mix", "in")
    c.audio("mix", "out", "limit", "in")
    c.audio("limit", "out", "out", "in")
    return c


def y2k_bass():
    c = Circuit("y2kbass", "Y2K rolling bass",
                "y2k-bass.ttl\n\nA rolling techno bass. A saw at the played pitch and a square an octave below go through a\n"
                "resonant 24 dB low-pass that an envelope opens on every note, then a gentle tanh and a DC blocker. It is\n"
                "monophonic and plays from E1 to E3. The short envelope leaves a gap between sixteenths, so the line pumps\n"
                "instead of blurring.");
    c.add("pitch", "MidiPitch")
    c.add("sub", "ControlMultiply", b=0.5)
    c.add("osc1", "Oscillator", shape=1)
    c.add("osc2", "Oscillator", shape=2)
    c.add("l1", "Gain", gain=-4.0)
    c.add("l2", "Gain", gain=-8.0)
    c.add("mix", "Mixer")
    c.add("filtEnv", "Envelope", attack=1.0, decay=160.0, sustain=0.18, release=80.0)
    c.add("filtScale", "Scale", min=140.0, max=2600.0)
    c.add("vcf", "Ladder", resonance=0.28, drive=1.5)
    c.add("ampEnv", "Envelope", attack=1.0, decay=140.0, sustain=0.82, release=70.0)
    c.add("vca", "VCA")
    c.add("drive", "Tanh", gain=2.0)
    c.add("dc", "OnePole", mode=1, cutoff=25.0)
    c.add("trim", "Gain", gain=-7.0)
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("pitch", "out", "osc1", "frequency")
    c.control("pitch", "out", "sub", "a")
    c.control("sub", "out", "osc2", "frequency")
    c.audio("osc1", "out", "l1", "in")
    c.audio("osc2", "out", "l2", "in")
    c.audio("l1", "out", "mix", "in")
    c.audio("l2", "out", "mix", "in")
    c.audio("mix", "out", "vcf", "in")
    c.control("filtEnv", "out", "filtScale", "in")
    c.control("filtScale", "out", "vcf", "cutoff")
    c.audio("vcf", "out", "vca", "in")
    c.control("ampEnv", "out", "vca", "cv")
    c.audio("vca", "out", "drive", "in")
    c.audio("drive", "out", "dc", "in")
    c.audio("dc", "out", "trim", "in")
    c.audio("trim", "out", "limit", "in")
    c.audio("limit", "out", "out", "in")
    return c


def y2k_lead():
    c = Circuit("y2klead", "Y2K lead",
                "y2k-lead.ttl\n\nA wide lead in the year 2000 manner: five saws, four of them slightly detuned and one an octave\n"
                "up, into a resonant low-pass opened by an envelope, a chorus and a short portamento. The detune is the width;\n"
                "the filter envelope gives each phrase a bright edge.");
    c.add("pitch", "MidiPitch")
    c.add("glide", "Slew", rise=8.0, fall=8.0)
    ratios = [("r1", 1.0), ("r2", 1.006), ("r3", 0.994), ("r4", 1.012), ("r5", 2.0)]
    for name, ratio in ratios:
        if ratio != 1.0:
            c.add(name, "ControlMultiply", b=ratio)
    for i in (1, 2, 3, 4, 5):
        c.add("saw%d" % i, "Oscillator", shape=1)
    for i, g in zip((1, 2, 3, 4, 5), (-4.0, -7.0, -7.0, -9.0, -12.0)):
        c.add("l%d" % i, "Gain", gain=g)
    c.add("mix", "Mixer")
    c.add("filtEnv", "Envelope", attack=4.0, decay=420.0, sustain=0.45, release=220.0)
    c.add("cutoff", "Scale", min=1100.0, max=8500.0)
    c.add("vcf", "Ladder", resonance=0.18, drive=1.3)
    c.add("ampEnv", "Envelope", attack=6.0, decay=320.0, sustain=0.8, release=260.0)
    c.add("vca", "VCA")
    c.add("chorus", "Chorus", rate=0.55, depth=2.5, mix=0.35)
    c.add("trim", "Gain", gain=-10.0)
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("pitch", "out", "glide", "in")
    for i, (name, ratio) in enumerate(ratios, 1):
        if ratio != 1.0:
            c.control("glide", "out", name, "a")
            c.control(name, "out", "saw%d" % i, "frequency")
        else:
            c.control("glide", "out", "saw%d" % i, "frequency")
    for i in (1, 2, 3, 4, 5):
        c.audio("saw%d" % i, "out", "l%d" % i, "in")
        c.audio("l%d" % i, "out", "mix", "in")
    c.control("filtEnv", "out", "cutoff", "in")
    c.control("cutoff", "out", "vcf", "cutoff")
    c.audio("mix", "out", "vcf", "in")
    c.audio("vcf", "out", "vca", "in")
    c.control("ampEnv", "out", "vca", "cv")
    c.audio("vca", "out", "chorus", "in")
    c.audio("chorus", "out", "trim", "in")
    c.audio("trim", "out", "limit", "in")
    c.audio("limit", "out", "out", "in")
    return c


def y2k_bleep():
    c = Circuit("y2kbleep", "Y2K bleep arpeggio",
                "y2k-bleep.ttl\n\nA digital bleep: a square at the played pitch and a sine an octave above, mixed and held at\n"
                "9 bits with a little sample-rate reduction, so the line has the grain of a 2000 game console. A short\n"
                "envelope and a high-pass keep every note a separate event. Monophonic.");
    c.add("pitch", "MidiPitch")
    c.add("up", "ControlMultiply", b=2.0)
    c.add("oscA", "Oscillator", shape=2)
    c.add("oscB", "Oscillator", shape=0)
    c.add("lA", "Gain", gain=-5.0)
    c.add("lB", "Gain", gain=-14.0)
    c.add("mix", "Mixer")
    c.add("redux", "Redux", bits=9.0, downsample=3.0, jitter=0.15)
    c.add("ampEnv", "Envelope", attack=0.5, decay=100.0, sustain=0.0, release=40.0)
    c.add("vca", "VCA")
    c.add("hp", "OnePole", mode=1, cutoff=500.0)
    c.add("trim", "Gain", gain=-8.0)
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("pitch", "out", "oscA", "frequency")
    c.control("pitch", "out", "up", "a")
    c.control("up", "out", "oscB", "frequency")
    c.audio("oscA", "out", "lA", "in")
    c.audio("oscB", "out", "lB", "in")
    c.audio("lA", "out", "mix", "in")
    c.audio("lB", "out", "mix", "in")
    c.audio("mix", "out", "redux", "in")
    c.audio("redux", "out", "vca", "in")
    c.control("ampEnv", "out", "vca", "cv")
    c.audio("vca", "out", "hp", "in")
    c.audio("hp", "out", "trim", "in")
    c.audio("trim", "out", "limit", "in")
    c.audio("limit", "out", "out", "in")
    return c


def y2k_riser():
    c = Circuit("y2kriser", "Y2K riser",
                "y2k-riser.ttl\n\nA four-bar build-up at 138 bpm. While a note is held, noise through a band-pass opens from a\n"
                "low rumble to a hiss, a saw climbs in pitch under it, and a square an octave above the saw adds a digital\n"
                "whistle. The envelope opens over 6.4 s, so a note held for four bars ends at the top. The note's pitch is ignored.");
    c.add("rise", "Envelope", attack=6400.0, decay=30.0, sustain=1.0, release=250.0)
    c.add("noise", "Noise", colour=0.2)
    c.add("sweep", "Scale", min=250.0, max=10500.0)
    c.add("bp", "StateVariable", resonance=2.5, drive=1.0)
    c.add("noiseVca", "VCA")
    c.add("noiseLevel", "Gain", gain=-6.0)
    c.add("climb", "Scale", min=80.0, max=2600.0)
    c.add("saw", "Oscillator", shape=1)
    c.add("sawVca", "VCA")
    c.add("sawLevel", "Gain", gain=-14.0)
    c.add("up", "ControlMultiply", b=2.0)
    c.add("bleep", "Oscillator", shape=2)
    c.add("bleepVca", "VCA")
    c.add("bleepLevel", "Gain", gain=-26.0)
    c.add("mix", "Mixer")
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("rise", "out", "sweep", "in")
    c.control("sweep", "out", "bp", "cutoff")
    c.audio("noise", "out", "bp", "in")
    c.audio("bp", "bp", "noiseVca", "in")
    c.control("rise", "out", "noiseVca", "cv")
    c.audio("noiseVca", "out", "noiseLevel", "in")
    c.audio("noiseLevel", "out", "mix", "in")
    c.control("rise", "out", "climb", "in")
    c.control("climb", "out", "saw", "frequency")
    c.audio("saw", "out", "sawVca", "in")
    c.control("rise", "out", "sawVca", "cv")
    c.audio("sawVca", "out", "sawLevel", "in")
    c.audio("sawLevel", "out", "mix", "in")
    c.control("climb", "out", "up", "a")
    c.control("up", "out", "bleep", "frequency")
    c.audio("bleep", "out", "bleepVca", "in")
    c.control("rise", "out", "bleepVca", "cv")
    c.audio("bleepVca", "out", "bleepLevel", "in")
    c.audio("bleepLevel", "out", "mix", "in")
    c.audio("mix", "out", "limit", "in")
    c.audio("limit", "out", "out", "in")
    return c


def copy_edited(src_name, dst_name, header, edits):
    """Copy a Valis example, replace its header and apply exact replacements."""
    path = os.path.join(VALIS, "circuits", src_name)
    with open(path) as f:
        text = f.read()
    i = text.index("@prefix")
    text = header.strip() + "\n\n" + text[i:]
    for old, new, count in edits:
        found = text.count(old)
        if found != count:
            raise SystemExit("%s: expected %d of %r, found %d" % (src_name, count, old, found))
        text = text.replace(old, new)
    with open(os.path.join(OUT, "circuits", dst_name), "w") as f:
        f.write(text)


def main():
    os.makedirs(os.path.join(OUT, "circuits"), exist_ok=True)
    for circuit, fn in ((y2k_kick, "y2k-kick.ttl"), (y2k_bass, "y2k-bass.ttl"),
                        (y2k_lead, "y2k-lead.ttl"), (y2k_bleep, "y2k-bleep.ttl"),
                        (y2k_riser, "y2k-riser.ttl")):
        with open(os.path.join(OUT, "circuits", fn), "w") as f:
            f.write(circuit().text())
    shutil.copyfile(os.path.join(VALIS, "circuits", "909.ttl"), os.path.join(OUT, "circuits", "909.ttl"))
    shutil.copyfile(os.path.join(VALIS, "circuits", "reverb-return.ttl"), os.path.join(OUT, "circuits", "reverb-return.ttl"))
    copy_edited("prophet-5.ttl", "y2k-stab.ttl",
                """# circuits/y2k-stab.ttl
#
# A Y2K chord stab: eight voices of two saws, the second detuned sharp, into a resonant low-pass that an
# envelope opens and closes. The release is short, so a chord on the offbeat is gone before the next one
# arrives, and a chorus widens what is left. Based on the Prophet-5 voice in circuits/prophet-5.ttl, with
# both oscillators on saw, more detune and a faster envelope.""",
                [("lv2:default 700.0", "lv2:default 1200.0", 1),
                 ("lv2:default 5200.0", "lv2:default 6500.0", 1),
                 ("lv2:default 1.0045", "lv2:default 1.008", 1),
                 ("lv2:default 3.0", "lv2:default 2.0", 1),
                 ("lv2:default 320.0", "lv2:default 220.0", 1),
                 ("val:b 1.0045 .", "val:b 1.008 .", 1),
                 ("val:shape 2 .", "val:shape 1 .", 1),
                 ("val:gain -7.0 .", "val:gain -4.0 .", 1),
                 (":filtEnv a val:Envelope ;\n    val:attack 3.0 ;", ":filtEnv a val:Envelope ;\n    val:attack 2.0 ;", 1),
                 (":ampEnv a val:Envelope ;\n    val:attack 3.0 ;", ":ampEnv a val:Envelope ;\n    val:attack 2.0 ;", 1),
                 ("val:min 700.0 ;", "val:min 1200.0 ;", 1),
                 ("val:max 5200.0 .", "val:max 6500.0 .", 1),
                 ("val:release 320.0 .", "val:release 220.0 .", 1),
                 ("val:mix 0.3 .", "val:mix 0.45 .", 1),
                 ("val:gain -9.0 .", "val:gain -8.0 .", 1)])
    copy_edited("quadra-strings.ttl", "y2k-pad.ttl",
                """# circuits/y2k-pad.ttl
#
# A wide pad: eight voices of three saws, one sharp and one flat, through a soft low-pass, two choruses and a
# phaser, with a slow attack and a long release. Based on the string-machine voice in circuits/quadra-strings.ttl,
# with a slower envelope, a darker tone and a longer room.""",
                [("lv2:default 260.0", "lv2:default 900.0", 1),
                 ("lv2:default 520.0", "lv2:default 900.0", 1),
                 ("lv2:default 4200.0", "lv2:default 3000.0", 1),
                 ("val:attack 260.0 ;", "val:attack 900.0 ;", 1),
                 ("val:decay 300.0 ;", "val:decay 600.0 ;", 1),
                 ("val:release 520.0 .", "val:release 900.0 .", 1),
                 ("val:cutoff 4200.0 .", "val:cutoff 3000.0 .", 1),
                 ("val:mix 0.2 .", "val:mix 0.35 .", 1),
                 ("val:gain -10.0 .", "val:gain -12.0 .", 1)])
    copy_edited("dub-delay.ttl", "dub-delay.ttl",
                """# circuits/dub-delay.ttl
#
# A dub echo return: only the repeats come out, for a send. A bucket-brigade delay set to a dotted eighth
# note at 138 bpm (326 ms), with enough feedback that an echo is still audible after three trips round, and
# a low cut so the repeats do not pile up in the bass. Copied from the Valis example, with the delay time
# changed from its 85 bpm setting.""",
                [("val:time 529.0", "val:time 326.0", 1),
                 ("val:feedback 0.62", "val:feedback 0.5", 1),
                 ("val:gain -3.0", "val:gain -2.0", 1)])
    with open(os.path.join(OUT, "score.ttl"), "w") as f:
        f.write(turtle_score())
    with open(os.path.join(OUT, "song.ttl"), "w") as f:
        f.write(turtle_song())
    total = sum(b for _, b, _ in SECTIONS)
    print("wrote %s: %d bars, %.1f s at %d bpm" % (OUT, total, total * 4 * 60.0 / TEMPO, TEMPO))


if __name__ == "__main__":
    main()
