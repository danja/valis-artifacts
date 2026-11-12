#!/usr/bin/env python3
"""Write and render Danube Ciao, a 3/4 Blue Danube / Bella Ciao arrangement."""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VALIS = os.environ.get("VALIS", os.path.normpath(os.path.join(REPO, "..", "valis")))
sys.path.insert(0, os.path.join(VALIS, "scripts", "song"))
import midiw
import songlib

OUT = os.path.join(REPO, "artifacts", "danube-ciao")
TITLE = "Danube Ciao"
TEMPO = 126
SECTIONS = [
    ("intro", 4, -2.0),
    ("bella-ciao", 8, -0.5),
    ("blue-danube", 8, 0.0),
    ("crossing", 8, 0.0),
    ("break", 4, -2.0),
    ("finale", 12, 1.0),
    ("coda", 4, -2.0),
]
SECTION_START = {}
_bar = 0
for _name, _bars, _level in SECTIONS:
    SECTION_START[_name] = _bar
    _bar += _bars
BARS = _bar

PARTS = [
    ("blue", "violins.ttl", -22.0, -0.15, 150),
    ("ciao", "clarinet.ttl", -23.0, 0.15, 180),
    ("chords", "nylon-guitar.ttl", -25.0, 0.0, 120),
    ("bass", "dub-bass.ttl", -23.0, 0.0, 35),
    ("kick", "808-bd.ttl", -28.0, 0.0, 35),
    ("shakers", "latin-perc.ttl", -34.0, 0.25, 500),
]
RETURNS = [("blue-hall", "blue", "reverb-return.ttl", -29.0, -0.4)]
CIRCUITS = sorted({circuit for _, circuit, *_ in PARTS} |
                  {circuit for _, _, circuit, *_ in RETURNS})

# The opening triadic figure and a newly shaped answer/continuation from the
# public-domain waltz melody, in D major.
BLUE = [
    [(0, 1, 66), (1, 1, 69), (2, 1, 74)],
    [(0, 3, 74)],
    [(0, 1, 66), (1, 1, 69), (2, 1, 74)],
    [(0, 3, 74)],
    [(0, 1, 69), (1, 1, 73), (2, 1, 76)],
    [(0, 1, 79), (1, 1, 78), (2, 1, 76)],
    [(0, 1, 74), (1, 1, 73), (2, 1, 71)],
    [(0, 1.5, 69), (1.5, 1.5, 74)],
]

# Bella Ciao's familiar refrain, transposed up a major third from G minor to
# B minor so it sits naturally against the waltz's D-major palette.
CIAO = [
    [(0, 1, 66), (1, 1, 71), (2, 1, 71)],
    [(0, 1, 71), (1, 1, 74), (2, 1, 73)],
    [(0, 1, 71), (1, 1, 66), (2, 1, 66)],
    [(0, 3, 71)],
    [(0, 1, 66), (1, 1, 71), (2, 1, 71)],
    [(0, 1, 71), (1, 1, 74), (2, 1, 73)],
    [(0, 1, 71), (1, 1, 66), (2, 1, 66)],
    [(0, 3, 71)],
]

CHORDS_BLUE = ["D", "D", "A", "A", "D", "G", "A", "D"]
CHORDS_CIAO = ["Bm", "Bm", "F#7", "F#7", "G", "D", "F#7", "Bm"]
VOICING = {
    "D": (38, (62, 66, 69)),
    "A": (45, (61, 64, 69)),
    "Bm": (35, (59, 62, 66)),
    "F#7": (42, (58, 61, 64, 66)),
    "G": (43, (59, 62, 67)),
}


def write_circuits():
    os.makedirs(os.path.join(OUT, "circuits"), exist_ok=True)
    for name in CIRCUITS:
        shutil.copyfile(os.path.join(VALIS, "circuits", name),
                        os.path.join(OUT, "circuits", name))


def write_song():
    lines = [
        "# song.ttl",
        "#",
        "# Danube Ciao: a D-major waltz carrying Bella Ciao in B minor.",
        "",
        "@prefix val: <http://purl.org/stuff/valis/> .",
        "@prefix : <urn:valis-artifacts:danube-ciao#> .",
        "",
        ":song a val:Song ;",
        '    val:title "Danube Ciao" ;',
        f"    val:tempo {TEMPO} ;",
        "    val:beatsPerBar 3 ;",
        "    val:loudness -14 ;",
        "    val:tailSeconds 8 ;",
        "    val:fadeSeconds 4 ;",
        "    val:roomAmount 0.14 ;",
        "    val:roomDecay 0.65 ;",
        "    val:roomLowpass 6500 ;",
        "    val:drive 1.15 ;",
        "    val:hasSection " + " , ".join(f":{name}" for name, *_ in SECTIONS) + " ;",
        "    val:hasPart " + " , ".join(f":{name}" for name, *_ in PARTS) + " ;",
        "    val:hasReturn " + " , ".join(f":{name}" for name, *_ in RETURNS) + " .",
        "",
    ]
    for i, (name, bars, level) in enumerate(SECTIONS, 1):
        lines.append(f":{name} a val:Section ; val:index {i} ; val:bars {bars} ; val:level {level:g} .")
    lines.append("")
    for i, (name, circuit, level, pan, highpass) in enumerate(PARTS, 1):
        lines.append(
            f':{name} a val:Part ; val:index {i} ; val:circuit "circuits/{circuit}" ; '
            f"val:level {level:g} ; val:pan {pan:g} ; val:highpass {highpass} ."
        )
    lines.append("")
    for i, (name, source, circuit, level, pan) in enumerate(RETURNS, 1):
        lines.append(
            f':{name} a val:Return ; val:index {i} ; val:source :{source} ; '
            f'val:circuit "circuits/{circuit}" ; val:level {level:g} ; val:pan {pan:g} .'
        )
    with open(os.path.join(OUT, "song.ttl"), "w") as f:
        f.write("\n".join(lines) + "\n")


