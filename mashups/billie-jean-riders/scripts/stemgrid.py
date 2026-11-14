import numpy as np
from wav import readwav
sr=44100; St="/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/audio/stems/"
g = readwav("/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/logic/mashup-grid.logicx/Media/Audio Files/bj-grid.wav")
parts={}
for p in ["vocals","drums","bass","guitar","piano","other"]:
    parts[p]=readwav(St+f"bj-{p}.wav"); print(p, round(len(parts[p])/sr,3),"s")
print("bj-grid", round(len(g)/sr,3),"s")
total=np.zeros(max(len(v) for v in parts.values())+sr*5,np.float32)
for v in parts.values(): total[:len(v)]+=v
seg=slice(sr*60,sr*90); w=sr*2
ref=g[seg]
c=np.correlate(total[seg.start-w:seg.stop+w], ref, 'valid'); lag=int(np.argmax(c))-w
print("stems are offset from bj-grid by", lag, "samples =", round(lag/sr*1000,2),"ms")
a=total[max(0,lag):]; b=g[max(0,-lag):]; n=min(len(a),len(b))
print("stems sum to bj-grid within", round(100*np.sqrt(np.mean((a[:n]-b[:n])**2))/np.sqrt(np.mean(b[:n]**2)),2),"%")
