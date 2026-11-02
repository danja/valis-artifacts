# scripts/all-fall-down/make.py
#
# "All Fall Down": a 140 bpm dance track in A minor whose tunes are nursery rhymes turned minor, so they stay
# recognisable and become eerie. The tunes are traditional and long out of copyright:
#   - "Twinkle, Twinkle, Little Star" (the French song "Ah! vous dirai-je, maman", 1761) and "Baa, Baa, Black Sheep",
#     which share it. The lead plays it; in the second drop the bass plays it two octaves down as "baa baa".
#   - "London Bridge Is Falling Down", the break and the outro (the lullaby the track ends on).
#   - "Mary Had a Little Lamb" (Sarah Josepha Hale, 1830), on the toy-piano pluck in the intro.
# Every note of each tune is moved onto the A natural minor scale, so a major third becomes a minor third, and the
# chords under them are minor too. The instruments are the eight in circuits/nursery-*.ttl.
#
#   python3 make.py            write circuits/, score.ttl and song.ttl under artifacts/all-fall-down/
#
# Then, with the Valis tools built (`cmake --build build`):
#   valis-song score  artifacts/all-fall-down/song.ttl
#   valis-song render artifacts/all-fall-down/song.ttl
#   valis-song stems  artifacts/all-fall-down/song.ttl
#   valis-song mix    artifacts/all-fall-down/song.ttl --version v1 --arc
import os, shutil

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "all-fall-down"))

TEMPO = 140
STEPS = 16          # sixteenth notes in a 4/4 bar

# -- the plan ---------------------------------------------------------------------------------------------
# name, bars, level (dB) of the whole mix while it plays
SECTIONS = [
    ("intro",  16, 1.5),
    ("build1",  8, 1.0),
    ("drop1",  16,  1.0),
    ("break",  16, 2.0),
    ("build2",  8, 1.0),
    ("drop2",  24,  2.5),
    ("outro",  16, 1.5),
]
BARS = dict((n, b) for n, b, _ in SECTIONS)

# the eight-bar chord loop, and the break's, which keeps to the tonic and the subdominant
PROGRESSION = "Am F Dm E F G Am E"
BREAK_PROGRESSION = "Am Am Dm E Am Am Dm Am"

PLAN = {}


def play(part, section, pattern, first=1, last=None, prog=None):
    PLAN.setdefault(part, {}).setdefault(section, []).append((pattern, first, last or BARS[section], prog))


def lay(part, section, groove, fills=(), first=1, last=None, prog=None):
    """A groove over the section with one-bar replacements (fills) at the given bars."""
    last = last or BARS[section]
    at = first
    where = dict(fills)
    for b in sorted(where):
        if b > last:
            break
        if b > at:
            play(part, section, groove, at, b - 1, prog)
        play(part, section, where[b], b, b, prog)
        at = b + 1
    if at <= last:
        play(part, section, groove, at, last, prog)


# kick: the Humpty kick. Any note plays it.
play("kick", "intro", "kick-light", 13, 16)
lay("kick", "build1", "kick4", [(7, "kick-fill"), (8, "kick-gap")])
lay("kick", "drop1", "kick4", [(16, "kick-fill")])
play("kick", "break", "kick-light", 13, 16)
lay("kick", "build2", "kick4", [(7, "kick-roll"), (8, "kick-gap")])
lay("kick", "drop2", "kick4", [(8, "kick-fill"), (16, "kick-fill"), (24, "kick-roll")])
play("kick", "outro", "kick4", 1, 8); play("kick", "outro", "kick-light", 9, 12)

# the rattle snare: a backbeat, and rolls into each drop
lay("snare", "build1", "backbeat", [(5, "roll8"), (6, "roll8"), (7, "roll16"), (8, "roll16-gap")], first=3)
lay("snare", "drop1", "backbeat", [(16, "roll8")])
play("snare", "break", "tick", 9, 14); play("snare", "break", "roll8", 15, 15); play("snare", "break", "roll16-gap", 16, 16)
lay("snare", "build2", "backbeat", [(5, "roll8"), (6, "roll8"), (7, "roll16"), (8, "roll16-gap")])
lay("snare", "drop2", "backbeat", [(8, "roll8"), (16, "roll8"), (24, "roll16")])
play("snare", "outro", "backbeat", 1, 8)

