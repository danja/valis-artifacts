# scripts/all-fall-down/voicemix.py: adds wavs/voice.wav (rendered from Reaper) to the v3 mix, section by section, 7 dB under the mix rms; writes /tmp/mix_raw.npy. Limiting and -10 LUFS were done by hand, see README.
import numpy as np, subprocess, sys, wave
D='/home/danny/github/valis-artifacts/artifacts/all-fall-down/'
R=48000
def load(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','2','-ar',str(R),'-'],capture_output=True)
    return np.frombuffer(r.stdout,dtype=np.float32).reshape(-1,2).astype(np.float64)
db=lambda x:20*np.log10(np.sqrt((np.asarray(x)**2).mean())+1e-12)
OFFSET=float(sys.argv[1]) if len(sys.argv)>1 else -7.0
v=load(D+'wavs/voice.wav'); m=load(D+'mixes/all-fall-down-v3.wav')
n=len(m); v=v[:n] if len(v)>=n else np.vstack([v,np.zeros((n-len(v),2))])
S=[('intro',16),('build1',8),('drop1',16),('break',16),('build2',8),('drop2',24),('outro',16)]
bar=4*60/140*R; t=0
blk=2400
gains=np.ones(n); rows=[]
for name,b in S:
    a,z=int(t*bar),int((t+b)*bar); t+=b
    vs=v[a:z]; ms=m[a:z]
    # active windows of the voice: 50 ms blocks above -45 dBFS
    k=len(vs)//blk
    act=np.array([db(vs[i*blk:(i+1)*blk])>-45 for i in range(k)])
    if act.sum()<4: g=0.0; rows.append((name,None,None,0.0)); gains[a:z]=1; continue
    idx=np.concatenate([np.arange(i*blk,(i+1)*blk) for i in np.where(act)[0]])
    vr=db(vs[idx]); mr=db(ms)
    gdb=(mr+OFFSET)-vr
    gains[a:z]=10**(gdb/20); rows.append((name,vr,mr,gdb))
# smooth gain over one bar
kern=np.ones(int(bar))/int(bar)
K=int(bar); c=np.cumsum(np.insert(gains,0,0)); i=np.arange(n); lo=np.clip(i-K//2,0,n); hi=np.clip(i+K//2,0,n); gs=(c[hi]-c[lo])/np.maximum(hi-lo,1)
vm=v*gs[:,None]
mix=m+vm
for r in rows: print('%-7s voice %s mix %s gain %+.1f dB'%(r[0],'%.1f'%r[1] if r[1] is not None else 'n/a','%.1f'%r[2] if r[2] is not None else 'n/a',r[3]))
np.save('/tmp/mix_raw.npy',mix.astype(np.float32))
