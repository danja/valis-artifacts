# scripts/lights-on-nobody-home/track.py
#
# "Lights On, Nobody Home": an original song for a Latin band of acoustic-sounding instruments, played by the
# circuits in the Valis repository (nylon-guitar.ttl, guitarron.ttl, harp.ttl, trumpets.ttl, violins.ttl,
# latin-perc.ttl). The verses are bright mariachi/son in C major; the chorus jumps a whole step up into D Hungarian
# minor (D E F G# A Bb C#) and goes punk. Lyrics: artifacts/lights-on-nobody-home/docs/lyrics.md.
#
#   python3 track.py score    write one MIDI file per part to artifacts/lights-on-nobody-home/midi/
#   python3 track.py render   render every part to artifacts/lights-on-nobody-home/wavs/
#   python3 track.py mix      mix the stems to artifacts/lights-on-nobody-home/mixes/
#   python3 track.py          all three
#
# 128 bpm, 92 bars (about 2:53). Nothing in it is taken from another song: the melody and the patterns are new.
import os, sys, random, subprocess
from concurrent.futures import ThreadPoolExecutor

VALIS = os.environ.get("VALIS", "/chalet/github/valis")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, "..", "..", "artifacts", "lights-on-nobody-home"))
MIDI, WAVS, MIXES = (os.path.join(OUTDIR, d) for d in ("midi", "wavs", "mixes"))
RENDER = os.path.join(VALIS, "build", "valis_render_artefacts", "Debug", "valis_render")
sys.path.insert(0, os.path.join(VALIS, "scripts", "halloween"))
import midiw

BPM = 128
STEP = 0.25
SECTIONS = [("intro", 8), ("verse1", 16), ("pre1", 4), ("chorus1", 8), ("verse2", 16), ("pre2", 4), ("chorus2", 8),
            ("bridge", 8), ("chorus3", 16), ("outro", 4)]
BARS = sum(n for _, n in SECTIONS)
SECONDS = BARS * 4 * 60 / BPM + 8
PARTS = ["shakers", "congas", "kit", "guitarron", "vihuela", "guitar", "harp", "trumpets", "violins"]

# chord: (name, guitarron root, guitarron fifth, vihuela strum, guitar arpeggio, violin chord)
CH = {
    "C":  (36, 43, (60, 64, 67, 72), (48, 52, 55, 60), (64, 67, 72, 76)),
    "F":  (41, 36, (60, 65, 69, 72), (53, 57, 60, 65), (65, 69, 72, 77)),
    "G7": (43, 38, (59, 62, 65, 67), (55, 59, 62, 65), (65, 67, 71, 74)),
    "G":  (43, 38, (59, 62, 67, 71), (55, 59, 62, 67), (62, 67, 71, 74)),
    "Am": (33, 40, (57, 60, 64, 69), (45, 52, 57, 60), (64, 69, 72, 76)),
    "Dm": (38, 33, (62, 65, 69, 74), (50, 57, 62, 65), (69, 74, 77, 81)),
    "Bb": (34, 41, (58, 62, 65, 70), (46, 53, 58, 62), (70, 74, 77, 82)),
    "A":  (33, 40, (57, 61, 64, 69), (45, 52, 57, 61), (69, 73, 76, 81)),
    "A7": (33, 40, (57, 61, 64, 67), (45, 52, 55, 61), (67, 73, 76, 81)),
}
VERSE = ["C", "F", "C", "G7", "C", "F", "G7", "C"]
PRE = ["F", "G", "Bb", "A7"]
CHORUS = ["Dm", "Bb", "A", "A", "Dm", "Bb", "A", "A"]
BRIDGE = ["Am", "Dm", "G7", "C", "F", "G", "Bb", "A7"]
OUTRO = ["C", "F", "G7", "C"]