# the hat: the Ding Dong hat; its velocity picks closed or open
play("hat", "intro", "hat-closed", 9, 12); play("hat", "intro", "hat-full", 13, 16)
play("hat", "build1", "hat-full", 1, 8)
play("hat", "drop1", "hat-full", 1, 16)
play("hat", "break", "hat-closed", 9, 16)
play("hat", "build2", "hat-full", 1, 8)
play("hat", "drop2", "hat-full", 1, 24)
play("hat", "outro", "hat-full", 1, 8); play("hat", "outro", "hat-closed", 9, 12)

# the bass: offbeats, and in the second drop the tune, two octaves down, "baa baa"
play("bass", "build1", "bass-off", 5, 7)
play("bass", "drop1", "bass-off", 1, 15)
play("bass", "build2", "bass-baa", 1, 8)
play("bass", "drop2", "bass-baa", 1, 8); play("bass", "drop2", "bass-off", 9, 16); play("bass", "drop2", "bass-baa", 17, 24)
play("bass", "outro", "bass-off", 1, 8, BREAK_PROGRESSION)

# the lead: the first four bars of the star tune as a promise in the first build, then the whole tune
play("lead", "build1", "twinkle", 5, 8)
play("lead", "drop1", "twinkle", 1, 16)
play("lead", "break", "london", 9, 16)
play("lead", "drop2", "twinkle", 1, 24)
play("lead", "outro", "london", 1, 8)

# the arp: the lamb in the intro, the spider climbing in builds and drops, the falling bridge in the break
play("arp", "intro", "mary", 1, 16)
play("arp", "build1", "climb", 1, 8)
play("arp", "drop1", "climb", 1, 16)
play("arp", "break", "london", 1, 8); play("arp", "break", "mary", 9, 16)
play("arp", "build2", "climb", 1, 8)
play("arp", "drop2", "climb", 1, 24)
play("arp", "outro", "mary", 1, 16)

# the pad: the cradle, under almost everything
play("pad", "intro", "pad", 1, 16)
play("pad", "build1", "pad", 1, 8)
play("pad", "drop1", "pad", 1, 16)
play("pad", "break", "pad", 1, 16, BREAK_PROGRESSION)
play("pad", "build2", "pad", 1, 8)
play("pad", "drop2", "pad", 1, 24)
play("pad", "outro", "pad", 1, 12, BREAK_PROGRESSION)

# risers: a held note whose envelope opens over four bars
play("riser", "build1", "riser4", 5, 8)
play("riser", "break", "riser4", 13, 16)
play("riser", "build2", "riser4", 5, 8)

PARTS = [  # name, circuit, level dB (playing rms), pan, highpass Hz, follows
    ("kick",  "nursery-humpty-kick.ttl",       -17,  0.0,   30, None),
    # val:follows is not used: a follower's level is an offset from its leader's gain and cannot be above 0 dB, and
    # the hat needs to be louder than the kick's gain would make it. Both play in most of the windows measured.
    ("snare", "nursery-rattle-snare.ttl",      -22,  0.0,  120, None),
    ("hat",   "nursery-ding-dong-hat.ttl",     -30,  0.1,  400, None),
    ("bass",  "nursery-black-sheep-bass.ttl",  -22,  0.0,   35, None),
    ("lead",  "nursery-twinkle-lead.ttl",      -21,  0.1,  200, None),
    ("arp",   "nursery-incy-wincy-arp.ttl",    -27, -0.25, 150, None),
    ("pad",   "nursery-rock-a-bye-pad.ttl",    -27,  0.0,   70, None),
    ("riser", "nursery-wind-up-riser.ttl",     -31,  0.0,  200, None),
]

