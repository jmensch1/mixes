"""Key, bar by bar, of a song's grid stems (bar 1 = the file's start, 117 BPM, 4/4): chroma of the pitched stems,
Krumhansl-Schmuckler over a sliding window, and each bar's strongest bass note."""
import sys, numpy as np
from wav import readwav
S = "/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/audio/stems/"
SR, BAR = 44100, 4 * 60 / 117
NAMES = "C C# D D# E F F# G G# A A# B".split()
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

def chroma_per_bar(x, lo, hi):
    n = int(len(x) / SR / BAR); out = np.zeros((n, 12)); N = 8192
    f = np.fft.rfftfreq(N, 1 / SR); keep = (f > lo) & (f < hi)
    pc = (np.round(12 * np.log2(f[keep] / 440)) + 9) % 12
    win = np.hanning(N)
    for b in range(n):
        s, e = int(b * BAR * SR), int((b + 1) * BAR * SR)
        for i in range(s, e - N, N // 2):
            m = np.abs(np.fft.rfft(x[i:i + N] * win))[keep] ** 2
            out[b] += np.bincount(pc.astype(int), m, 12)
    return out

def key(c):
    c = c / (c.sum() + 1e-12); best = []
    for r in range(12):
        for prof, q in ((MAJ, "major"), (MIN, "minor")):
            best.append((np.corrcoef(c, np.roll(prof, r))[0, 1], f"{NAMES[r]} {q}"))
    best.sort(reverse=True); return best[0], best[1]

song, W = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8
mix = None
for p in ["vocals", "bass", "guitar", "piano", "other"]:
    x = readwav(S + f"{song}-{p}.wav")
    mix = x if mix is None else (np.pad(mix, (0, max(0, len(x) - len(mix)))) + np.pad(x, (0, max(0, len(mix) - len(x)))))
bass = readwav(S + f"{song}-bass.wav")
C = chroma_per_bar(mix, 80, 2000); B = chroma_per_bar(bass, 30, 300)
loud = C.sum(1); thr = loud.max() * 0.01
print(f"{song}: {len(C)} bars; whole song: {key(C[loud > thr].sum(0))}")
for b in range(len(C)):
    lo, hi = max(0, b - W // 2), min(len(C), b + W // 2)
    (r1, k1), (r2, k2) = key(C[lo:hi].sum(0))
    bn = NAMES[int(np.argmax(B[b]))] if b < len(B) and B[b].sum() > B.sum(1).max() * 0.02 else "-"
    print(f"bar {b+1:3d}  {k1:9s} {r1:.2f}  (next {k2:9s} {r2:.2f})  bass {bn:2s}  {'quiet' if loud[b] < thr else ''}")
