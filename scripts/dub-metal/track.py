# scripts/dub-metal/track.py
#
# "dub-metal" (working title): dub reggae foundations with industrial metal-bashing on top, played by the circuits in
# the Valis repository (dub-bass.ttl, 909.ttl, tonewheel-organ.ttl, metal-clang.ttl, free-bell.ttl) and sent through
# dub-delay.ttl. The brief is in sources/dub-metal-prompt.md.
#
#   python3 track.py score    write one MIDI file per part to artifacts/dub-metal/midi/
#   python3 track.py render   render every part, and the echo returns, to artifacts/dub-metal/wavs/
#   python3 track.py mix      mix the stems to artifacts/dub-metal/mixes/
#   python3 track.py          all three
#
# C Phrygian Dominant (C Db E F G Ab Bb), 85 bpm, 72 bars (about 3:23). The harmony is a vamp on C and Db, so the half
# step above the tonic and the augmented second Db to E, which are what the scale sounds like, are always in the bass.
import os, sys, random, subprocess
from concurrent.futures import ThreadPoolExecutor

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "dub-metal"))
MIDI, WAVS, MIXES = (os.path.join(OUTDIR, d) for d in ("midi", "wavs", "mixes"))
# Release is several times faster and renders the same samples; fall back to Debug when only that is built.
# VALIS_RENDER names a binary outright, for when the Release build is older than the code.
RENDER = os.environ.get("VALIS_RENDER") or next((p for p in (os.path.join(VALIS, d, "valis_render_artefacts", c, "valis_render")
                           for d, c in (("build-release", "Release"), ("build", "Debug"))) if os.path.exists(p)),
              os.path.join(VALIS, "build", "valis_render_artefacts", "Debug", "valis_render"))
sys.path.insert(0, os.path.join(VALIS, "scripts", "halloween"))
sys.path.insert(0, os.path.join(VALIS, "scripts", "shot"))
import midiw, lufs

BPM = 85
SECTIONS = [("intro", 8), ("groove", 16), ("bash", 16), ("dub", 8), ("peak", 16), ("outro", 8)]
BARS = sum(n for _, n in SECTIONS)
SECONDS = BARS * 4 * 60 / BPM + 10
PARTS = ["bass", "kit", "stabs", "metal", "bell"]

# Eight bars, round again: C C Db C | C C Fm Db. (name, bass root, bass pickup into the next bar, stab chord)
CHORDS = {"C":  (36, 37, (60, 64, 67)),     # the pickup is the half step above, the bII
          "Db": (37, 40, (61, 65, 68)),     # Db to E, the augmented second
          "Fm": (41, 37, (60, 65, 68))}
VAMP = ["C", "C", "Db", "C", "C", "C", "Fm", "Db"]

# Which parts play in which section.
PLAN = {"intro":  {"kit": "hats", "bass": "plain"},
        "groove": {"kit": "onedrop", "bass": "plain", "stabs": "light"},
        "bash":   {"kit": "onedrop", "bass": "plain", "stabs": "skank", "metal": "cycle"},
        "dub":    {"bass": "plain", "stabs": "lone", "bell": "toll", "metal": "anvil"},
        "peak":   {"kit": "steppers", "bass": "heavy", "stabs": "skank", "metal": "cycle"},
        "outro":  {"kit": "hats", "bass": "plain", "stabs": "lone", "bell": "toll"}}


def locate(bar):
    for name, n in SECTIONS:
        if bar < n:
            return name, bar
        bar -= n
    raise ValueError(bar)


