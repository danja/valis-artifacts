# scripts/interstate-rain/track.py
#
# "Interstate Rain": an original piece in the manner of late-1960s rock with a jazz rhythm section and a storm on the
# soundtrack. It borrows the mood and the instruments of that era, not a tune: E Dorian, a slow loping triplet feel,
# a Rhodes-style electric piano over a soft electric bass, a light kit, one clean guitar into an echo, and a recorded
# rain and thunder. Every note is written here from a seed.
#
#   python3 track.py score    write one MIDI file per part to artifacts/interstate-rain/midi/
#   python3 track.py render   render every part, and the reverb returns, to artifacts/interstate-rain/wavs/
#   python3 track.py mix      mix the stems to artifacts/interstate-rain/mixes/ (--version=vN, --lufs=N, --arc)
#   python3 track.py          all three
#
# The circuits are in artifacts/interstate-rain/circuits/ (the kit is the sampler drum machine, the rain and the
# thunder are val:Sampler too, with CC0 recordings from freesound.org kept in sources/interstate-rain/audio/).
import os, sys, random, subprocess
from concurrent.futures import ThreadPoolExecutor

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "interstate-rain"))
CIRCUITS = os.path.join(OUTDIR, "circuits")
MIDI, WAVS, MIXES = (os.path.join(OUTDIR, d) for d in ("midi", "wavs", "mixes"))
NAME = "interstate-rain"


def newest_source():
    newest = 0.0
    for top in ("src", "include", "vocabs"):
        for root, _, names in os.walk(os.path.join(VALIS, top)):
            for n in names:
                newest = max(newest, os.path.getmtime(os.path.join(root, n)))
    return newest


def pick_renderer():
    """A binary older than the source renders the old code, so a stale one is passed over. VALIS_RENDER names one."""
    if os.environ.get("VALIS_RENDER"):
        return os.environ["VALIS_RENDER"]
    newest = newest_source()
    for d, c in (("build-release", "Release"), ("build", "Debug")):
        p = os.path.join(VALIS, d, "valis_render_artefacts", c, "valis_render")
        if os.path.exists(p):
            if os.path.getmtime(p) >= newest:
                return p
            print("skipping %s: older than the source (rebuild it, or set VALIS_RENDER)" % p, file=sys.stderr)
    sys.exit("no valis_render newer than the source: run cmake --build build")


_renderer = None


def renderer():
    global _renderer
    if _renderer is None:
        _renderer = pick_renderer()
    return _renderer


sys.path.insert(0, os.path.join(VALIS, "scripts", "halloween"))
sys.path.insert(0, os.path.join(VALIS, "scripts", "shot"))
import midiw, lufs

BPM = 100
# (name, bars). 80 bars of 2.4 s: 3:12.
SECTIONS = [("intro", 8), ("verseA", 16), ("verseB", 16), ("bridge", 8), ("solo", 16), ("verseC", 8), ("outro", 8)]
BARS = sum(n for _, n in SECTIONS)
SECONDS = BARS * 4 * 60 / BPM + 10
PARTS = ["bass", "epiano", "guitar", "kit", "rain", "thunder"]

# Chord: (bass root, epiano voicing, the scale to play over it). E Dorian is E F# G A B C# D.
E_DORIAN = [4, 6, 7, 9, 11, 13, 14]            # semitones above C, in the first octave (E=4 ... D=14)
CHORDS = {
    "Em7":    (40, (55, 59, 62, 64), "dorian"),
    "A7":     (45, (55, 61, 64, 66), "dorian"),       # A13: G C# E F#
    "Dmaj7":  (38, (54, 57, 61, 64), "dorian"),
    "Gmaj7":  (43, (54, 59, 62, 67), "dorian"),
    "F#m7b5": (42, (52, 57, 60, 66), "locrian"),
    "B7":     (47, (51, 57, 62, 66), "dorian"),       # D# A D F#: the one chord that leaves the mode
    "Bm7":    (47, (50, 57, 59, 62), "dorian"),
}
VERSE = ["Em7", "Em7", "A7", "A7", "Em7", "Em7", "Dmaj7", "A7"]
BRIDGE = ["Gmaj7", "Gmaj7", "F#m7b5", "B7", "Em7", "Em7", "A7", "A7"]
HARMONY = {"intro": VERSE, "verseA": VERSE, "verseB": VERSE, "bridge": BRIDGE, "solo": VERSE, "verseC": VERSE, "outro": VERSE}

