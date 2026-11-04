# scripts/asturias-industrial/make.py
#
# "Asturias (Industrial)": an industrial dubstep take on Isaac Albeniz's "Asturias (Leyenda)".
# E minor, 140 bpm, 64 bars (~2:17). The Asturias arpeggio survives as a fast lead and a
# top-note line over a wobble bass, an industrial kick, a 909 kit, metal percussion and a
# nylon guitar that quotes the theme. The material is new; the harmony nods to the original.
#
#   python3 make.py            write circuits/, score.ttl and song.ttl under artifacts/asturias-industrial/
import os, shutil, sys
VALIS = os.environ.get("VALIS", "/chalet/github/valis")
sys.path.insert(0, os.path.join(VALIS, "scripts", "song"))
import midiw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "asturias-industrial"))

TEMPO = 140
TITLE = "Asturias Industrial"

SECTIONS = [  # name, bars, section level dB
    ("intro",  8, -4.0),
    ("build",  8, -2.0),
    ("drop1", 16,  0.0),
    ("break",  8,  2.0),
    ("build2", 8, -2.0),
    ("drop2",  8,  1.0),
    ("outro",  8, -3.0),
]
BARS = dict((n, b) for n, b, _ in SECTIONS)

# Parts: name, circuit, level dB (playing rms), pan, highpass Hz.
PARTS = [
    ("kick",   "nursery-humpty-kick.ttl", -17,  0.00,  30),
    ("kit",    "909.ttl",                  -28,  0.00, 130),
    ("bass",   "halloween-bass.ttl",       -21,  0.00,  30),
    ("lead",   "fuzz-lead.ttl",            -18,  0.05, 260),
    ("arp",    "sh101.ttl",                -24,  0.25, 500),
    ("guitar", "nylon-guitar.ttl",         -24, -0.10, 220),
    ("metal",  "metal-clang.ttl",          -28,  0.30, 400),
    ("riser",  "nursery-wind-up-riser.ttl",-28,  0.00, 300),
]

RETURNS = [
    ("lead-echo", "lead", "dub-delay.ttl", -28, 0.40, 600),
    ("guitar-verb", "guitar", "reverb-return.ttl", -28, -0.40, 250),
]

def main():
    os.makedirs(os.path.join(OUT, "circuits"), exist_ok=True)
    for src in ["nursery-humpty-kick.ttl", "909.ttl", "halloween-bass.ttl", "fuzz-lead.ttl",
                "sh101.ttl", "nylon-guitar.ttl", "metal-clang.ttl", "nursery-wind-up-riser.ttl",
                "reverb-return.ttl", "dub-delay.ttl"]:
        shutil.copyfile(os.path.join(VALIS, "circuits", src), os.path.join(OUT, "circuits", src))
    # dub-delay is timed for 85 bpm; leave as is (close enough for an echo).
    with open(os.path.join(OUT, "song.ttl"), "w") as f:
        f.write(turtle_song())
    with open(os.path.join(OUT, "score.ttl"), "w") as f:
        f.write(turtle_score())
    # The arp is a real arpeggio: cycle through the chord's tones over 16 sixteenths per bar.
    os.makedirs(os.path.join(OUT, "midi"), exist_ok=True)
    # chord tones per chord name (lowest first), from score.ttl
    chord_tones = {"Em": [52, 55, 59], "B7": [59, 62, 66], "C": [48, 52, 55]}
    progression = ["Em", "B7", "Em", "C", "B7", "Em"]
    arp_notes = []
    for bar in range(64):
        ch = progression[bar % 6]
        tones = chord_tones[ch]
        # arpeggio figure: up then down through the tones, two octaves
        fig = [tones[0], tones[1], tones[2], tones[1]]
        for step in range(16):
            pitch = fig[step % len(fig)] + (12 if step >= 8 else 0)
            arp_notes.append((bar * 4.0 + step * 0.25, 0.2, pitch, 78))
    midiw.write(os.path.join(OUT, "midi", "arp.mid"), arp_notes, TEMPO)
    # riser held notes
    riser_notes = []
    for start_bar in (9, 41):
        riser_notes.append(((start_bar - 1) * 4.0, 8 * 4.0, 60, 100))
    midiw.write(os.path.join(OUT, "midi", "riser.mid"), riser_notes, TEMPO)
    total = sum(b for _, b, _ in SECTIONS)
    print("wrote %s: %d bars, %.1f s at %d bpm" % (OUT, total, total * 4 * 60.0 / TEMPO, TEMPO))


