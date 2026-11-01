# scripts/street-hammer/make.py
#
# "Street Hammer": a hardcore techno track inspired by Orff's "Gassenhauer" (a street hit): a bright mallet
# ostinato that bounces under short phrases of a tune, here over a gabber kick, an offbeat distorted bass and
# a hoover lead. No melody of Orff's is used; the material is new. 170 bpm, G minor, 152 bars (about 3:36).
#
#   python3 make.py            write circuits/, score.ttl and song.ttl under artifacts/street-hammer/
#
# Then, with the Valis tools built (`cmake --build build`):
#   valis-song score  artifacts/street-hammer/song.ttl
#   valis-song render artifacts/street-hammer/song.ttl
#   valis-song stems  artifacts/street-hammer/song.ttl
#   valis-song mix    artifacts/street-hammer/song.ttl --version v1 --arc
#
# The arrangement is a table (SECTIONS and PLAN); the score and the song are generated from it, so a changed
# plan is a changed table. The circuits are generated here too, because a Turtle file with one block per
# connection is long to write by hand.
import os, shutil

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "street-hammer"))

TEMPO = 170
STEPS = 16          # sixteenth notes in a 4/4 bar

# -- the plan ---------------------------------------------------------------------------------------------
# name, bars, level (dB) of the whole mix while it plays
SECTIONS = [
    ("intro",  16, -4.0),
    ("build1",  8, -1.0),
    ("drop1",  32,  1.0),
    ("break1", 16, -6.0),
    ("build2",  8, -1.0),
    ("drop2",  32,  2.5),
    ("break2",  8, -6.0),
    ("drop3",  16,  3.0),
    ("outro",  16, -4.0),
]
BARS = dict((n, b) for n, b, _ in SECTIONS)


def rng(a, b):
    return list(range(a, b + 1))


def every(section, start, step=8):
    """Bars start, start+step, ... of a section."""
    return list(range(start, BARS[section] + 1, step))


# part -> section -> list of (pattern, first bar, last bar). A pattern covers its bars; it restarts every
# time it is played, so a one-bar pattern repeats and an eight-bar hook runs through.
PLAN = {}


def play(part, section, pattern, first=1, last=None):
    PLAN.setdefault(part, {}).setdefault(section, []).append((pattern, first, last or BARS[section]))


def lay(part, section, groove, fills=(), gap_last=False, first=1, last=None):
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


# kick (also the boom that lands on each drop)
play("kick", "intro", "kick4", 9, 15); play("kick", "intro", "kick-gap", 16, 16)
lay("kick", "build1", "kick4", [(7, "kick-fill"), (8, "kick-gap")], last=8)
play("kick", "drop1", "boom", 1, 1)
lay("kick", "drop1", "kick4", [(8, "kick-fill"), (16, "kick-fill"), (24, "kick-fill"), (32, "kick-roll")])
lay("kick", "build2", "kick4", [(6, "kick-fill"), (7, "kick-roll"), (8, "kick-gap")], last=8)
play("kick", "drop2", "boom", 1, 1)
lay("kick", "drop2", "kick4", [(8, "kick-fill"), (16, "kick-fill"), (24, "kick-fill"), (32, "kick-roll")])
play("kick", "drop3", "boom", 1, 1)
lay("kick", "drop3", "kick4", [(8, "kick-fill"), (16, "kick-roll")])
play("kick", "outro", "kick4", 1, 7); play("kick", "outro", "kick-gap", 8, 8)
play("kick", "outro", "kick4", 9, 12)

# the 909: hats, clap, snare rolls
play("kit", "intro", "hats", 5, 8); play("kit", "intro", "kit-groove", 9, 16)
lay("kit", "build1", "kit-groove", [(7, "roll8"), (8, "roll16-gap")])
lay("kit", "drop1", "kit-groove", [(8, "tomfill"), (16, "tomfill"), (24, "tomfill"), (32, "roll16")])
play("kit", "break1", "hats", 9, 12); lay("kit", "break1", "hats", [(15, "roll8"), (16, "roll16-gap")], first=13)
lay("kit", "build2", "kit-groove", [(6, "roll8"), (7, "roll16"), (8, "roll16-gap")])
lay("kit", "drop2", "kit-groove", [(8, "tomfill"), (16, "tomfill"), (24, "tomfill"), (32, "roll16")])
play("kit", "break2", "hats", 1, 6); lay("kit", "break2", "hats", [(7, "roll8"), (8, "roll16-gap")], first=7)
lay("kit", "drop3", "kit-groove", [(8, "tomfill"), (16, "roll16")])
play("kit", "outro", "kit-groove", 1, 8); play("kit", "outro", "hats", 9, 16)

