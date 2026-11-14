"""How far each song sits from A440, in cents: strong spectral peaks of its pitched stems, folded onto one semitone."""
import sys, numpy as np
from wav import readwav
SR=44100; N=32768
f=np.fft.rfftfreq(N,1/SR)
for song in sys.argv[1:]:
    devs=[]; w=[]
    for p in ["bass","other","vocals","guitar","piano"]:
        x=readwav(f"/Users/jacobmensch/src/mixes/mashups/billie-jean-riders/audio/stems/{song}-{p}.wav")
        for i in range(SR*20, len(x)-N, SR*2):
            m=np.abs(np.fft.rfft(x[i:i+N]*np.hanning(N)))
            for j in np.argsort(m[(f>60)&(f<1500)])[::-1][:6]+np.argmax(f>60):
                if 1<j<len(m)-1 and m[j]>m[j-1] and m[j]>m[j+1]:
                    a,b,c=np.log(m[j-1:j+2]+1e-12); d=0.5*(a-c)/(a-2*b+c)   # parabolic peak
                    fr=(j+d)*SR/N; cents=1200*np.log2(fr/440)
                    devs.append(((cents+50)%100)-50); w.append(m[j])
    devs=np.array(devs); w=np.array(w)
    ang=np.angle(np.sum(w*np.exp(2j*np.pi*devs/100)))*100/(2*np.pi)
    hist=np.histogram(devs,bins=10,range=(-50,50),weights=w)[0]
    print(f"{song:7s} tuning {ang:+.0f} cents from A440   spread {np.round(hist/hist.max(),2)}")