def turtle_song():
    out = []
    out.append('# song.ttl\n#\n# "Asturias Industrial": the layout and the mix as data.\n')
    out.append("@prefix val:  <http://purl.org/stuff/valis/> .")
    out.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    out.append("@prefix :     <urn:valis-artifacts:asturias-industrial#> .")
    out.append("")
    out.append(":song a val:Song ;")
    out.append('    val:title "Asturias Industrial" ;')
    out.append("    val:tempo %d ;" % TEMPO)
    out.append("    val:score \"score.ttl\" ;")
    out.append("    val:loudness -10 ;")
    out.append("    val:tailSeconds 10 ;")
    out.append("    val:fadeSeconds 6 ;")
    out.append("    val:roomAmount 0.05 ;")
    out.append("    val:roomDecay 0.4 ;")
    out.append("    val:roomLowpass 4000 ;")
    out.append("    val:drive 3.0 ;")
    out.append("    val:hasSection " + " , ".join(":" + n for n, _, _ in SECTIONS) + " ;")
    out.append("    val:hasPart " + " , ".join(":" + n for n, _, _, _, _ in PARTS) + " ;")
    out.append("    val:hasReturn " + " , ".join(":" + n for n, _, _, _, _, _ in RETURNS) + " .")
    out.append("")
    for i, (n, b, lvl) in enumerate(SECTIONS, 1):
        out.append(":%s a val:Section ; val:index %d ; val:bars %d ; val:level %g ." % (n, i, b, lvl))
    out.append("")
    for i, (n, circuit, level, pan, hp) in enumerate(PARTS, 1):
        out.append(":%s a val:Part ; val:index %d ; val:circuit \"circuits/%s\" ; val:level %g ; val:pan %g ; val:highpass %d ." %
                   (n, i, circuit, level, pan, hp))
    out.append("")
    for i, (n, source, circuit, level, pan, hp) in enumerate(RETURNS, 1):
        out.append(":%s a val:Return ; val:index %d ; val:source :%s ; val:circuit \"circuits/%s\" ;\n"
                   "    val:level %g ; val:pan %g ; val:highpass %d ." % (n, i, source, circuit, level, pan, hp))
    return "\n".join(out) + "\n"