def write_score():
    notes = {name: [] for name, *_ in PARTS}

    def put(part, beat, length, pitch, velocity):
        notes[part].append((beat, length * 0.92, pitch, velocity))

    def melody(part, first_bar, pattern, count, velocity, transpose=0):
        for offset in range(count):
            events = pattern[offset % len(pattern)]
            for beat, length, pitch in events:
                put(part, (first_bar + offset) * 3 + beat, length, pitch + transpose, velocity)

    def chord_bar(bar, chord_name, velocity=58):
        root, tones = VOICING[chord_name]
        start = bar * 3
        put("bass", start, 1.8, root, 72)
        put("kick", start, 0.8, 36, 48)
        for beat in (1, 2):
            for i, pitch in enumerate(tones):
                put("chords", start + beat + i * 0.012, 0.78, pitch, velocity - (i * 2))
        for beat in (1, 2):
            put("shakers", start + beat, 0.22, 70, 38 if beat == 1 else 30)

    def accompaniment(first_bar, progression, count):
        for offset in range(count):
            chord_bar(first_bar + offset, progression[offset % len(progression)])

    # Intro: the Danube's rising tonic triad, over a restrained waltz pulse.
    intro = SECTION_START["intro"]
    accompaniment(intro, ["D"], 4)
    melody("blue", intro, BLUE, 4, 68)

    # Bella Ciao takes the lead; its refrain is in B minor.
    ciao = SECTION_START["bella-ciao"]
    accompaniment(ciao, CHORDS_CIAO, 8)
    melody("ciao", ciao, CIAO, 8, 82)

    # The Danube answers in its home key.
    danube = SECTION_START["blue-danube"]
    accompaniment(danube, CHORDS_BLUE, 8)
    melody("blue", danube, BLUE, 8, 82)

    # Trade four-bar phrases, then let both melodies meet in the finale.
    crossing = SECTION_START["crossing"]
    accompaniment(crossing, CHORDS_CIAO, 4)
    accompaniment(crossing + 4, CHORDS_BLUE, 4)
    melody("ciao", crossing, CIAO, 4, 76)
    melody("blue", crossing + 4, BLUE, 4, 78)

    quiet = SECTION_START["break"]
    accompaniment(quiet, ["Bm", "G", "D", "F#7"], 4)
    melody("ciao", quiet, CIAO[4:], 4, 66)

    finale = SECTION_START["finale"]
    accompaniment(finale, CHORDS_BLUE + CHORDS_CIAO[:4], 12)
    melody("blue", finale, BLUE, 12, 88)
    melody("ciao", finale + 4, CIAO, 8, 78)

    coda = SECTION_START["coda"]
    accompaniment(coda, ["G", "A", "D", "D"], 4)
    melody("blue", coda, [[(0, 3, 74)]], 4, 60)

    midi_dir = os.path.join(OUT, "midi")
    os.makedirs(midi_dir, exist_ok=True)
    for part, events in notes.items():
        midiw.write(os.path.join(midi_dir, part + ".mid"), sorted(events), TEMPO)
        print(f"{part:10s} {len(events):4d} notes")


def main():
    actions = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    opts = dict(arg[2:].split("=", 1) for arg in sys.argv[1:] if arg.startswith("--") and "=" in arg)
    actions = actions or ["circuits", "song", "score", "check", "render", "mix"]
    os.makedirs(OUT, exist_ok=True)
    if "circuits" in actions:
        write_circuits()
    if "song" in actions:
        write_song()
    if "score" in actions:
        write_score()
    if "check" in actions or "render" in actions or "mix" in actions:
        song = songlib.load(os.path.join(OUT, "song.ttl"))
    if "check" in actions:
        result = songlib.check(song)
        print("check:", result)
    if "render" in actions:
        songlib.render(song)
    if "mix" in actions:
        songlib.mix(song, opts.get("version", "v1"), arc=True)


if __name__ == "__main__":
    main()