# A part made outside Valis: the SAM speech synthesizer through nursery-voice-vocoder.ttl, played in Reaper and rendered by hand to
# wavs/voice.wav (see README.md). It has no circuit here and no MIDI; the mix levels it like any stem.
RECORDED = [  # name, level dB (playing rms), pan, highpass Hz
    ("voice", -22, 0.0, 150),
]

# -- the harmony: A natural minor ------------------------------------------------------------------------
CHORDS = [  # name, bass root, bass pickup, treble tones (lowest first)
    ("Am", 33, 40, "57 60 64"),
    ("F",  29, 36, "53 57 60"),
    ("Dm", 38, 45, "50 53 57"),
    ("E",  28, 35, "52 59 64"),     # open: a root and a fifth, so the tunes' C and A do not clash with a G sharp
    ("G",  31, 38, "55 59 62"),
]

# -- the tunes: (step from the start of the eight bars, MIDI note, length in steps) ---------------------------
# "Twinkle, Twinkle, Little Star" on the A minor scale: 1 1 5 5 6 6 5 | 4 4 3 3 2 2 1 | 5 5 4 4 3 3 2 | 5 5 4 4 3 3 2.
# The last note is the second degree, so the tune asks a question each time round and the loop answers it.
TWINKLE = [
    (0, 69, 4), (4, 69, 4), (8, 76, 4), (12, 76, 4),
    (16, 77, 4), (20, 77, 4), (24, 76, 8),
    (32, 74, 4), (36, 74, 4), (40, 72, 4), (44, 72, 4),
    (48, 71, 4), (52, 71, 4), (56, 69, 8),
    (64, 76, 4), (68, 76, 4), (72, 74, 4), (76, 74, 4),
    (80, 72, 4), (84, 72, 4), (88, 71, 8),
    (96, 76, 4), (100, 76, 4), (104, 74, 4), (108, 74, 4),
    (112, 72, 4), (116, 72, 4), (120, 71, 8),
]

# "London Bridge Is Falling Down": 5 6 5 4 3 4 5 | 2 3 4 | 3 4 5 | 5 6 5 4 3 4 5 | 2 5 3 1, on the same scale
LONDON = [
    (0, 76, 6), (6, 77, 2), (8, 76, 4), (12, 74, 4),
    (16, 72, 4), (20, 74, 4), (24, 76, 8),
    (32, 71, 4), (36, 72, 4), (40, 74, 8),
    (48, 72, 4), (52, 74, 4), (56, 76, 8),
    (64, 76, 6), (70, 77, 2), (72, 76, 4), (76, 74, 4),
    (80, 72, 4), (84, 74, 4), (88, 76, 8),
    (96, 71, 4), (100, 76, 4), (104, 72, 4), (108, 69, 4),
    (112, 69, 12),
]

# "Mary Had a Little Lamb": 3 2 1 2 | 3 3 3 | 2 2 2 | 3 5 5 | 3 2 1 2 | 3 3 3 3 | 2 2 3 2 | 1
MARY = [
    (0, 72, 4), (4, 71, 4), (8, 69, 4), (12, 71, 4),
    (16, 72, 4), (20, 72, 4), (24, 72, 8),
    (32, 71, 4), (36, 71, 4), (40, 71, 8),
    (48, 72, 4), (52, 76, 4), (56, 76, 8),
    (64, 72, 4), (68, 71, 4), (72, 69, 4), (76, 71, 4),
    (80, 72, 4), (84, 72, 4), (88, 72, 4), (92, 72, 4),
    (96, 71, 4), (100, 71, 4), (104, 72, 4), (108, 71, 4),
    (112, 69, 16),
]