# Which parts play in which section, and how.
PLAN = {
    "intro":  {"epiano": "pad", "kit": "late", "thunder": [(2, 60), (6, 64)]},
    "verseA": {"epiano": "comp", "bass": "walk", "kit": "groove", "thunder": [(9, 62)]},
    "verseB": {"epiano": "comp", "bass": "walk", "kit": "groove", "guitar": "figure"},
    "bridge": {"epiano": "pad", "bass": "held", "kit": "build", "guitar": "figure", "thunder": [(0, 64), (7, 60)]},
    "solo":   {"epiano": "solo", "bass": "walk", "kit": "groove", "guitar": "answer", "thunder": [(7, 62)]},
    "verseC": {"epiano": "comp", "bass": "walk", "kit": "groove", "guitar": "figure"},
    "outro":  {"epiano": "pad", "bass": "held", "kit": "fade", "thunder": [(1, 64), (5, 60)]},
}

# The kit's keys (General MIDI): 36 kick, 38 snare, 42 closed hat, 44 pedal hat, 45 47 48 toms, 49 crash, 51 ride.
T = 1.0 / 3.0       # a triplet eighth, in beats


def locate(bar):
    for name, n in SECTIONS:
        if bar < n:
            return name, bar
        bar -= n
    raise ValueError(bar)


def scale_notes(kind, low, high):
    """Notes of the scale between two MIDI numbers."""
    base = E_DORIAN if kind == "dorian" else [4, 6, 7, 9, 10, 12, 14]   # locrian on F#: F# G A B C D E
    out = []
    for octave in range(-1, 10):
        for s in base:
            n = s + 12 * octave
            if low <= n <= high:
                out.append(n)
    return sorted(set(out))