# the bass
play("bass", "intro", "bass-off", 13, 16)
play("bass", "build1", "bass-off", 1, 6)
play("bass", "drop1", "bass-off", 1, 31)
play("bass", "build2", "bass-off", 1, 5)
play("bass", "drop2", "bass-roll", 1, 31)
play("bass", "drop3", "bass-roll", 1, 15)
play("bass", "outro", "bass-off", 1, 7)

# the mallet ostinato
play("xylo", "intro", "ost-sparse", 1, 4); play("xylo", "intro", "ost-full", 5, 16)
play("xylo", "build1", "ost-full", 1, 7); play("xylo", "build1", "ost-gap", 8, 8)
play("xylo", "drop1", "ost-full", 1, 31)
play("xylo", "break1", "ost-full", 1, 15); play("xylo", "break1", "ost-gap", 16, 16)
play("xylo", "build2", "ost-full", 1, 7); play("xylo", "build2", "ost-gap", 8, 8)
play("xylo", "drop2", "ost-full", 1, 31)
play("xylo", "break2", "ost-full", 1, 7); play("xylo", "break2", "ost-gap", 8, 8)
play("xylo", "drop3", "ost-full", 1, 15)
play("xylo", "outro", "ost-full", 1, 12); play("xylo", "outro", "ost-sparse", 13, 16)

# the lead: the eight-bar tune, an octave higher in the second drop
play("lead", "build1", "hook", 1, 8)
play("lead", "drop1", "hook", 9, 32)
play("lead", "break1", "hook", 1, 16)
play("lead", "build2", "hook", 1, 8)
play("lead", "drop2", "hook-hi", 1, 32)
play("lead", "break2", "hook", 1, 8)
play("lead", "drop3", "hook-hi", 1, 16)

# risers: a held note whose envelope opens over four bars
play("riser", "build1", "riser4", 5, 8)
play("riser", "break1", "riser4", 13, 16)
play("riser", "build2", "riser4", 5, 8)
play("riser", "break2", "riser4", 5, 8)

PARTS = [  # name, circuit, level dB (playing rms), pan, highpass Hz
    ("kick",  "gabber-kick.ttl", -17, 0.0,   30),
    ("kit",   "909.ttl",         -27, 0.0,  120),
    ("bass",  "hc-bass.ttl",     -23, 0.0,   35),
    ("xylo",  "xylo.ttl",        -28, -0.15, 150),
    ("lead",  "hoover.ttl",      -27, 0.15, 200),
    ("riser", "riser.ttl",       -34, 0.0,  200),
]

# -- the harmony: G minor, a chord a bar, eight bars round -------------------------------------------------
PROGRESSION = "Gm Gm Eb Eb Bb Bb F F"
CHORDS = [  # name, bass root, bass pickup, treble tones (lowest first)
    ("Gm", 31, 38, "70 74 79"),
    ("Eb", 27, 34, "70 75 79"),
    ("Bb", 34, 41, "70 74 77"),
    ("F",  29, 36, "69 72 77"),
]