# -- the voice: lyrics for a speech synth, one word to a beat ---------------------------------------------------
# (section, bar of the section, beat 0 to 3, words). "_" is a rest. The synth (the SAM plugin, in Transport mode with a
# step of 1/4) speaks one slot to a beat from bar 1, so the text is the song's 104 bars of four slots, with a rest in
# every slot nobody speaks in. The words are fragments of traditional rhymes ("Ring a Ring o' Roses", "London Bridge Is
# Falling Down", "Humpty Dumpty", "Twinkle, Twinkle, Little Star", "Baa, Baa, Black Sheep", "Rock-a-bye Baby", "Mary Had a
# Little Lamb"), which are out of copyright, with the order broken on purpose.
VOICE = [
    # the intro: a calm recitation that trails off
    ("intro", 9, 0, "twinkle twinkle little star"),
    ("intro", 10, 0, "how I wonder what you are"),
    ("intro", 12, 0, "up above the world so high"),
    ("intro", 14, 0, "like a diamond in the"),
    # the first build: the first slip
    ("build1", 5, 0, "ring a ring o roses"),
    ("build1", 6, 1, "a pocket full of"),
    ("build1", 7, 1, "a pocket full of"),
    ("build1", 8, 1, "pocket full pocket"),
    # the first drop: chopped, a word or two on the beat
    ("drop1", 1, 0, "all _ all fall"),
    ("drop1", 2, 0, "fall down _ down"),
    ("drop1", 3, 0, "down down _ _"),
    ("drop1", 4, 0, "we all _ we"),
    ("drop1", 5, 0, "all fall _ fall"),
    ("drop1", 6, 0, "fall fall fall _"),
    ("drop1", 9, 0, "hush _ _ _"),
    ("drop1", 11, 0, "all fall down _"),
    # the break: the breakdown, the voice loses its place
    ("break", 1, 0, "london bridge is falling down"),
    ("break", 2, 2, "falling down falling down"),
    ("break", 4, 0, "london bridge is falling up"),
    ("break", 5, 2, "falling up falling"),
    ("break", 7, 0, "humpty _ humpty humpty"),
    ("break", 8, 0, "humpty sat on a"),
    ("break", 9, 0, "sat on a sat"),
    ("break", 10, 0, "on a sat on"),
    ("break", 11, 0, "all the kings horses"),
    ("break", 12, 0, "and all the kings"),
    ("break", 13, 0, "and all the all"),
    ("break", 14, 0, "the all couldnt couldnt"),
    ("break", 15, 0, "when the bough _"),
    ("break", 16, 0, "when the _ when"),
    # the second build: a stutter
    ("build2", 1, 0, "wake wake wake wake"),
    ("build2", 2, 0, "twinkle twinkle twinkle twinkle"),
    ("build2", 3, 0, "little little little little"),
    ("build2", 4, 0, "what what what what"),
    ("build2", 5, 0, "what are are are"),
    ("build2", 6, 0, "are you are you"),
    ("build2", 7, 0, "ring a ring a"),
    ("build2", 8, 0, "all all all all"),
    # the second drop: fragments over the tune, and one clear line at the end
    ("drop2", 1, 0, "baa baa _ _"),
    ("drop2", 2, 0, "baa baa black _"),
    ("drop2", 3, 0, "baa _ baa _"),
    ("drop2", 4, 0, "have you any _"),
    ("drop2", 5, 0, "have you _ _"),
    ("drop2", 6, 0, "have _ _ _"),
    ("drop2", 9, 0, "we all fall down"),
    ("drop2", 10, 0, "we all fall _"),
    ("drop2", 11, 0, "we fall _ _"),
    ("drop2", 12, 0, "I fall _ _"),
    ("drop2", 21, 0, "all fall down _"),
    ("drop2", 22, 0, "all fall down _"),
    ("drop2", 23, 0, "all fall down _"),
    # the outro: calm again, but the rhyme has changed
    ("outro", 1, 0, "twinkle twinkle _ _"),
    ("outro", 2, 0, "little _ _ _"),
    ("outro", 3, 0, "little _ _ _"),
    ("outro", 4, 0, "lamb _ _ _"),
    ("outro", 5, 0, "mary had a little"),
    ("outro", 6, 0, "star _ _ _"),
    ("outro", 9, 0, "hush _ hush _"),
    ("outro", 11, 0, "all fall down _"),
    ("outro", 12, 0, "all fall _ _"),
    ("outro", 13, 0, "all _ _ _"),
]