def build():
    rng = random.Random(1971 % 100)
    parts = {p: [] for p in PARTS}
    solo_motif = None
    bar0 = 0
    for name, n in SECTIONS:
        plan = PLAN[name]
        harmony = HARMONY[name]
        for i in range(n):
            bar = bar0 + i
            b = bar * 4.0
            chord = harmony[i % 8]
            nxt = harmony[(i + 1) % 8]
            root, voicing, mode = CHORDS[chord]
            next_root = CHORDS[nxt][0]
            phrase_end = i % 4 == 3
            section_end = i == n - 1

            # -- electric piano
            style = plan.get("epiano")
            if style == "pad":
                parts["epiano"] += [(b, 3.7, p, 58 + rng.randint(-4, 4)) for p in voicing]
            elif style == "comp":
                # the chord on the one, a push before three, and the top note ringing on
                parts["epiano"] += [(b, 1.45, p, 66 + rng.randint(-5, 5)) for p in voicing]
                parts["epiano"] += [(b + 1.67, 0.6, p, 58 + rng.randint(-5, 5)) for p in voicing[1:]]
                if i % 2 == 1:
                    parts["epiano"] += [(b + 3.0 + T, 0.8, p, 54 + rng.randint(-4, 4)) for p in voicing[:3]]
                if phrase_end:
                    # a rippling run through the voicing and up the scale into the next bar
                    run = scale_notes(mode, voicing[0], voicing[-1] + 9)[-6:]
                    for k, p in enumerate(run):
                        parts["epiano"].append((b + 3.0 + k * (1.0 / 6.0), 0.2, p, 52 + 3 * k + rng.randint(-3, 3)))
            elif style == "solo":
                if i % 4 == 0 or solo_motif is None:
                    solo_motif = [rng.choice((-2, -1, 1, 2, 3)) for _ in range(5)]
                low, high = 64, 88
                notes = scale_notes(mode, low, high)
                pos = min(range(len(notes)), key=lambda k: abs(notes[k] - voicing[2] - 12))
                # two rhythms for the bar, alternated: triplet runs and spaced eighths
                if (i + (1 if i >= 8 else 0)) % 2 == 0:
                    times = [0.0, 1.0, 1.0 + T, 1.0 + 2 * T, 2.0, 2.0 + T * 2, 3.0, 3.0 + T]
                else:
                    times = [0.5, 1.5, 1.5 + T, 2.5, 3.0, 3.0 + T, 3.0 + 2 * T]
                rest = i % 4 == 3 and rng.random() < 0.6
                for k, t in enumerate(times):
                    if rest and t > 1.9:
                        continue
                    pos = max(0, min(len(notes) - 1, pos + solo_motif[k % len(solo_motif)] * (1 if k < 4 else -1)))
                    length = (times[k + 1] - t) * 0.8 if k + 1 < len(times) else 0.8
                    parts["epiano"].append((b + t, max(0.1, length), notes[pos], 70 + (10 if t == 0.0 else 0) + rng.randint(-6, 6)))
                # the comping continues underneath, softly
                parts["epiano"] += [(b, 1.2, p, 40) for p in voicing[:3]]

            # -- bass
            style = plan.get("bass")
            if style == "walk":
                third = root + (3 if chord in ("Em7", "Bm7", "F#m7b5") else 4 if chord != "A7" else 4)
                approach = next_root + (-1 if (bar % 2 == 0) else 1)
                parts["bass"] += [(b, 1.45, root, 100), (b + 1.67, 0.5, root, 84),
                                  (b + 2.0, 0.9, root + 7, 92), (b + 3.0, 0.6, third if i % 2 else root + 12, 84),
                                  (b + 3.0 + 2 * T, 0.3, approach, 80)]
            elif style == "held":
                parts["bass"].append((b, 3.6, root, 92))

            # -- guitar: sparse high figures that the echo carries over the bar
            style = plan.get("guitar")
            if style == "figure" and i % 2 == 1:
                tones = [p + 12 for p in (voicing[1], voicing[2], voicing[3])]
                pitches = [rng.choice(tones) for _ in range(2)]
                parts["guitar"] += [(b + 1.0 + T, 0.5, pitches[0], 84), (b + 2.0 + 2 * T, 0.8, pitches[1], 78)]
            elif style == "answer" and i % 4 == 2:
                tones = scale_notes(mode, 71, 83)
                a = rng.randrange(len(tones) - 3)
                parts["guitar"] += [(b + 0.5, 0.4, tones[a + 2], 88), (b + 1.0 + T, 0.4, tones[a + 1], 80),
                                    (b + 2.0, 1.2, tones[a], 82)]

            # -- kit: a light loping feel. ride in triplets (ding, ding-a-ding), a chick on two and four,
            # soft ghost snare, a kick that mostly stays out of the way
            style = plan.get("kit")
            if style == "late" and i >= 4:
                parts["kit"] += [(b + 1.0, 0.1, 44, 46), (b + 3.0, 0.1, 44, 52)]
            elif style in ("groove", "build", "fade"):
                soft = 0.7 if style == "fade" else 1.0
                ride = [0.0, 1.0, 1.0 + 2 * T, 2.0, 3.0, 3.0 + 2 * T]
                for t in ride:
                    parts["kit"].append((b + t, 0.2, 51, int((70 if t % 1.0 == 0.0 else 52) * soft) + rng.randint(-5, 5)))
                parts["kit"] += [(b + 1.0, 0.1, 44, int(60 * soft)), (b + 3.0, 0.1, 44, int(60 * soft))]
                if style != "fade" or i % 2 == 0:
                    parts["kit"].append((b, 0.2, 36, int(66 * soft) + rng.randint(-5, 5)))
                if i % 2 == 1 and style != "fade":
                    parts["kit"].append((b + 2.0 + 2 * T, 0.2, 36, 54))
                if style == "groove":
                    parts["kit"].append((b + 3.0 + 2 * T, 0.1, 38, 34 + rng.randint(0, 8)))      # a ghost on the last triplet
                    if i % 2 == 0:
                        parts["kit"].append((b + 1.0, 0.1, 38, 46))                               # the backbeat, very soft
                    if i % 4 == 2:
                        parts["kit"].append((b + 3.0, 0.1, 38, 54))
                if style == "build":
                    for k in range(4):
                        parts["kit"].append((b + k, 0.1, 42, 46 + 4 * k))
                    if i % 4 == 3:
                        parts["kit"] += [(b + 3.0 + k * T, 0.1, t, 56 + 5 * k) for k, t in enumerate((48, 47, 45))]
            if style in ("groove", "build") and phrase_end and i % 8 == 7:
                # a fill into the next section: toms falling in triplets
                parts["kit"] += [(b + 2.0 + k * T, 0.1, t, 58 + 3 * k) for k, t in enumerate((48, 48, 47, 47, 45, 45))]
            if i == 0 and name not in ("intro",):
                parts["kit"].append((b, 0.3, 49, 62))                                               # a crash at the head of a section

            # -- thunder: at the bars the plan names
            for at, key in plan.get("thunder", []):
                if i == at:
                    parts["thunder"].append((b + 0.5, 0.5, key, 100))
        bar0 += n

    # The rain is one held note across the whole piece.
    parts["rain"].append((0.0, BARS * 4.0 - 0.5, 60, 100))

    # A little timing and level variation per part, from a fixed seed, never starting before 0.
    for part, notes in parts.items():
        if part in ("rain", "thunder"):
            continue
        hum = random.Random(sum(map(ord, part)))
        parts[part] = [(max(0.0, s + (hum.random() - 0.5) * 0.04), l, p, max(1, min(127, v + hum.randint(-5, 5))))
                       for s, l, p, v in notes]
    return parts