# The verse tune, eight bars, as (beat, length, note). It is played by the trumpets in thirds in the intro and the outro.
THEME = [[(0, .5, 67), (.5, .5, 67), (1, .5, 69), (1.5, .5, 67), (2, 1, 64), (3, .5, 64), (3.5, .5, 67)],
         [(0, .5, 69), (.5, .5, 69), (1, .5, 72), (1.5, .5, 69), (2, 2, 65)],
         [(0, .5, 67), (.5, .5, 67), (1, .5, 69), (1.5, .5, 67), (2, 1, 64), (3, 1, 60)],
         [(0, 1, 62), (1, .5, 65), (1.5, .5, 67), (2, 2, 71)],
         [(0, .5, 72), (.5, .5, 72), (1, .5, 71), (1.5, .5, 72), (2, 1, 67), (3, 1, 64)],
         [(0, .5, 69), (.5, .5, 72), (1, .5, 77), (1.5, .5, 76), (2, 2, 72)],
         [(0, .5, 74), (.5, .5, 72), (1, .5, 71), (1.5, .5, 69), (2, 1, 67), (3, 1, 65)],
         [(0, 2, 64), (2, .5, 67), (2.5, .5, 64), (3, 1, 60)]]
SOLO = [[(0, .5, 76), (.5, .5, 76), (1, .5, 74), (1.5, .5, 72), (2, 2, 69)],
        [(0, .5, 74), (.5, .5, 74), (1, .5, 72), (1.5, .5, 69), (2, 2, 65)],
        [(0, .5, 71), (.5, .5, 74), (1, .5, 77), (1.5, .5, 74), (2, 2, 71)],
        [(0, 1, 72), (1, 1, 76), (2, 2, 79)],
        [(0, .5, 77), (.5, .5, 76), (1, .5, 72), (1.5, .5, 69), (2, 2, 72)],
        [(0, .5, 74), (.5, .5, 71), (1, .5, 74), (1.5, .5, 79), (2, 2, 74)],
        [(0, .5, 70), (.5, .5, 74), (1, .5, 77), (1.5, .5, 74), (2, 2, 70)],
        [(0, .5, 73), (.5, .5, 74), (1, .5, 76), (1.5, .5, 77), (2, 1, 76), (3, 1, 73)]]
# The chorus riff over Dm, Bb, A, A (twice): the Bb to C# step is the augmented second.
RIFF = [[(0, .75, 74), (.75, .25, 73), (1, .5, 70), (1.5, .5, 69), (2, 1, 70), (3, 1, 73)],
        [(0, .75, 70), (.75, .25, 69), (1, .5, 68), (1.5, .5, 69), (2, 2, 70)],
        [(0, .5, 69), (.5, .5, 70), (1, .5, 73), (1.5, .5, 74), (2, 2, 69)],
        [(0, .5, 73), (.5, .5, 74), (1, .5, 76), (1.5, .5, 77), (2, 1, 76), (3, 1, 73)]]
C_MAJOR = {0, 2, 4, 5, 7, 9, 11}
D_HUNGARIAN = {1, 2, 4, 5, 8, 9, 10}


def third_below(note):
    """The note a diatonic third below in C major; 4 semitones when the note is outside the key."""
    if note % 12 not in C_MAJOR:
        return note - 4
    n = note
    for _ in range(2):
        n -= 1
        while n % 12 not in C_MAJOR:
            n -= 1
    return n


def run_up(start, count, pcs):
    notes, n = [], start
    while len(notes) < count:
        if n % 12 in pcs:
            notes.append(n)
        n += 1
    return notes


def locate(bar):
    start = 0
    for name, n in SECTIONS:
        if bar < start + n:
            return name, bar - start, n
        start += n


def chord_of(sec, i):
    if sec in ("intro", "verse1", "verse2"):
        return VERSE[i % 8]
    if sec.startswith("pre"):
        return PRE[i]
    if sec.startswith("chorus"):
        return CHORUS[i % 8]
    if sec == "bridge":
        return BRIDGE[i]
    return OUTRO[i]