def voice_slots():
    """The song as a list of four slots a bar: a word, or '_'."""
    start = {}
    first = 1
    for name, bars, _ in SECTIONS:
        start[name] = first
        first += bars
    total = sum(b for _, b, _ in SECTIONS)
    slots = ["_"] * (total * 4)
    for section, bar, beat, words in VOICE:
        at = (start[section] + bar - 2) * 4 + beat
        for k, w in enumerate(words.split()):
            assert slots[at + k] == "_", (section, bar, beat, words)
            slots[at + k] = w
    while slots and slots[-1] == "_":
        slots.pop()
    return slots


def voice_text():
    return " ".join(voice_slots())


def lyrics_markdown():
    out = ["# All Fall Down: lyrics for a speech synth\n",
           "Generated by `scripts/all-fall-down/make.py` from its `VOICE` table; do not edit it here. The same table makes `voice.txt`, the text "
           "loaded into the SAM speech plugin.\n",
           "A short, broken text. The voice starts calm, as if reciting a rhyme to a child, and comes apart as the track goes on: lines "
           "repeat, words stick, the rhymes run into each other and lose their order, and at the end the voice is calm again but has "
           "forgotten how the rhyme goes. The fragments are traditional nursery rhymes, which are out of copyright. Each word is spoken on a "
           "beat (a bar at 140 bpm is 1.714 seconds); `_` is a beat of rest. Bar numbers are from the start of the section.\n"]
    sec = None
    for section, bar, beat, words in VOICE:
        if section != sec:
            sec = section
            out.append("\n## %s (%d bars)\n" % (section, BARS[section]))
        where = "bar %d" % bar + (", beat %d" % (beat + 1) if beat else "")
        out.append("* %s: %s" % (where, words))
    return "\n".join(out) + "\n"


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


def tune_lanes(tune, vel=100, gate=0.9, transpose=0):
    by = {}
    for step, note, length in tune:
        by.setdefault((note, length), []).append(step)
    lanes = []
    for (note, length), steps in sorted(by.items()):
        s = ["."] * (8 * STEPS)
        for st in steps:
            s[st] = "x"
        lanes.append(lane("".join(s), key=note, vel=vel, length=length, gate=gate,
                          transpose=transpose if transpose else None))
    return lanes


def climb_lanes():
    """Eight notes a bar, up the chord and back: low, top, root, top, root, top, root, top (an octave each)."""
    seq = [("low", 0), ("top", 0), ("root", 3), ("top", 1), ("root", 4), ("top", 1), ("root", 3), ("top", 0)]
    by = {}
    for i, key in enumerate(seq):
        by.setdefault(key, []).append(i * 2)
    lanes = []
    for (voice, octave), steps in sorted(by.items()):
        s = ["."] * STEPS
        for st in steps:
            s[st] = "x"
        lanes.append(lane("".join(s), voice=voice, octave=octave if octave else None, vel=96, length=2, gate=0.8))
    return lanes


