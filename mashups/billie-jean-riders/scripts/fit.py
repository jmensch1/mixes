"""Which bars of riders can be laid over bj's bass loops (bj transposed -2: E minor). Tuning of each song corrected."""
import numpy as np, json
from wav import readwav
SR, BAR = 44100, 4*60/117
NAMES="C C# D D# E F F# G G# A A# B".split()
S="/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/audio/stems/"
TUNE={"bj":32, "riders":-8}

def chroma(x, cents, shift, lo, hi, N=16384, fund=False):
    f=np.fft.rfftfreq(N,1/SR); k=(f>lo)&(f<hi)
    pc=((np.round(12*np.log2(f[k]/440)-cents/100)+9+shift)%12).astype(int)
    n=int(len(x)/SR/BAR); out=np.zeros((n,12)); win=np.hanning(N)
    for b in range(n):
        for i in range(int(b*BAR*SR), int((b+1)*BAR*SR)-N, N//4):
            m=np.abs(np.fft.rfft(x[i:i+N]*win))[k]**2
            out[b]+=np.bincount(pc, m/f[k] if fund else m, 12)
    return out

def mix(song, parts):
    xs=[readwav(S+f"{song}-{p}.wav") for p in parts]; n=max(map(len,xs)); t=np.zeros(n,np.float32)
    for x in xs: t[:len(x)]+=x
    return t

bjB=chroma(readwav(S+"bj-bass.wav"), TUNE["bj"], -2, 35, 400, fund=True)
bjO=chroma(mix("bj",["bass","other"]), TUNE["bj"], -2, 60, 2000)
rB=chroma(readwav(S+"riders-bass.wav"), TUNE["riders"], 0, 35, 400, fund=True)
rP=chroma(mix("riders",["vocals","guitar","piano","other","bass"]), TUNE["riders"], 0, 80, 2000)

print("bj bass per bar (E minor):")
print(" ".join(f"{b+1}:{NAMES[int(np.argmax(h))] if h.sum()>bjB.sum(1).max()*0.05 else '-'}" for b,h in enumerate(bjB)))
print("riders bass per bar:")
print(" ".join(f"{b+1}:{NAMES[int(np.argmax(h))] if h.sum()>rB.sum(1).max()*0.05 else '-'}" for b,h in enumerate(rB)))
np.savez("chroma.npz", bjB=bjB, bjO=bjO, rB=rB, rP=rP)
