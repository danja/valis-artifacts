# scripts/autumn-leaves/track.py
#
# "Autumn Leaves" as acid rock: an original arrangement of the chord changes of the standard, played by
# the circuits in the Valis repository (examples/dmx.ttl, psych-bass.ttl, tonewheel-organ.ttl,
# leslie.ttl, horn-section.ttl, fuzz-lead.ttl). The reference file, sources/autumn-leaves/Autumn-Leaves.mid,
# supplied the key (G minor) and the cycle of chords; the call lines are new and do not use its melody.
#
#   python3 track.py score    write one MIDI file per part to artifacts/autumn-leaves/midi/
#   python3 track.py render   render every part to artifacts/autumn-leaves/wavs/ (a few minutes)
#   python3 track.py mix      mix the stems to artifacts/autumn-leaves/mixes/autumn-leaves.wav
#   python3 track.py          all three
#
# G minor, 112 bpm, 144 bars (about 5:08). Two bars to a chord, sixteen bars to the cycle:
# Cm7 F7 Bbmaj7 Ebmaj7 Am7b5 D7 Gm Gm.
import os, sys, random, subprocess
from concurrent.futures import ThreadPoolExecutor

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "autumn-leaves"))
MIDI, WAVS, MIXES = (os.path.join(OUTDIR, d) for d in ("midi", "wavs", "mixes"))
RENDER = os.path.join(VALIS, "build", "valis_render_artefacts", "Debug", "valis_render")
sys.path.insert(0, os.path.join(VALIS, "scripts", "halloween"))
import midiw

BPM = 112
STEP = 0.25                      # a sixteenth, in beats
SWING = 0.53                     # the second sixteenth of each pair, drums only
SECTIONS = [("intro", 8), ("verse", 16), ("call", 16), ("jam", 32), ("break", 8),
            ("return", 32), ("climax", 16), ("outro", 16)]
BARS = sum(n for _, n in SECTIONS)
SECONDS = BARS * 4 * 60 / BPM + 8
DRUMS = ("kick", "drums", "perc")
PARTS = ["kick", "drums", "perc", "bass", "organ", "horns", "lead"]

# Cm7 F7 Bbmaj7 Ebmaj7 Am7b5 D7 Gm Gm, two bars each
ROOTS = [36, 41, 34, 39, 33, 38, 31, 31]
ORGAN = [(55, 58, 60, 63), (53, 57, 60, 63), (53, 57, 58, 62), (55, 58, 62, 63),
         (55, 57, 60, 63), (54, 57, 60, 62), (55, 58, 62, 67), (55, 58, 62, 67)]
# The call lines, (beat, length in beats, note), played in the first bar of each chord; the second bar is left open.
CALLS = [[(0, .75, 70), (.75, .25, 72), (1, 1.5, 75)],
         [(0, .5, 72), (.5, .5, 69), (1, 1, 72), (2, 1.5, 77)],
         [(0, 1, 74), (1, .5, 72), (1.5, .5, 70), (2, 2, 74)],
         [(0, .5, 75), (.5, .5, 74), (1, 1.5, 70), (2.5, 1.5, 67)],
         [(0, 1, 72), (1, .5, 75), (1.5, .5, 72), (2, 2, 69)],
         [(0, .5, 66), (.5, .5, 69), (1, .5, 72), (1.5, .5, 74), (2, 2, 78)],
         [(0, 1.5, 74), (1.5, .5, 70), (2, 2, 67)],
         [(0, .75, 67), (.75, .75, 70), (1.5, .5, 74), (2, 2, 79)]]

K_MAIN = {0: 120, 7: 66, 8: 108, 10: 84}
K_PUSH = {0: 120, 7: 66, 8: 108, 10: 84, 15: 70}


def locate(bar):
    start = 0
    for name, n in SECTIONS:
        if bar < start + n:
            return name, bar - start, n
        start += n


def leslie_fast(sec, i):
    return sec == "climax" or sec == "jam" or (sec == "return" and i >= 16)