def score():
    os.makedirs(MIDI, exist_ok=True)
    for part, notes in build().items():
        if notes:
            midiw.write("%s/%s.mid" % (MIDI, part), notes, BPM)
            print("%-8s %4d notes" % (part, len(notes)))


JOBS = [("bass", "dx7-bass.ttl"), ("epiano", "dx7-epiano.ttl"), ("guitar", "halloween-guitar.ttl"),
        ("kit", "drum-machine.ttl"), ("rain", "rain.ttl"), ("thunder", "thunder.ttl")]
RETURNS = [("epiano", "epiano-verb"), ("guitar", "guitar-verb")]


def run(args):
    # cwd is the Valis repository so the kit's relative sound paths resolve
    r = subprocess.run([renderer()] + args, cwd=VALIS, capture_output=True, text=True)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]


def render_one(job):
    part, circuit = job
    if not os.path.exists("%s/%s.mid" % (MIDI, part)):
        return
    print(part, run(["%s/%s" % (CIRCUITS, circuit), "--midi", "%s/%s.mid" % (MIDI, part), "--tempo", str(BPM), "--rolling",
                     "--seconds", "%.1f" % SECONDS, "-o", "%s/%s.wav" % (WAVS, part)]), flush=True)


def render():
    """Every part, or only those named by --only=bass,kit (the reverb returns of a part are redone with it)."""
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--only=")), None)
    os.makedirs(WAVS, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(render_one, [j for j in JOBS if only is None or j[0] in only]))
        list(pool.map(lambda r: print(r[1], run(["%s/reverb-return.ttl" % CIRCUITS, "-i", "%s/%s.wav" % (WAVS, r[0]),
                                                 "-o", "%s/%s.wav" % (WAVS, r[1])]), flush=True),
                      [r for r in RETURNS if only is None or r[0] in only]))


# stem: (level in dB of the stem's playing rms, pan -1..1, high-pass Hz or 0). A stereo stem keeps its image and takes
# the pan as a balance.
LEVELS = {"bass": (-20.0, 0.0, 30), "epiano": (-23.0, -0.2, 90), "epiano-verb": (-31.0, 0.3, 200),
          "guitar": (-28.0, 0.35, 150), "guitar-verb": (-33.0, -0.3, 250),
          "kit": (-26.0, 0.0, 40), "rain": (-34.0, 0.0, 120), "thunder": (-29.0, 0.0, 30)}


def playing_rms_db(x, rate):
    import numpy as np
    w = rate // 10
    n = len(x) // w
    e = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(axis=1))
    e = e[e > 1.0e-3]
    return 20 * np.log10(np.sqrt((e ** 2).mean()) + 1.0e-12) if len(e) else -120.0


def room(x, rate):
    """A synthetic room: exponentially decaying noise, different in each ear, convolved with the whole band."""
    import numpy as np
    from scipy.signal import fftconvolve, butter, sosfilt
    rng = np.random.default_rng(7)
    n = int(1.6 * rate)
    t = np.arange(n) / rate
    env = np.exp(-t / 0.4) * (1.0 - np.exp(-t / 0.004))
    ir = np.stack([rng.standard_normal(n) * env, rng.standard_normal(n) * env], axis=1)
    ir = sosfilt(butter(1, 4500, "lowpass", fs=rate, output="sos"), ir, axis=0)
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    ir = np.concatenate([np.zeros((int(0.012 * rate), 2)), ir])
    wet = np.stack([fftconvolve(x[:, 0], ir[:, 0]), fftconvolve(x[:, 1], ir[:, 1])], axis=1)
    return wet[:len(x)]