# the tune: (step from the start of the eight bars, MIDI note, length in steps). Two bars to a chord pair.
HOOK = [
    # over Gm
    (0, 79, 3), (3, 77, 1), (4, 75, 3), (7, 74, 1), (8, 75, 2), (10, 74, 2), (12, 70, 4),
    (16, 74, 3), (19, 70, 1), (20, 67, 3), (23, 70, 1), (24, 74, 2), (26, 77, 2), (28, 79, 4),
    # over Eb
    (32, 79, 3), (35, 75, 1), (36, 77, 3), (39, 79, 1), (40, 82, 2), (42, 79, 2), (44, 75, 4),
    (48, 77, 3), (51, 75, 1), (52, 74, 3), (55, 75, 1), (56, 77, 2), (58, 75, 2), (60, 74, 4),
    # over Bb
    (64, 82, 3), (67, 79, 1), (68, 77, 3), (71, 74, 1), (72, 77, 2), (74, 79, 2), (76, 82, 4),
    (80, 86, 3), (83, 82, 1), (84, 79, 3), (87, 82, 1), (88, 86, 2), (90, 89, 2), (92, 86, 4),
    # over F
    (96, 84, 3), (99, 81, 1), (100, 77, 3), (103, 81, 1), (104, 84, 2), (106, 81, 2), (108, 77, 4),
    (112, 81, 3), (115, 84, 1), (116, 89, 3), (119, 84, 1), (120, 81, 2), (122, 79, 2), (124, 74, 4),
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


def hook_lanes(transpose=0):
    by = {}
    for step, note, length in HOOK:
        by.setdefault((note, length), []).append(step)
    lanes = []
    for (note, length), steps in sorted(by.items()):
        s = ["."] * (8 * STEPS)
        for st in steps:
            s[st] = "x"
        lanes.append(lane("".join(s), key=note, vel=100, length=length, gate=0.85,
                          transpose=transpose if transpose else None))
    return lanes


def patterns():
    """name -> (bars, lanes)"""
    P = {}
    # kick: X is an accent
    P["kick4"]     = (1, [lane(grid("X...|X...|X...|X..."), key=36, vel=104, accent=18)])
    P["kick-gap"]  = (1, [lane(grid("X...|X...|X...|...."), key=36, vel=104, accent=18)])
    P["kick-fill"] = (1, [lane(grid("X...|X...|X...|X.X."), key=36, vel=104, accent=18)])
    P["kick-roll"] = (1, [lane(grid("X...|X...|XxXx|XxXx"), key=36, vel=100, accent=24)])
    P["boom"]      = (1, [lane(grid("X...|....|....|...."), key=35, vel=110, length=14, gate=1.0)])
    # the 909. Its drums are gated by the note's velocity as a level, and the envelope fires only above 0.5 (velocity 64),
    # so every hit here is 64 or more: a quieter one would be silent. (Fixed in the Valis 909 since; kept at these values.)
    P["kit-groove"] = (1, [lane(grid(".x.x|.x.x|.x.x|.x.x"), key=42, vel=72),
                           lane(grid("..x.|..x.|..x.|..x."), key=46, vel=84),
                           lane(grid("....|X...|....|X..."), key=39, vel=92, accent=16)])
    P["hats"]       = (1, [lane(grid("x.x.|x.x.|x.x.|x.x."), key=42, vel=78)])
    P["roll8"]      = (1, [lane(grid("x.x.|x.x.|x.x.|x.x."), key=38, vel=88)])
    P["roll16"]     = (1, [lane(grid("xxxx|xxxx|xxxx|xxxx"), key=38, vel=110)])
    P["roll16-gap"] = (1, [lane(grid("xxxx|xxxx|xxxx|...."), key=38, vel=112)])
    P["tomfill"]    = (1, [lane(grid("....|....|....|x.x."), key=38, vel=96),
                           lane(grid("....|....|....|..x."), key=50, vel=100),
                           lane(grid("....|....|.x.x|...."), key=43, vel=100),
                           lane(grid("....|....|x.x.|...."), key=41, vel=100)])
    # the bass (a voice of the chord of the bar)
    P["bass-off"]   = (1, [lane(grid("..x.|..x.|..x.|..x."), voice="root", vel=100, length=2, gate=0.9)])
    P["bass-roll"]  = (1, [lane(grid(".xxx|.xxx|.xxx|.xxx"), voice="root", vel=100, length=1, gate=0.85),
                           lane(grid("....|....|....|...x"), voice="pickup", vel=96, length=1, gate=0.85)])
    # the mallet ostinato: root, low, top of the chord of the bar, bouncing round each beat
    P["ost-full"]   = (1, [lane(grid("x...|x...|x...|x..."), voice="root", octave=2, vel=96, length=1, gate=0.7),
                           lane(grid("..x.|..x.|..x.|..x."), voice="low", octave=-1, vel=84, length=1, gate=0.7),
                           lane(grid("...x|...x|...x|...x"), voice="top", octave=-1, vel=90, length=1, gate=0.7)])
    P["ost-sparse"] = (1, [lane(grid("x...|x...|x...|x..."), voice="root", octave=2, vel=90, length=1, gate=0.7),
                           lane(grid("....|..x.|....|..x."), voice="low", octave=-1, vel=78, length=1, gate=0.7)])
    P["ost-gap"]    = (1, [lane(grid("x...|x...|x...|...."), voice="root", octave=2, vel=96, length=1, gate=0.7),
                           lane(grid("..x.|..x.|..x.|...."), voice="low", octave=-1, vel=84, length=1, gate=0.7),
                           lane(grid("...x|...x|...x|...."), voice="top", octave=-1, vel=90, length=1, gate=0.7)])
    P["hook"]       = (8, hook_lanes())
    P["hook-hi"]    = (8, hook_lanes(12))
    # a held note for a riser
    P["riser4"]     = (4, [lane("x" + "." * (4 * STEPS - 1), key=60, vel=100, length=62, gate=1.0)])
    return P


def turtle_score():
    P = patterns()
    used = sorted({p for part in PLAN.values() for sec in part.values() for p, _, _ in sec})
    out = []
    out.append("# score.ttl\n#\n# \"Street Hammer\": generated by scripts/street-hammer/make.py from its table. Play it with\n"
               "# `valis-song score song.ttl`. The bass, kit, kick, mallet, lead and riser are all here.\n")
    out.append("@prefix val: <http://purl.org/stuff/valis/> .\n@prefix :    <urn:valis-artifacts:street-hammer#> .\n")
    play_ids = []
    plays = []
    for part, secs in PLAN.items():
        for sec, items in secs.items():
            for k, (pat, a, b) in enumerate(items):
                pid = "%s-%s-%d" % (part, sec, k + 1)
                play_ids.append(":" + pid)
                plays.append(":%s a val:Play ; val:section \"%s\" ; val:part \"%s\" ; val:pattern :%s ; val:fromBar %d ; val:toBar %d ."
                             % (pid, sec, part, pat.replace("-", "_"), a, b))
    chord_ids = [":" + c[0] for c in CHORDS]
    feel_ids = [":xylo-feel", ":lead-feel", ":bass-feel"]
    out.append(":score a val:Score ; val:seed 170 ;\n    val:progression \"%s\" ;\n    val:hasChord %s ;\n    val:hasPattern %s ;\n    val:hasFeel %s ;\n    val:hasPlay\n        %s .\n"
               % (PROGRESSION, " , ".join(chord_ids), " , ".join(":" + p.replace("-", "_") for p in used),
                  " , ".join(feel_ids), " ,\n        ".join(play_ids)))
    for name, root, pickup, tones in CHORDS:
        out.append(":%s a val:Chord ; val:root %d ; val:pickup %d ; val:tones \"%s\" ." % (name, root, pickup, tones))
    out.append("")
    for p in used:
        bars, lanes = P[p]
        out.append(":%s a val:Pattern ; val:bars %d ; val:hasLane\n    %s ." % (p.replace("-", "_"), bars, " ,\n    ".join(lanes)))
    out.append("")
    out.append(':xylo-feel a val:Feel ; val:part "xylo" ; val:timing 1.5 ; val:velocity 6 .')
    out.append(':lead-feel a val:Feel ; val:part "lead" ; val:timing 2 ; val:velocity 5 .')
    out.append(':bass-feel a val:Feel ; val:part "bass" ; val:timing 0.8 ; val:velocity 3 .')
    out.append("")
    out.extend(plays)
    return "\n".join(out) + "\n"


def turtle_song():
    out = []
    out.append("# song.ttl\n#\n# \"Street Hammer\": the layout and the mix as data. Generated by scripts/street-hammer/make.py;\n"
               "# the notes are in score.ttl, played by the circuits in circuits/.\n")
    out.append("@prefix val:  <http://purl.org/stuff/valis/> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix :     <urn:valis-artifacts:street-hammer#> .\n")
    out.append(":song a val:Song ;\n    val:title \"Street Hammer\" ;\n    val:tempo %d ;\n    val:score \"score.ttl\" ;\n    val:loudness -10 ;\n"
               "    val:fadeSeconds 6 ;\n    val:roomAmount 0.05 ;\n    val:roomDecay 0.25 ;\n    val:drive 1.6 ;\n"
               "    val:hasSection %s ;\n    val:hasPart %s ;\n    val:hasReturn :lead-verb ." %
               (TEMPO, " , ".join(":" + n for n, _, _ in SECTIONS), " , ".join(":" + p[0] for p in PARTS)))
    out.append("")
    for i, (n, bars, level) in enumerate(SECTIONS, 1):
        out.append(":%s a val:Section ; val:index %d ; val:bars %d ; val:level %g ." % (n, i, bars, level))
    out.append("")
    for i, (n, circuit, level, pan, hp) in enumerate(PARTS, 1):
        out.append(":%s a val:Part ; val:index %d ; val:circuit \"circuits/%s\" ; val:level %g ; val:pan %g ; val:highpass %d ." %
                   (n, i, circuit, level, pan, hp))
    out.append("")
    out.append(":lead-verb a val:Return ; val:index 1 ; val:source :lead ; val:circuit \"circuits/reverb-return.ttl\" ;\n"
               "    val:level -36 ; val:pan -0.2 ; val:highpass 250 .")
    return "\n".join(out) + "\n"


# -- circuits -------------------------------------------------------------------------------------------
HEADER = """@prefix val:   <http://purl.org/stuff/valis/> .
@prefix lv2:   <http://lv2plug.in/ns/lv2core#> .
@prefix units: <http://lv2plug.in/ns/extensions/units#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix trn:   <http://purl.org/stuff/transmissions/> .
@prefix :      <urn:valis-artifacts:street-hammer:%s#> .
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


def gabber_kick():
    c = Circuit("gabberkick", "Gabber kick",
                "gabber-kick.ttl\n\nA hardcore kick. A sine falls from 330 Hz to the G below the bass (49 Hz) in about 40 ms,\n"
                "its amplitude falls over 300 ms, and the result is driven into a tanh stage and a hard clip AFTER the envelope, so the\n"
                "tail stays clipped and loud while it dies away: that is the sound. A short high noise click gives the attack.\n"
                "Key 36 is the kick; key 35 is a long sub boom for the start of a drop.\n"
                "Gabber: https://en.wikipedia.org/wiki/Gabber_(music_genre)")
    c.add("kGate", "NoteGate", note=36)
    c.add("kPitchEnv", "Envelope", attack=0.1, decay=40.0, sustain=0.0, release=3.0)
    c.add("kPitch", "Scale", min=49.0, max=330.0)
    c.add("kOsc", "Oscillator", shape=0)
    c.add("kAmpEnv", "Envelope", attack=0.4, decay=300.0, sustain=0.0, release=30.0)
    c.add("kVca", "VCA")
    c.add("kDrive", "Tanh", gain=14.0)
    c.add("kClip", "HardClip", threshold=0.7)
    c.add("kLevel", "Gain", gain=-6.0)
    c.add("clickNoise", "Noise", colour=0.0)
    c.add("clickHp", "Biquad", mode=4, frequency=3500.0, q=0.7)
    c.add("clickEnv", "Envelope", attack=0.1, decay=5.0, sustain=0.0, release=2.0)
    c.add("clickVca", "VCA")
    c.add("clickLevel", "Gain", gain=-16.0)
    c.add("bGate", "NoteGate", note=35)
    c.add("bPitchEnv", "Envelope", attack=0.5, decay=380.0, sustain=0.0, release=20.0)
    c.add("bPitch", "Scale", min=38.0, max=115.0)
    c.add("bOsc", "Oscillator", shape=0)
    c.add("bAmpEnv", "Envelope", attack=4.0, decay=2400.0, sustain=0.0, release=500.0)
    c.add("bVca", "VCA")
    c.add("bLevel", "Gain", gain=-3.0)
    c.add("mix", "Mixer")
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("kGate", "gate", "kPitchEnv", "gate"); c.control("kGate", "gate", "kAmpEnv", "gate")
    c.control("kGate", "gate", "clickEnv", "gate")
    c.control("kPitchEnv", "out", "kPitch", "in"); c.control("kPitch", "out", "kOsc", "frequency")
    c.audio("kOsc", "out", "kVca", "in"); c.control("kAmpEnv", "out", "kVca", "cv")
    c.audio("kVca", "out", "kDrive", "in"); c.audio("kDrive", "out", "kClip", "in"); c.audio("kClip", "out", "kLevel", "in")
    c.audio("kLevel", "out", "mix", "in")
    c.audio("clickNoise", "out", "clickHp", "in"); c.audio("clickHp", "out", "clickVca", "in")
    c.control("clickEnv", "out", "clickVca", "cv"); c.audio("clickVca", "out", "clickLevel", "in")
    c.audio("clickLevel", "out", "mix", "in")
    c.control("bGate", "gate", "bPitchEnv", "gate"); c.control("bGate", "gate", "bAmpEnv", "gate")
    c.control("bPitchEnv", "out", "bPitch", "in"); c.control("bPitch", "out", "bOsc", "frequency")
    c.audio("bOsc", "out", "bVca", "in"); c.control("bAmpEnv", "out", "bVca", "cv")
    c.audio("bVca", "out", "bLevel", "in"); c.audio("bLevel", "out", "mix", "in")
    c.audio("mix", "out", "limit", "in"); c.audio("limit", "out", "out", "in")
    return c


def xylo():
    c = Circuit("xylo", "Mallet",
                "xylo.ttl\n\nA struck bar: a short burst of noise, softened by a low-pass, strikes a val:ModalBank in marimba mode (the\n"
                "modes of a bar, not a string). A short ring, so a fast ostinato stays separate notes.\n"
                "See also examples/modal-tom.ttl, which this is cut down from.")
    c.add("pitch", "MidiPitch")
    c.add("noise", "Noise", colour=0.5)
    c.add("tone", "OnePole", cutoff=4200.0, mode=0.0)
    c.add("env", "Envelope", attack=0.1, decay=6.0, sustain=0.0, release=1.0)
    c.add("vca", "VCA")
    c.add("bank", "ModalBank", decay=0.38, brightness=0.85, mode=0.0)
    c.add("vol", "Gain", gain=-22.0)
    c.add("out", "Output")
    c.audio("noise", "out", "tone", "in"); c.audio("tone", "out", "vca", "in")
    c.audio("vca", "out", "bank", "in"); c.audio("bank", "out", "vol", "in"); c.audio("vol", "out", "out", "in")
    c.control("pitch", "out", "bank", "frequency"); c.control("env", "out", "vca", "cv")
    return c


def hoover():
    c = Circuit("hoover", "Hoover lead",
                "hoover.ttl\n\nA hardcore lead. Four saws (one at the pitch, two detuned a little either side, one an octave up) into a\n"
                "resonant ladder filter that an envelope opens and closes, a tanh stage, a chorus and an amplitude envelope. The pitch\n"
                "glides a little between notes (val:Slew), which is the swoop of the sound.\n"
                "Hoover: https://en.wikipedia.org/wiki/Hoover_sound")
    c.add("pitch", "MidiPitch")
    c.add("glide", "Slew", rise=35.0, fall=35.0)
    c.add("r1", "ControlMultiply", b=1.0)
    c.add("r2", "ControlMultiply", b=1.0085)
    c.add("r3", "ControlMultiply", b=0.9915)
    c.add("r4", "ControlMultiply", b=2.0)
    for i in (1, 2, 3, 4):
        c.add("saw%d" % i, "Oscillator", shape=1)
    c.add("l1", "Gain", gain=-4.0); c.add("l2", "Gain", gain=-5.0); c.add("l3", "Gain", gain=-5.0); c.add("l4", "Gain", gain=-10.0)
    c.add("mix", "Mixer")
    c.add("filtEnv", "Envelope", attack=2.0, decay=280.0, sustain=0.55, release=140.0)
    c.add("cutoff", "Scale", min=1800.0, max=9000.0)
    c.add("vcf", "Ladder", resonance=0.3, drive=1.5)
    c.add("drive", "Tanh", gain=4.0)
    c.add("ampEnv", "Envelope", attack=3.0, decay=200.0, sustain=0.8, release=110.0)
    c.add("vca", "VCA")
    c.add("chorus", "Chorus", rate=0.7, depth=2.0, mix=0.4)
    c.add("trim", "Gain", gain=-8.0)
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("pitch", "out", "glide", "in")
    for i in (1, 2, 3, 4):
        c.control("glide", "out", "r%d" % i, "a")
        c.control("r%d" % i, "out", "saw%d" % i, "frequency")
        c.audio("saw%d" % i, "out", "l%d" % i, "in")
        c.audio("l%d" % i, "out", "mix", "in")
    c.control("filtEnv", "out", "cutoff", "in"); c.control("cutoff", "out", "vcf", "cutoff")
    c.audio("mix", "out", "vcf", "in"); c.audio("vcf", "out", "drive", "in"); c.audio("drive", "out", "vca", "in")
    c.control("ampEnv", "out", "vca", "cv")
    c.audio("vca", "out", "chorus", "in"); c.audio("chorus", "out", "trim", "in")
    c.audio("trim", "out", "limit", "in"); c.audio("limit", "out", "out", "in")
    return c


def riser():
    c = Circuit("riser", "Riser",
                "riser.ttl\n\nA build-up. While a note is held, noise through a band-pass opens from a low rumble to a hiss, and a saw\n"
                "climbs in pitch under it, both over the envelope's 5 second attack, so a note held for four bars (5.6 s at 170 bpm)\n"
                "ends at the top. The note's pitch is ignored.")
    c.add("rise", "Envelope", attack=5000.0, decay=20.0, sustain=1.0, release=150.0)
    c.add("noise", "Noise", colour=0.2)
    c.add("sweep", "Scale", min=250.0, max=11000.0)
    c.add("bp", "StateVariable", resonance=2.5, drive=1.0)
    c.add("noiseVca", "VCA")
    c.add("noiseLevel", "Gain", gain=-6.0)
    c.add("climb", "Scale", min=90.0, max=2400.0)
    c.add("saw", "Oscillator", shape=1)
    c.add("sawVca", "VCA")
    c.add("sawLevel", "Gain", gain=-14.0)
    c.add("mix", "Mixer")
    c.add("limit", "Limiter", ceiling=-1.0)
    c.add("out", "Output")
    c.control("rise", "out", "sweep", "in"); c.control("sweep", "out", "bp", "cutoff")
    c.audio("noise", "out", "bp", "in"); c.audio("bp", "bp", "noiseVca", "in"); c.control("rise", "out", "noiseVca", "cv")
    c.audio("noiseVca", "out", "noiseLevel", "in"); c.audio("noiseLevel", "out", "mix", "in")
    c.control("rise", "out", "climb", "in"); c.control("climb", "out", "saw", "frequency")
    c.audio("saw", "out", "sawVca", "in"); c.control("rise", "out", "sawVca", "cv")
    c.audio("sawVca", "out", "sawLevel", "in"); c.audio("sawLevel", "out", "mix", "in")
    c.audio("mix", "out", "limit", "in"); c.audio("limit", "out", "out", "in")
    return c


def main():
    os.makedirs(os.path.join(OUT, "circuits"), exist_ok=True)
    for circuit, fn in ((gabber_kick, "gabber-kick.ttl"), (xylo, "xylo.ttl"), (hoover, "hoover.ttl"), (riser, "riser.ttl")):
        with open(os.path.join(OUT, "circuits", fn), "w") as f:
            f.write(circuit().text())
    for src, dst in (("909.ttl", "909.ttl"), ("psych-bass.ttl", "hc-bass.ttl"), ("reverb-return.ttl", "reverb-return.ttl")):
        shutil.copyfile(os.path.join(VALIS, "examples", src), os.path.join(OUT, "circuits", dst))
    with open(os.path.join(OUT, "score.ttl"), "w") as f:
        f.write(turtle_score())
    with open(os.path.join(OUT, "song.ttl"), "w") as f:
        f.write(turtle_song())
    total = sum(b for _, b, _ in SECTIONS)
    print("wrote %s: %d bars, %.1f s at %d bpm" % (OUT, total, total * 4 * 60.0 / TEMPO, TEMPO))


if __name__ == "__main__":
    main()