def build():
    rnd = random.Random(1967)
    perf = {p: [] for p in PARTS}
    fast = []                                         # bars with the rotating speaker fast
    gate = {"bass": 0.8, "horns": 1.0, "lead": 1.0, "organ": 0.85}

    def add(part, bar, step, length_steps, note, vel):
        length = length_steps * STEP * gate.get(part, 1.0)
        start = (bar * 16 + step) * STEP
        if part in DRUMS and step % 2 == 1:
            start += (SWING - 0.5) * 2 * STEP
        perf[part].append((start, length, note, int(vel)))

    def beat(part, bar, b, length, note, vel):
        perf[part].append(((bar * 4) + b, length - 0.08, note, int(vel)))

    organ_runs = []
    for bar in range(BARS):
        sec, i, n = locate(bar)
        c = (bar // 2) % 8
        root = ROOTS[c]
        first = bar % 2 == 0
        playing = sec not in ("intro", "break", "outro")
        fill = i % 8 == 7 and sec not in ("intro", "break", "outro")

        # ---- kick: a slow engine with a hole where the second beat would be
        if sec in ("intro", "verse", "call", "jam", "return", "climax") or (sec == "outro" and i < 8):
            if sec == "intro" and i < 4:
                pass
            else:
                pat = K_PUSH if (i % 4 == 3 and sec != "intro") else K_MAIN
                for st, v in pat.items():
                    add("kick", bar, st, 1, 36 if v > 100 else 35, v)

        # ---- the kit: hats on eighths, the snare on two and four, an open hat before the turn
        if sec != "break" and not (sec == "outro" and i >= 8) and not (sec == "intro" and i < 2):
            for st in range(0, 16, 2):
                add("drums", bar, st, 1, 42, (78 if st % 4 == 0 else 54) + rnd.randint(-5, 5))
            if playing or (sec == "outro" and i < 8):
                for st in (4, 12):
                    add("drums", bar, st, 1, 38, 108 if sec in ("jam", "climax") else 96)
                if i % 2 == 1:
                    add("drums", bar, 14, 2, 46, 70)
                if rnd.random() < 0.3:
                    add("drums", bar, 15, 1, 38, 38)
        if fill and sec in ("verse", "call", "jam", "return", "climax"):
            for st, tom in zip((8, 10, 12, 13, 14, 15), (48, 48, 47, 47, 45, 45)):
                add("drums", bar, st, 1, tom, 80 + (st - 8) * 4)

        # ---- percussion: a shaker through the song, a tambourine on the offbeats of the loud parts
        if sec not in ("break",) and not (sec == "outro" and i >= 12) and not (sec == "intro" and i < 4):
            for st in range(16):
                add("perc", bar, st, 1, 69, 34 + (14 if st % 4 == 2 else 0) + rnd.randint(0, 8))
        if sec in ("jam", "return", "climax"):
            for st in (2, 6, 10, 14):
                add("perc", bar, st, 1, 54, 62)
        if sec == "break" and i % 2 == 0:
            for k in range(3):
                perf["perc"].append(((bar * 4 + 3 + k / 3.0), 0.12, 37, 60 + k * 6))

        # ---- the bass: pounding eighths on the root, an octave leap, a chromatic step into the next chord
        bass_on = sec in ("verse", "call", "jam", "return", "climax") or (sec == "outro" and i < 8)
        if bass_on:
            nxt = ROOTS[((bar // 2) + 1) % 8]
            for st in range(0, 16, 2):
                note = root
                vel = 118 if st % 8 == 0 else 96
                if st in (6, 14) and not first:
                    note = root + 12
                if not first and st == 14:
                    note = nxt + (1 if nxt < root else -1) if nxt != root else root
                add("bass", bar, st, 2, note, vel)

        # ---- organ: held chords in the verse and the break, a chugging comp in the jam, a drone at the ends
        if sec in ("intro", "outro"):
            organ_runs.append((bar, ((43, 50, 55) if (sec == "intro") else (43, 50, 58)), 4.0, 70))
        elif sec == "break":
            organ_runs.append((bar, ORGAN[c], 4.0, 74))
        elif sec in ("verse", "call"):
            organ_runs.append((bar, ORGAN[c], 4.0, 80))
        else:
            for st, ln in ((0, 3), (3, 3), (6, 4), (10, 3), (13, 3)):
                for note in ORGAN[c]:
                    add("organ", bar, st, ln, note, 84 if st in (0, 6) else 72)

        # ---- horns: stabs on the "and" of two and of four
        stab = (sec in ("call", "climax")) or (sec in ("jam", "return") and first) or (sec == "return" and i >= 16)
        if stab:
            chord = [x + 12 for x in ORGAN[c]][1:] + [root + 12]
            for st in ((6, 14) if sec in ("climax",) or not first else (6,)):
                for note in chord:
                    add("horns", bar, st, 2, note, 100)

        # ---- the lead: call lines in the first bar of each chord, the rest left for a guitar
        lead_on = sec in ("call", "climax", "return") or (sec == "jam" and i < 16)
        if lead_on and first:
            lift = 12 if (sec == "climax" or (sec == "return" and i >= 16)) else 0
            for b, ln, note in CALLS[c]:
                beat("lead", bar, b, ln, note + lift, 104)
        if sec == "climax" and not first:
            for b, ln, note in CALLS[c]:
                beat("lead", bar, b, ln, note + 12 - 5, 96)
        if sec == "break" and i % 4 == 0:
            beat("lead", bar, 0, 3.0, 67, 90)               # one long note, left to ring in the echo

        if leslie_fast(sec, i):
            fast.append(bar)

    for bar, chord, length, vel in organ_runs:
        for note in chord:
            perf["organ"].append((bar * 4.0, length * 0.96, note, vel))

    # the rotating speaker's switch: note 60 held through each run of fast bars
    runs = []
    for bar in fast:
        if runs and runs[-1][1] == bar:
            runs[-1][1] = bar + 1
        else:
            runs.append([bar, bar + 1])
    perf["leslie-speed"] = [(a * 4.0, (b - a) * 4.0, 60, 100) for a, b in runs]
    return perf


def score():
    os.makedirs(MIDI, exist_ok=True)
    perf = build()
    for part, notes in perf.items():
        midiw.write("%s/%s.mid" % (MIDI, part), sorted(notes), BPM)
        print("%-12s %5d notes" % (part, len(notes)))


JOBS = [("kick", "examples/dmx.ttl"), ("drums", "examples/dmx.ttl"), ("perc", "examples/dmx.ttl"),
        ("bass", "examples/psych-bass.ttl"), ("organ", "examples/tonewheel-organ.ttl"),
        ("horns", "examples/horn-section.ttl"), ("lead", "examples/fuzz-lead.ttl")]


def run(cmd):
    r = subprocess.run(cmd, cwd=VALIS, capture_output=True, text=True)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]


def render_one(job):
    part, circuit = job
    print(part, run([RENDER, circuit, "--midi", "%s/%s.mid" % (MIDI, part), "--tempo", str(BPM), "--rolling",
                     "--seconds", "%.1f" % SECONDS, "-o", "%s/%s.wav" % (WAVS, part)]), flush=True)


def render():
    os.makedirs(WAVS, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(render_one, JOBS))
    # the organ goes through the rotating speaker, whose speed is a MIDI note
    print("organ-leslie", run([RENDER, "examples/leslie.ttl", "-i", WAVS + "/organ.wav", "--midi", MIDI + "/leslie-speed.mid",
                               "--tempo", str(BPM), "--rolling", "--seconds", "%.1f" % SECONDS, "-o", WAVS + "/organ-leslie.wav"]))


# part: (level in dB of the stem's playing rms, pan -1..1, high-pass Hz or 0). The percussion follows the kit.
FOLLOWS = {"perc"}
LEVELS = {"kick": (-19.0, 0.0, 0), "drums": (-23.0, 0.0, 0), "perc": (-6.0, 0.15, 0),
          "bass": (-20.0, 0.0, 0), "organ-leslie": (-25.0, -0.3, 110),
          "horns": (-25.0, 0.3, 150), "lead": (-25.0, 0.1, 150)}


def playing_rms_db(x, rate):
    import numpy as np
    w = rate // 10
    n = len(x) // w
    e = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(axis=1))
    e = e[e > 1.0e-3]
    return 20 * np.log10(np.sqrt((e ** 2).mean()) + 1.0e-12) if len(e) else -120.0


def mix():
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import butter, sosfilt
    os.makedirs(MIXES, exist_ok=True)
    total = None
    kit_gain = 1.0
    for part, (level, pan, hp) in LEVELS.items():
        path = "%s/%s.wav" % (WAVS, part)
        if not os.path.exists(path):
            print("missing", path)
            continue
        rate, d = wavfile.read(path)
        d = d.astype(np.float64) / (2.0 ** 31 if d.dtype == np.int32 else 32768.0 if d.dtype == np.int16 else 1.0)
        mono = d if d.ndim == 1 else d.mean(axis=1)
        if hp:
            mono = sosfilt(butter(2, hp, "highpass", fs=rate, output="sos"), mono)
        if part in FOLLOWS:
            g = 10 ** (level / 20) * kit_gain
        else:
            g = 10 ** ((level - playing_rms_db(mono, rate)) / 20)
            if part == "drums":
                kit_gain = g
        theta = (pan + 1) * np.pi / 4
        stereo = np.stack([mono * np.cos(theta), mono * np.sin(theta)], axis=1) * g * np.sqrt(2)
        if total is None:
            total = np.zeros((max(len(stereo), int(SECONDS * rate)), 2))
        total[:len(stereo)] += stereo
    end = int((BARS * 4 * 60 / BPM + 4) * rate)             # the song, and the last chord's tail
    total = total[:end]
    total[-3 * rate:] *= np.linspace(1.0, 0.0, 3 * rate)[:, None]
    mx = np.tanh(total * 1.8) / 1.8
    mx = mx / np.max(np.abs(mx)) * 10 ** (-1.0 / 20)
    wavfile.write("%s/autumn-leaves.wav" % MIXES, rate, (mx * 8388607).astype(np.int32) << 8)
    print("mixed: %.1f s, peak %.3f rms %.3f dB" % (len(mx) / rate, np.max(np.abs(mx)), 20 * np.log10(np.sqrt(np.mean(mx ** 2)))))


if __name__ == "__main__":
    steps = [a for a in sys.argv[1:] if not a.startswith("--")] or ["score", "render", "mix"]
    for s in steps:
        {"score": score, "render": render, "mix": mix}[s]()