# Gain in dB for each section, applied with --arc.
ARC_DB = {"intro": -4.0, "verseA": 0.0, "verseB": 0.5, "bridge": 1.0, "solo": 1.5, "verseC": 0.0, "outro": -3.0}


def arc_curve(rate, length):
    import numpy as np
    curve = np.zeros(length)
    bar = 4 * 60 / BPM
    at = 0
    for name, bars in SECTIONS:
        end = at + int(bars * bar * rate)
        curve[at:min(end, length)] = ARC_DB[name]
        at = end
    curve[at:] = ARC_DB[SECTIONS[-1][0]]
    w = int(2.0 * rate) | 1
    padded = np.concatenate([np.full(w // 2, curve[0]), curve, np.full(w // 2, curve[-1])])
    running = np.concatenate([[0.0], np.cumsum(padded)])
    smooth = (running[w:] - running[:-w]) / w
    return 10 ** (smooth / 20)


def section_levels(x, rate):
    import numpy as np
    bar = 4 * 60 / BPM
    out, at = [], 0
    for name, bars in SECTIONS:
        end = at + int(bars * bar * rate)
        seg = x[at:end]
        out.append((name, playing_rms_db(seg if seg.ndim == 1 else seg.mean(axis=1), rate)))
        at = end
    return out


def mix(target_lufs=None, version="v1", arc=False):
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import butter, sosfilt
    os.makedirs(MIXES, exist_ok=True)
    total = None
    for part, (level, pan, hp) in LEVELS.items():
        path = "%s/%s.wav" % (WAVS, part)
        if not os.path.exists(path):
            print("missing", path)
            continue
        rate, d = wavfile.read(path)
        d = d.astype(np.float64) / (2.0 ** 31 if d.dtype == np.int32 else 32768.0 if d.dtype == np.int16 else 1.0)
        if d.ndim == 1:
            d = np.stack([d, d], axis=1)
        if hp:
            d = sosfilt(butter(2, hp, "highpass", fs=rate, output="sos"), d, axis=0)
        mono = d.mean(axis=1)
        g = 10 ** ((level - playing_rms_db(mono, rate)) / 20)
        theta = (pan + 1) * np.pi / 4
        stereo = d * np.array([np.cos(theta), np.sin(theta)]) * g * np.sqrt(2)
        if total is None:
            total = np.zeros((max(len(stereo), int(SECONDS * rate)), 2))
        total[:len(stereo)] += stereo
    total = total[:int((BARS * 4 * 60 / BPM + 4) * rate)]
    if arc:
        total = total * arc_curve(rate, len(total))[:, None]
    total[-4 * rate:] *= np.linspace(1.0, 0.0, 4 * rate)[:, None]
    total = total + room(total, rate) * 0.10
    mx = np.tanh(total * 1.3) / 1.3
    mx = mx / np.max(np.abs(mx)) * 10 ** (-1.0 / 20)
    out = "%s/%s-%s.wav" % (MIXES, NAME, version)
    wavfile.write(out, rate, (mx * 8388607).astype(np.int32) << 8)
    if target_lufs is not None:
        gain, limited = lufs.gain_to_target(out, target_lufs)
        mx = mx * 10 ** (gain / 20)
        wavfile.write(out, rate, (mx * 8388607).astype(np.int32) << 8)
        print("loudness: gain %+.2f dB toward %.1f LUFS%s" % (gain, target_lufs, " (held back by the peak ceiling)" if limited else ""))
    print("mixed:", out)
    print("loudness:", lufs.measure(out))
    print("section levels (playing rms, dB):", ", ".join("%s %.1f" % lv for lv in section_levels(mx, rate)))


if __name__ == "__main__":
    steps = [a for a in sys.argv[1:] if not a.startswith("--")] or ["score", "render", "mix"]
    target = next((float(a.split("=", 1)[1]) for a in sys.argv[1:] if a.startswith("--lufs=")), None)
    version = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--version=")), "v1")
    for s in steps:
        if s == "mix":
            mix(target, version, arc="--arc" in sys.argv[1:])
        else:
            {"score": score, "render": render}[s]()