def build():
    rnd = random.Random(1946)
    perf = {p: [] for p in PARTS}

    def add(part, bar, step, length_steps, note, vel, shift=0.0, gate=1.0):
        perf[part].append((max(0.0, (bar * 16 + step) * STEP + shift), length_steps * STEP * gate, note, max(1, min(127, int(vel)))))

    def beat(part, bar, b, length, note, vel):
        perf[part].append((bar * 4 + b, max(0.1, length - 0.08), note, int(vel)))

    def strum(part, bar, step, chord, vel, up, length=1.5, spread=0.016):
        notes = list(reversed(chord)) if up else list(chord)
        for k, n in enumerate(notes):
            add(part, bar, step, length * 4, n, vel - 4 * (k if up else 0) + rnd.randint(-4, 4), shift=k * spread + rnd.uniform(-0.004, 0.004))

    for bar in range(BARS):
        sec, i, n = locate(bar)
        name = chord_of(sec, i)
        root, fifth, vih, arp, vio = CH[name]
        verse = sec in ("verse1", "verse2")
        chorus = sec.startswith("chorus")
        pre = sec.startswith("pre")
        intro_band = sec == "intro" and i >= 4
        band = verse or chorus or pre or sec in ("bridge", "outro") or intro_band
        last = i == n - 1
        final_hit = sec == "outro" and i == 3

        # ---- percussion, hand: shakers, scrape, claves, cowbell
        if band or (sec == "intro" and i >= 2):
            if chorus:
                for st in range(16):
                    add("shakers", bar, st, 1, 70, 62 + (16 if st % 4 == 0 else 0) + rnd.randint(-5, 5))
                for st in (0, 4, 8, 12):
                    add("shakers", bar, st, 1, 56, 84)
            elif not final_hit:
                for st in range(0, 16, 2):
                    add("shakers", bar, st, 1, 70, (84 if st % 4 == 0 else 58) + rnd.randint(-5, 5))
        if pre:
            for st in range(16):
                add("shakers", bar, st, 1, 69, 40 + i * 14 + (10 if st % 4 == 0 else 0))
        if verse or sec in ("intro", "bridge", "outro") and not final_hit:
            side = (bar % 2 == 0)                                  # son clave, 3-2
            for st in ((0, 6, 12) if side else (4, 8)):
                add("shakers", bar, st, 1, 75, 100)
        if verse or sec == "bridge":
            for st, nt in ((0, 73), (2, 73), (4, 74), (8, 73), (10, 73), (12, 74)):
                add("shakers", bar, st, 1, nt, 66)
        if final_hit:
            add("shakers", bar, 0, 1, 75, 110)

        # ---- congas and bongos
        if verse or sec in ("bridge", "outro") or intro_band:
            if not final_hit:
                for st, nt, v in ((0, 64, 84), (6, 63, 72), (8, 64, 92), (10, 63, 74), (12, 62, 108), (14, 63, 76)):
                    add("congas", bar, st, 1, nt, v)
        if sec in ("verse2", "bridge") and not last:
            for st in range(0, 16, 2):
                add("congas", bar, st, 1, 61 if st % 4 == 0 else 60, 62 + rnd.randint(-4, 4))

        # ---- the kit (punk): the chorus, the build before it, and a little at the end
        if chorus:
            for st in (0, 4, 8, 12):
                add("kit", bar, st, 1, 36, 108 if st in (0, 8) else 92)
            for st in (4, 12):
                add("kit", bar, st, 1, 38, 118)
                add("kit", bar, st, 1, 39, 100)
            for st in (2, 10, 14):
                add("kit", bar, st, 1, 41, 84)
            if i == 0:
                add("kit", bar, 0, 4, 49, 112)
            if i == 7 and sec != "chorus3" or (sec == "chorus3" and i in (7, 15)):
                for st in range(8, 16):
                    add("kit", bar, st, 1, 38, 70 + (st - 8) * 7)
                    add("kit", bar, st, 1, 39, 60 + (st - 8) * 6)
                add("kit", bar, 12, 1, 41, 100)
                if sec == "chorus3" and i == 15:
                    add("kit", bar, 15, 1, 49, 120)
        if pre:
            steps = (4, 12) if i < 2 else (range(0, 16, 2) if i == 2 else range(16))
            for st in steps:
                v = 64 + i * 14 + (st * 2 if i == 3 else 0)
                add("kit", bar, st, 1, 38, v)
                add("kit", bar, st, 1, 39, v - 10)
            if i == 3:
                add("kit", bar, 0, 1, 41, 100)
        if final_hit:
            add("kit", bar, 0, 4, 49, 118)
            add("kit", bar, 0, 1, 36, 120)

        # ---- the guitarron
        if (verse or sec == "bridge" or intro_band or (sec == "outro")) and not final_hit:
            for st, nt, v in ((0, root, 112), (4, fifth, 92), (8, root, 100), (12, fifth, 92)):
                add("guitarron", bar, st, 3, nt, v, gate=0.8)
        elif chorus:
            for st in range(0, 16, 2):
                add("guitarron", bar, st, 2, root, 112 if st % 4 == 0 else 96, gate=0.8)
        elif pre:
            for st in (0, 4, 8, 12):
                add("guitarron", bar, st, 3, root, 100 + i * 5, gate=0.8)
        if final_hit:
            add("guitarron", bar, 0, 12, root, 118)

        # ---- the vihuela
        if verse or sec in ("bridge", "outro") or intro_band:
            if final_hit:
                strum("vihuela", bar, 0, vih, 118, False, length=3.5)
            else:
                for k, st in enumerate((0, 3, 6, 8, 11, 14)):
                    strum("vihuela", bar, st, vih, 104 if st in (0, 8) else 80, k % 2 == 1, length=0.6)
        elif chorus:
            for k, st in enumerate(range(0, 16, 2)):
                strum("vihuela", bar, st, vih, 112 if k % 2 == 0 else 96, k % 2 == 1, length=0.45, spread=0.01)
        elif pre:
            for st in (0, 4, 8, 12) if i < 2 else range(0, 16, 2):
                strum("vihuela", bar, st, vih, 80 + i * 10, False, length=0.4)

        # ---- the guitar: picked arpeggios
        if sec == "intro" or sec == "verse2" or sec == "bridge" or sec == "outro":
            if not final_hit:
                for k, st in enumerate(range(0, 16, 2)):
                    add("guitar", bar, st, 2, arp[(0, 1, 2, 3, 2, 1, 2, 1)[k]], (82 if k % 4 == 0 else 66) + rnd.randint(-4, 4),
                        shift=rnd.uniform(-0.005, 0.005), gate=1.4)
            else:
                add("guitar", bar, 0, 14, arp[0], 100)

        # ---- the harp: runs into each section, arpeggios under the bridge
        if last and sec in ("intro", "verse1", "verse2", "bridge") or (sec.startswith("pre") and last):
            hungarian = sec.startswith("pre") or sec == "bridge"
            notes = run_up(72 if not hungarian else 70, 8, D_HUNGARIAN if hungarian else C_MAJOR)
            for k, nt in enumerate(notes):
                add("harp", bar, 8 + k, 1, nt, 76 + k * 3, gate=1.0)
        if sec == "bridge" and i < 7:
            for k, st in enumerate(range(0, 16, 2)):
                add("harp", bar, st, 2, arp[(0, 1, 2, 3, 2, 3, 2, 1)[k]] + 12, 70 + (8 if k % 4 == 0 else 0))
        if chorus and i % 4 == 0:
            add("harp", bar, 0, 16, vih[0] + 12, 74)                  # a low ring on the chord at the start of each four bars

        # ---- trumpets: the theme in thirds, stabs in the verses, the solo, the riff
        def duet(melody):
            for b, ln, nt in melody:
                beat("trumpets", bar, b, ln, nt, 100)
                beat("trumpets", bar, b, ln, third_below(nt), 94)
        if sec == "intro":
            duet(THEME[i])
        elif sec == "outro":
            if final_hit:
                for nt in (vih[0] + 12, vih[1] + 12, vih[2] + 12):
                    add("trumpets", bar, 0, 12, nt, 120)
            else:
                duet(THEME[i + 4] if i < 3 else THEME[7])
        elif verse and (i == 7 or (sec == "verse2" and i == 3)):
            for st in (12, 14):
                for nt in (vih[0] + 12, vih[1] + 12, vih[2] + 12):
                    add("trumpets", bar, st, 1.6, nt, 108)
        elif sec == "bridge":
            duet(SOLO[i])
        elif chorus:
            r = RIFF[i % 4]
            for b, ln, nt in r:
                beat("trumpets", bar, b, ln, nt, 112)
                beat("trumpets", bar, b, ln, nt - 12 if sec != "chorus3" else nt + 0, 100)
        elif pre and last:
            for st in (8, 10, 12, 14):
                for nt in (vih[0] + 12, vih[1] + 12, vih[2] + 12):
                    add("trumpets", bar, st, 1.5, nt, 100 + (st - 8) * 3)

        # ---- violins: pads, then long upper notes through the chorus
        if sec == "verse2" or sec == "bridge" or pre:
            if (i % 2 == 0 and not pre) or (pre):
                for nt in vio[:2]:
                    add("violins", bar, 0, (8 if not pre else 16) - 0.4, nt, 62 + (i * 6 if pre else 0))
        if chorus or final_hit:
            for nt in vio:
                add("violins", bar, 0, 16 - 0.4 if not final_hit else 14, nt, 88 if sec != "chorus3" else 100)

    return perf