def patterns():
    """name -> (bars, lanes)"""
    P = {}
    # the kick (key 36): X is an accent
    P["kick4"]      = (1, [lane(grid("X...|X...|X...|X..."), key=36, vel=104, accent=18)])
    P["kick-light"] = (1, [lane(grid("X...|....|X...|...."), key=36, vel=100, accent=18)])
    P["kick-fill"]  = (1, [lane(grid("X...|X...|X...|X.X."), key=36, vel=104, accent=18)])
    P["kick-roll"]  = (1, [lane(grid("X...|X...|XxXx|XxXx"), key=36, vel=100, accent=24)])
    P["kick-gap"]   = (1, [lane(grid("X...|X...|X...|...."), key=36, vel=104, accent=18)])
    # the snare (key 38; any note plays it)
    P["backbeat"]   = (1, [lane(grid("....|X...|....|X..."), key=38, vel=100, accent=16)])
    P["tick"]       = (1, [lane(grid("....|....|....|x..."), key=38, vel=70)])
    P["roll8"]      = (1, [lane(grid("x.x.|x.x.|x.x.|x.x."), key=38, vel=90)])
    P["roll16"]     = (1, [lane(grid("xxxx|xxxx|xxxx|xxxx"), key=38, vel=110)])
    P["roll16-gap"] = (1, [lane(grid("xxxx|xxxx|xxxx|...."), key=38, vel=110)])
    # the hat. Velocity chooses how long it rings, so a closed hat is soft and the open one on the offbeat is hard.
    P["hat-closed"] = (1, [lane(grid("xxxx|xxxx|xxxx|xxxx"), key=42, vel=20)])
    P["hat-full"]   = (1, [lane(grid("xx.x|xx.x|xx.x|xx.x"), key=42, vel=20),
                           lane(grid("..x.|..x.|..x.|..x."), key=46, vel=120)])
    # the bass: a voice of the chord of the bar
    P["bass-off"]   = (1, [lane(grid("..x.|..x.|..x.|..x."), voice="root", vel=100, length=2, gate=0.9)])
    P["bass-baa"]   = (8, tune_lanes(TWINKLE, vel=104, gate=0.88, transpose=-36))
    # the tunes
    P["twinkle"]    = (8, tune_lanes(TWINKLE, vel=100, gate=0.9))
    P["london"]     = (8, tune_lanes(LONDON, vel=96, gate=0.9))
    P["mary"]       = (8, tune_lanes(MARY, vel=88, gate=0.85))
    P["climb"]      = (1, climb_lanes())
    # the pad: the chord's root a bar at a time
    P["pad"]        = (1, [lane("x" + "." * (STEPS - 1), voice="root", octave=1, vel=90, length=16, gate=0.98)])
    # a held note for a riser
    P["riser4"]     = (4, [lane("x" + "." * (4 * STEPS - 1), key=60, vel=100, length=62, gate=1.0)])
    return P


def turtle_score():
    P = patterns()
    used = sorted({p for part in PLAN.values() for sec in part.values() for p, _, _, _ in sec})
    out = []
    out.append("# score.ttl\n#\n# \"All Fall Down\": generated by scripts/all-fall-down/make.py from its table. Play it with\n"
               "# `valis-song score song.ttl`.\n")
    out.append("@prefix val: <http://purl.org/stuff/valis/> .\n@prefix :    <urn:valis-artifacts:all-fall-down#> .\n")
    play_ids, plays = [], []
    for part, secs in PLAN.items():
        for sec, items in secs.items():
            for k, (pat, a, b, prog) in enumerate(items):
                pid = "%s-%s-%d" % (part, sec, k + 1)
                play_ids.append(":" + pid)
                extra = ' ; val:progression "%s"' % prog if prog else ""
                plays.append(":%s a val:Play ; val:section \"%s\" ; val:part \"%s\" ; val:pattern :%s ; val:fromBar %d ; val:toBar %d%s ."
                             % (pid, sec, part, pat.replace("-", "_"), a, b, extra))
    chord_ids = [":" + c[0] for c in CHORDS]
    feel_ids = [":lead-feel", ":arp-feel", ":bass-feel", ":hat-feel", ":kick-feel"]
    out.append(":score a val:Score ; val:seed 140 ;\n    val:progression \"%s\" ;\n    val:hasChord %s ;\n    val:hasPattern %s ;\n    val:hasFeel %s ;\n    val:hasPlay\n        %s .\n"
               % (PROGRESSION, " , ".join(chord_ids), " , ".join(":" + p.replace("-", "_") for p in used),
                  " , ".join(feel_ids), " ,\n        ".join(play_ids)))
    for name, root, pickup, tones in CHORDS:
        out.append(":%s a val:Chord ; val:root %d ; val:pickup %d ; val:tones \"%s\" ." % (name, root, pickup, tones))
    out.append("")
    for p in used:
        bars, lanes = P[p]
        out.append(":%s a val:Pattern ; val:bars %d ; val:hasLane\n    %s ." % (p.replace("-", "_"), bars, " ,\n    ".join(lanes)))
    out.append("")
    out.append(':lead-feel a val:Feel ; val:part "lead" ; val:timing 2 ; val:velocity 4 .')
    out.append(':arp-feel  a val:Feel ; val:part "arp" ; val:timing 1.5 ; val:velocity 5 .')
    out.append(':bass-feel a val:Feel ; val:part "bass" ; val:timing 0.8 ; val:velocity 3 .')
    out.append(':hat-feel  a val:Feel ; val:part "hat" ; val:timing 1.2 ; val:velocity 4 .')
    out.append(':kick-feel a val:Feel ; val:part "kick" ; val:timing 0.4 ; val:velocity 2 .')
    out.append("")
    out.extend(plays)
    return "\n".join(out) + "\n"


