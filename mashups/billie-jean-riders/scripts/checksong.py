import sys, numpy as np
from wav import readwav
sr=44100; St="/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/audio/stems/"; A="/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/logic/mashup-grid.logicx/Media/Audio Files/"
song, grid = sys.argv[1], sys.argv[2]
g=readwav(A+grid); print(song, "grid file", round(len(g)/sr,1), "s, loudest", round(float(np.abs(g).max()),3))
total=np.zeros(len(g)+sr*10,np.float32)
for p in ["vocals","drums","bass","guitar","piano","other"]:
    x=readwav(St+f"{song}-{p}.wav"); total[:len(x)]+=x
    print(f"  {p:6s} {len(x)/sr:6.1f} s  loudest {float(np.abs(x).max()):.3f}")
seg=slice(sr*60,sr*90); w=sr*3
c=np.correlate(total[seg.start-w:seg.stop+w], g[seg], 'valid'); lag=int(np.argmax(c))-w
a=total[max(0,lag):]; b=g[max(0,-lag):]; n=min(len(a),len(b),len(g)-max(0,-lag))
print(f"  stems start {lag/sr*1000:.0f} ms before the grid file; they sum to it within {100*np.sqrt(np.mean((a[:n]-b[:n])**2))/np.sqrt(np.mean(b[:n]**2)):.1f}%")
