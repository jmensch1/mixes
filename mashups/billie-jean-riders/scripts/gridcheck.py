import sys, numpy as np
from wav import readwav
p = sys.argv[1]; bpm = float(sys.argv[2]); sr = 44100
x = readwav(p); print("length s", len(x)/sr)
k = 200; low = np.convolve(x, np.ones(k)/k, 'same')   # crude low-pass: kicks
hop = 441; n = len(low)//hop
e = np.abs(low[:n*hop]).reshape(n, hop).max(1)
on = [i for i in range(5, n-5) if e[i]==e[i-5:i+6].max() and e[i] > 0.3*e.max() and e[i] > 2*e[max(0,i-30):i-3].mean()]
on = np.array(on)*hop/sr
print("first kicks", np.round(on[:4], 3))
beat = 60/bpm
dev = (on/beat + 0.5) % 1 - 0.5          # how far each kick is from the nearest beat, in beats
for w0 in range(0, int(len(x)/sr), 20):
    d = dev[(on >= w0) & (on < w0+20)]
    if len(d) > 4: print(f"{w0:4d}-{w0+20:4d} s: kicks {np.median(d)*beat*1000:+6.1f} ms from the {bpm} grid (spread {np.std(d)*beat*1000:4.1f} ms, {len(d)} kicks)")