def build():
    rng = random.Random(85)
    parts = {p: [] for p in PARTS}
    bar0 = 0
    for name, n in SECTIONS:
        plan = PLAN[name]
        for i in range(n):
            bar = bar0 + i
            b = bar * 4.0
            chord = VAMP[i % 8]
            root, pickup, stab = CHORDS[chord]
            last = i == n - 1

            # -- bass: the root held through the first beat and a half, then a push before beat three and a pickup
            style = plan.get("bass")
            if style:
                parts["bass"] += [(b, 1.4, root, 118), (b + 2.5, 0.4, root, 104), (b + 3.5, 0.4, pickup, 100)]
                if style == "heavy":
                    parts["bass"].append((b + 1.75, 0.2, root + 12, 90))   # an octave up between the two

            # -- kit: one-drop (the kick and the rim on beat three), or a steady pulse in the peak
            style = plan.get("kit")
            if style:
                for k in range(8):
                    parts["kit"].append((b + k * 0.5, 0.2, 42, 62 if k % 2 == 0 else 84))
                if style in ("onedrop", "steppers"):
                    parts["kit"] += [(b + 2.0, 0.25, 36, 124), (b + 2.0, 0.25, 37, 104)]
                if style == "steppers":
                    parts["kit"] += [(b, 0.25, 36, 118), (b + 1.0, 0.25, 36, 96), (b + 3.0, 0.25, 36, 96)]
                if style == "onedrop" and i % 2 == 1:
                    parts["kit"].append((b + 3.5, 0.3, 46, 76))
                if last and name in ("groove", "bash"):
                    parts["kit"] += [(b + 3.0, 0.25, 43, 100), (b + 3.5, 0.25, 41, 112)]

            # -- stabs: offbeat chords on the and of two and the and of four
            style = plan.get("stabs")
            if style == "skank":      # every offbeat, the second and fourth louder: the chop that bubbles
                spots = [0.5, 1.5, 2.5, 3.5]
            elif style == "light":    # the and of two and the and of four
                spots = [1.5, 3.5]
            elif style == "sparse":
                spots = [1.5, 3.5] if i % 2 == 0 else [3.5]
            elif style == "lone":
                spots = [1.5] if i % 4 == 0 else []
            else:
                spots = []
            for s in spots:
                velocity = 100 if s in (1.5, 3.5) else 78
                parts["stabs"] += [(b + s, 0.12, p, velocity) for p in stab + (stab[0] + 12,)]

            # -- metal: a cycle five sixteenths long, against the bar of sixteen
            style = plan.get("metal")
            if style == "cycle":
                tones = [48, 49, 52, 48, 55, 49, 53, 60]     # C3 to C4, a Phrygian Dominant set, struck hard
                for cycle, period, lead in ((0, 1.25, 0.0), (1, 0.75, 0.5)):    # five sixteenths against three
                    for k in range(int(4 / period) + 1):
                        start = lead + k * period + (bar % 5) * 0.25 * (1 - cycle)
                        if start < 4.0 and rng.random() < (0.8 if cycle == 0 else 0.5):
                            parts["metal"].append((b + start, 0.1, tones[(bar * 3 + k + cycle) % len(tones)],
                                                   rng.choice((90, 110, 127))))
            elif style == "anvil" and i % 2 == 0:
                parts["metal"].append((b, 0.2, 36, 124))

            # -- bell: one low toll at the head of a section and every fourth bar after it
            if plan.get("bell") == "toll" and i % 4 == 0:
                parts["bell"].append((b, 3.0, 60, 100))
        bar0 += n

    # A little timing and level variation per part, from a fixed seed, never starting before 0.
    for part, notes in parts.items():
        hum = random.Random(sum(map(ord, part)))
        parts[part] = [(max(0.0, s + (hum.random() - 0.5) * (0.0 if part == "metal" else 0.03)), l, p,
                        max(1, min(127, v + hum.randint(-6, 6)))) for s, l, p, v in notes]
    return parts


def score():
    os.makedirs(MIDI, exist_ok=True)
    for part, notes in build().items():
        if notes:
            midiw.write("%s/%s.mid" % (MIDI, part), notes, BPM)
            print("%-6s %4d notes" % (part, len(notes)))