def turtle_score():
    out = []
    out.append("# score.ttl\n#\n# Asturias Industrial: chords, patterns, plays, feels.\n")
    out.append("@prefix val:  <http://purl.org/stuff/valis/> .")
    out.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    out.append("@prefix :     <urn:valis-artifacts:asturias-industrial#> .")
    out.append("")
    out.append(":score a val:Score ; val:seed 1971 ;")
    out.append('    val:progression "Em B7 Em C B7 Em" ;')
    out.append("    val:barsPerChord 1 ;")
    out.append("    val:hasChord :Em , :B7 , :C ;")
    out.append("    val:hasPattern :kick-pat , :kit-pat , :bass-pat , :arp-pat , :lead-pat , :metal-pat , :guitar-pat , :riser-pat ;")
    out.append("    val:hasFeel :kit-feel , :metal-feel ;")
    out.append("")
    # Chords: root, tones (lowest first)
    out.append(":Em a val:Chord ; val:root 40 ; val:tones \"52 55 59\" .")   # E2, E3 G3 B3
    out.append(":B7 a val:Chord ; val:root 47 ; val:tones \"59 62 66\" .")   # B2, B3 D#4 F#4
    out.append(":C  a val:Chord ; val:root 36 ; val:tones \"48 52 55\" .")   # C2, C3 E3 G3
    out.append("")
    # Patterns
    out.append(":kick-pat a val:Pattern ; val:hasLane [ val:key 36 ; val:steps \"X...|....|X...|....\" ] .")
    out.append(":kit-pat a val:Pattern ; val:hasLane")
    out.append("    [ val:key 36 ; val:steps \"X...|....|X...|....\" ; val:velocity 75 ; val:accent 10 ] ,")
    out.append("    [ val:key 38 ; val:steps \"....|X...|....|X...\" ; val:velocity 75 ; val:accent 10 ] ,")
    out.append("    [ val:key 42 ; val:steps \"x.x.|x.x.|x.x.|x.x.\" ; val:velocity 55 ] .")
    out.append(":bass-pat a val:Pattern ; val:hasLane [ val:voice \"root\" ; val:steps \"X...|....|....|....\" ; val:length 3 ; val:gate 0.9 ] .")
    out.append(":arp-pat a val:Pattern ; val:hasLane [ val:voice \"top\" ; val:steps \"xxxx|xxxx|xxxx|xxxx\" ; val:velocity 78 ; val:length 1 ] .")
    out.append(":lead-pat a val:Pattern ; val:hasLane [ val:voice \"top\" ; val:steps \"x...|....|x...|....\" ; val:velocity 100 ; val:length 3 ; val:gate 0.9 ] .")
    out.append(":metal-pat a val:Pattern ; val:hasLane [ val:key 60 ; val:steps \"....|....|....|x...\" ; val:velocity 100 ] .")
    out.append(":guitar-pat a val:Pattern ; val:hasLane [ val:voice \"chord\" ; val:steps \"x...|....|....|....\" ; val:octave 1 ; val:length 3 ; val:gate 0.9 ] .")
    out.append(":riser-pat a val:Pattern ; val:bars 8 ; val:hasLane [ val:key 60 ; val:steps \"" + "x" + "."*127 + "\" ] .")
    out.append("")
    out.append(":kit-feel a val:Feel ; val:part \"kit\" ; val:timing 3 ; val:velocity 4 ; val:swing 0.54 .")
    out.append(":metal-feel a val:Feel ; val:part \"metal\" ; val:timing 8 ; val:velocity 6 .")
    out.append("")
    # Plays: which part plays which pattern in which section
    play_ids = []
    # helper
    def play(part, section, pattern, first=1, last=None):
        last = last or BARS[section]
        pid = "p-%s-%s" % (part, section)
        play_ids.append(":" + pid)
        return ':%s a val:Play ; val:section "%s" ; val:part "%s" ; val:pattern :%s ; val:fromBar %d ; val:toBar %d .' % (pid, section, part, pattern, first, last)
    plays = []
    plays.append(play("kick", "intro", "kick-pat"))
    plays.append(play("lead", "intro", "lead-pat"))
    plays.append(play("kick", "build", "kick-pat"))
    plays.append(play("metal", "build", "metal-pat"))
    plays.append(play("kick", "drop1", "kick-pat"))
    plays.append(play("kit", "drop1", "kit-pat"))
    plays.append(play("bass", "drop1", "bass-pat"))
    plays.append(play("lead", "drop1", "lead-pat"))
    plays.append(play("metal", "drop1", "metal-pat"))
    plays.append(play("guitar", "break", "guitar-pat"))
    plays.append(play("kick", "build2", "kick-pat"))
    plays.append(play("metal", "build2", "metal-pat"))
    plays.append(play("kick", "drop2", "kick-pat"))
    plays.append(play("kit", "drop2", "kit-pat"))
    plays.append(play("bass", "drop2", "bass-pat"))
    plays.append(play("lead", "drop2", "lead-pat"))
    plays.append(play("guitar", "outro", "guitar-pat"))
    out.append("\n".join(plays))
    # Insert hasPlay into the score header (appended here because play_ids is built above).
    for i, line in enumerate(out):
        if line.startswith("    val:hasFeel"):
            out.insert(i + 1, "    val:hasPlay " + " , ".join(play_ids) + " .")
            break
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()
