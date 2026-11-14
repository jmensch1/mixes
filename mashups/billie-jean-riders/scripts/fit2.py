import numpy as np, json
from wav import readwav
SR, BAR = 44100, 4*60/117
N="C C# D D# E F F# G G# A A# B".split()
d=np.load("chroma.npz"); bjO,rP,rB=d["bjO"],d["rP"],d["rB"]
x=readwav("/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/audio/stems/bj-bass.wav")
n=16384; f=np.fft.rfftfreq(n,1/SR); k=(f>38)&(f<180)
def first(b):
    i=max(0,int(((b-1)*BAR+0.05)*SR)-n//2)
    if i+n>len(x): return "-"
    m=np.abs(np.fft.rfft(x[i:i+n]*np.hanning(n)))
    if m[k].max()<1: return "-"
    return N[int(round(12*np.log2(f[k][np.argmax(m[k])]/440)-0.32)+9-2)%12]
cls=[first(b) for b in range(1,len(bjO)+1)]
print("bj loop per bar:", "".join(c if c in "EAC" else "." for c in cls))
nz=lambda h:h/(h.sum()+1e-12)
T={c:nz(bjO[[i for i,x in enumerate(cls) if x==c]].sum(0)) for c in "EAC"}
for c in T: print(c, "loop notes:", " ".join(f"{N[j]}{v:.2f}" for j,v in sorted(enumerate(T[c]),key=lambda t:-t[1])[:8]))
W=np.zeros((12,12))
for i in range(12):
    for j in range(12):
        dd=min((i-j)%12,(j-i)%12); W[i,j]={1:1.0,6:0.4,2:0.15}.get(dd,0)
def clash(r,t): r=nz(r); return float(r@W@t)
loud=rP.sum(1); thr=loud.max()*0.02
rows=[]
for b in range(len(rP)):
    rb=N[int(np.argmax(rB[b]))] if b<len(rB) and rB[b].sum()>rB.sum(1).max()*0.05 else "-"
    rows.append((b+1, rb, loud[b]>thr, {c:clash(rP[b],T[c]) for c in "EAC"}))
allv=np.array([r[3][c] for r in rows if r[2] for c in "EA"])
print("clash spread E/A: p10 %.3f p50 %.3f p90 %.3f"%tuple(np.percentile(allv,[10,50,90])))
for b,rb,on,cs in rows:
    print(f"{b:3d} bass {rb:2s} {'' if on else 'quiet'} E {cs['E']:.3f} A {cs['A']:.3f} C {cs['C']:.3f}   top: " +
          " ".join(f"{N[j]}" for j in np.argsort(rP[b-1])[::-1][:5]))
json.dump({"bj":cls,"riders":[(b,rb,bool(on),cs) for b,rb,on,cs in rows]}, open("fit.json","w"))