# part: circuit in the Valis repository
JOBS = [("bass", "examples/dub-bass.ttl"), ("kit", "examples/909.ttl"), ("stabs", "examples/tonewheel-organ.ttl"),
        ("metal", "examples/metal-clang.ttl"), ("bell", "examples/free-bell.ttl")]
# stem: (effect circuit, result)
RETURNS = [("stabs", "stabs-echo"), ("metal", "metal-echo")]


def run(args):
    r = subprocess.run([RENDER] + args, cwd=VALIS, capture_output=True, text=True)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]


def render_one(job):
    part, circuit = job
    if not os.path.exists("%s/%s.mid" % (MIDI, part)):
        return
    print(part, run([circuit, "--midi", "%s/%s.mid" % (MIDI, part), "--tempo", str(BPM), "--rolling",
                     "--seconds", "%.1f" % SECONDS, "-o", "%s/%s.wav" % (WAVS, part)]), flush=True)


def render():
    """Every part, or only those named by --only=metal,stabs (the echo returns of a part are redone with it)."""
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--only=")), None)
    os.makedirs(WAVS, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(render_one, [j for j in JOBS if only is None or j[0] in only]))
        list(pool.map(lambda r: print(r[1], run(["examples/dub-delay.ttl", "-i", "%s/%s.wav" % (WAVS, r[0]),
                                                 "-o", "%s/%s.wav" % (WAVS, r[1])]), flush=True),
                      [r for r in RETURNS if only is None or r[0] in only]))


# stem: (level in dB of the stem's playing rms, pan -1..1, high-pass Hz or 0)
LEVELS = {"bass": (-19.0, 0.0, 28), "kit": (-23.0, 0.0, 0), "stabs": (-26.0, -0.25, 160), "stabs-echo": (-27.0, 0.35, 160),
          "metal": (-21.0, 0.2, 100), "metal-echo": (-27.0, -0.4, 150), "bell": (-33.0, 0.0, 100)}


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


def mix(target_lufs=None, version="v1"):
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
        mono = d if d.ndim == 1 else d.mean(axis=1)
        if hp:
            mono = sosfilt(butter(2, hp, "highpass", fs=rate, output="sos"), mono)
        g = 10 ** ((level - playing_rms_db(mono, rate)) / 20)
        theta = (pan + 1) * np.pi / 4
        stereo = np.stack([mono * np.cos(theta), mono * np.sin(theta)], axis=1) * g * np.sqrt(2)
        if total is None:
            total = np.zeros((max(len(stereo), int(SECONDS * rate)), 2))
        total[:len(stereo)] += stereo
    total = total[:int((BARS * 4 * 60 / BPM + 4) * rate)]
    total[-3 * rate:] *= np.linspace(1.0, 0.0, 3 * rate)[:, None]
    total = total + room(total, rate) * 0.12
    mx = np.tanh(total * 1.5) / 1.5
    mx = mx / np.max(np.abs(mx)) * 10 ** (-1.0 / 20)
    out = "%s/dub-metal-%s.wav" % (MIXES, version)
    wavfile.write(out, rate, (mx * 8388607).astype(np.int32) << 8)
    if target_lufs is not None:
        gain, limited = lufs.gain_to_target(out, target_lufs)
        mx = mx * 10 ** (gain / 20)
        wavfile.write(out, rate, (mx * 8388607).astype(np.int32) << 8)
        print("loudness: gain %+.2f dB toward %.1f LUFS%s" % (gain, target_lufs, " (held back by the peak ceiling)" if limited else ""))
    print("mixed:", out)
    print("loudness:", lufs.measure(out))


if __name__ == "__main__":
    steps = [a for a in sys.argv[1:] if not a.startswith("--")] or ["score", "render", "mix"]
    target = next((float(a.split("=", 1)[1]) for a in sys.argv[1:] if a.startswith("--lufs=")), None)
    version = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--version=")), "v1")
    for s in steps:
        if s == "mix":
            mix(target, version)
        else:
            {"score": score, "render": render}[s]()