def turtle_song():
    out = []
    out.append("# song.ttl\n#\n# \"All Fall Down\": the layout and the mix as data. Generated by scripts/all-fall-down/make.py;\n"
               "# the notes are in score.ttl, played by the circuits in circuits/.\n")
    out.append("@prefix val:  <http://purl.org/stuff/valis/> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix :     <urn:valis-artifacts:all-fall-down#> .\n")
    out.append(":song a val:Song ;\n    val:title \"All Fall Down\" ;\n    val:tempo %d ;\n    val:score \"score.ttl\" ;\n    val:loudness -10 ;\n"
               "    val:fadeSeconds 8 ;\n    val:roomAmount 0.07 ;\n    val:roomDecay 0.35 ;\n    val:drive 1.4 ;\n"
               "    val:hasSection %s ;\n    val:hasPart %s ;\n    val:hasReturn :lead-verb ." %
               (TEMPO, " , ".join(":" + n for n, _, _ in SECTIONS), " , ".join(":" + p[0] for p in PARTS + RECORDED)))
    out.append("")
    for i, (n, bars, level) in enumerate(SECTIONS, 1):
        out.append(":%s a val:Section ; val:index %d ; val:bars %d ; val:level %g ." % (n, i, bars, level))
    out.append("")
    for i, (n, circuit, level, pan, hp, follows) in enumerate(PARTS, 1):
        f = " ; val:follows :%s" % follows if follows else ""
        out.append(":%s a val:Part ; val:index %d ; val:circuit \"circuits/%s\" ; val:level %g ; val:pan %g ; val:highpass %d%s ." %
                   (n, i, circuit, level, pan, hp, f))
    for i, (n, level, pan, hp) in enumerate(RECORDED, len(PARTS) + 1):
        out.append(":%s a val:Part ; val:index %d ; val:recorded true ; val:level %g ; val:pan %g ; val:highpass %d ." % (n, i, level, pan, hp))
    out.append("")
    out.append(":lead-verb a val:Return ; val:index 1 ; val:source :lead ; val:circuit \"circuits/reverb-return.ttl\" ;\n"
               "    val:level -35 ; val:pan -0.2 ; val:highpass 250 .")
    return "\n".join(out) + "\n"


def main():
    os.makedirs(os.path.join(OUT, "circuits"), exist_ok=True)
    for _, circuit, *_ in PARTS:
        shutil.copyfile(os.path.join(VALIS, "circuits", circuit), os.path.join(OUT, "circuits", circuit))
    shutil.copyfile(os.path.join(VALIS, "circuits", "reverb-return.ttl"), os.path.join(OUT, "circuits", "reverb-return.ttl"))
    with open(os.path.join(OUT, "score.ttl"), "w") as f:
        f.write(turtle_score())
    with open(os.path.join(OUT, "song.ttl"), "w") as f:
        f.write(turtle_song())
    with open(os.path.join(OUT, "voice.txt"), "w") as f:
        f.write(voice_text() + "\n")
    os.makedirs(os.path.join(OUT, "docs"), exist_ok=True)
    with open(os.path.join(OUT, "docs", "lyrics.md"), "w") as f:
        f.write(lyrics_markdown())
    total = sum(b for _, b, _ in SECTIONS)
    print("wrote %s: %d bars, %.1f s at %d bpm" % (OUT, total, total * 4 * 60.0 / TEMPO, TEMPO))


if __name__ == "__main__":
    main()