# part: (timing spread in ms, velocity spread). Wind and strings enter a little loose; the kit is tight.
FEEL = {"shakers": (9, 7), "congas": (8, 8), "kit": (4, 5), "guitarron": (7, 5), "vihuela": (6, 6), "guitar": (8, 7),
        "harp": (9, 6), "trumpets": (11, 5), "violins": (16, 4)}


def humanise(part, notes):
    import random
    rng = random.Random(sum(map(ord, part)))
    ms, vel = FEEL[part]
    beats = ms * BPM / 60000.0
    out = []
    for s, l, p, v in notes:
        s2 = max(0.0, s + rng.gauss(0.0, beats))
        out.append((s2, max(0.05, l - (s2 - s) * 0.5), p, int(min(127, max(20, v + rng.gauss(0.0, vel))))))
    return out


def score():
    os.makedirs(MIDI, exist_ok=True)
    perf = build()
    for part, notes in perf.items():
        notes = humanise(part, notes)
        midiw.write("%s/%s.mid" % (MIDI, part), sorted(notes), BPM)
        print("%-10s %5d notes" % (part, len(notes)))


JOBS = [("shakers", "examples/latin-perc.ttl"), ("congas", "examples/latin-perc.ttl"), ("kit", "examples/latin-perc.ttl"),
        ("guitarron", "examples/guitarron.ttl"), ("vihuela", "examples/nylon-guitar.ttl"), ("guitar", "examples/nylon-guitar.ttl"),
        ("harp", "examples/harp.ttl"), ("trumpets", "examples/trumpets.ttl"), ("violins", "examples/violins.ttl")]


def render_one(job):
    part, circuit = job
    r = subprocess.run([RENDER, circuit, "--midi", "%s/%s.mid" % (MIDI, part), "--tempo", str(BPM), "--rolling",
                        "--seconds", "%.1f" % SECONDS, "-o", "%s/%s.wav" % (WAVS, part)], cwd=VALIS, capture_output=True, text=True)
    print(part, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:], flush=True)


def render():
    os.makedirs(WAVS, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(render_one, JOBS))


# part: (level in dB of the stem's playing rms, pan -1..1, high-pass Hz or 0)
LEVELS = {"shakers": (-31.0, 0.2, 200), "congas": (-28.0, -0.2, 90), "kit": (-24.0, 0.0, 0),
          "guitarron": (-21.0, 0.0, 0), "vihuela": (-27.0, 0.4, 150), "guitar": (-27.0, -0.4, 100),
          "harp": (-29.0, -0.15, 100), "trumpets": (-25.0, 0.1, 150), "violins": (-30.0, -0.3, 140)}


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
    n = int(1.3 * rate)
    t = np.arange(n) / rate
    env = np.exp(-t / 0.28) * (1.0 - np.exp(-t / 0.004))
    ir = np.stack([rng.standard_normal(n) * env, rng.standard_normal(n) * env], axis=1)
    ir = sosfilt(butter(1, 5500, "lowpass", fs=rate, output="sos"), ir, axis=0)
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    pre = np.zeros((int(0.012 * rate), 2))
    ir = np.concatenate([pre, ir])
    wet = np.stack([fftconvolve(x[:, 0], ir[:, 0]), fftconvolve(x[:, 1], ir[:, 1])], axis=1)
    return wet[:len(x)]


def mix():
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
    total = total + room(total, rate) * 0.16
    mx = np.tanh(total * 1.6) / 1.6
    mx = mx / np.max(np.abs(mx)) * 10 ** (-1.0 / 20)
    wavfile.write("%s/lights-on-nobody-home.wav" % MIXES, rate, (mx * 8388607).astype(np.int32) << 8)
    print("mixed: %.1f s, peak %.3f rms %.3f dB" % (len(mx) / rate, np.max(np.abs(mx)), 20 * np.log10(np.sqrt(np.mean(mx ** 2)))))


if __name__ == "__main__":
    steps = [a for a in sys.argv[1:] if not a.startswith("--")] or ["score", "render", "mix"]
    for s in steps:
        {"score": score, "render": render, "mix": mix}[s]()
