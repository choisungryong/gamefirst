from pathlib import Path
import numpy as np
from scipy.signal import resample_poly
import subprocess,shutil,wave,json,hashlib
BASE=Path('C:/Project/game-research/audio-sources/quality03-20261031-01')
OUT=Path('C:/Project/d2r-combat-baseline/chapter1/art/quality03_audio')
OUT.mkdir(parents=True,exist_ok=True)
FF=shutil.which('ffmpeg');assert FF
RATE=48000
commands=[];sources={};products=[]
def source(rel,speed=1.0):
    p=BASE/rel
    command=[FF,'-v','error','-i',str(p),'-f','f32le','-ac','1','-ar',str(RATE),'pipe:1']
    result=subprocess.run(command,capture_output=True);commands.append({'argv':command,'actual_exit':result.returncode,'stderr':result.stderr.decode()});assert result.returncode==0
    x=np.frombuffer(result.stdout,dtype='<f4').copy()
    if speed!=1:x=np.interp(np.arange(0,len(x),speed),np.arange(len(x)),x)
    sources[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
    return x
def mix(name,duration,layers,peak=.68):
    x=np.zeros(int(duration*RATE),dtype=np.float64)
    for rel,gain,delay,speed in layers:
        a=source(rel,speed);offset=int(delay*RATE);n=min(len(a),len(x)-offset)
        if n>0:x[offset:offset+n]+=a[:n]*gain
    x-=np.mean(x)
    edge=min(int(.012*RATE),len(x)//4)
    x[:edge]*=np.linspace(0,1,edge);x[-edge:]*=np.linspace(1,0,edge)
    maximum=np.max(np.abs(x));assert maximum>1e-8
    x=x/maximum*peak
    data=np.round(x*32767).astype('<i2')
    target=OUT/(name+'.wav');assert not target.exists(),target
    with wave.open(str(target),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(data.tobytes())
    products.append({'file':target.name,'duration':duration,'frames':len(x),'rate':RATE,'channels':1,'peak':float(np.max(np.abs(x))),'rms':float(np.sqrt(np.mean(x*x))),'clipped_samples':int(np.sum(np.abs(data)>=32767)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'layers':layers})
for i in range(3):
    mix('fire_'+str(i),.42,[('sci-fi-sounds/Audio/thrusterFire_%03d.ogg'%i,.85,0,1.5),('rpg-audio/Audio/knifeSlice.ogg',.30,.015,.80)])
    mix('impact_'+str(i),.25,[('Audio/impactPunch_heavy_%03d.ogg'%i,.80,0,1.0),('Audio/impactWood_light_%03d.ogg'%i,.32,.008,1.15)])
    mix('death_'+str(i),.34,[('Audio/impactWood_heavy_%03d.ogg'%i,.70,0,.9),('Audio/impactGlass_medium_%03d.ogg'%i,.25,.01,.85)])
mix('cold_0',.43,[('rpg-audio/Audio/drawKnife2.ogg',.65,0,1.1),('Audio/impactGlass_light_000.ogg',.5,.035,1.15)])
mix('cold_1',.43,[('rpg-audio/Audio/drawKnife3.ogg',.65,0,1.1),('Audio/impactGlass_light_001.ogg',.5,.035,1.15)])
mix('lightning_0',.30,[('sci-fi-sounds/Audio/forceField_000.ogg',.65,0,1.8),('Audio/impactMetal_medium_000.ogg',.3,.01,.90)])
mix('explosion_0',.64,[('sci-fi-sounds/Audio/explosionCrunch_000.ogg',.85,0,1.2),('sci-fi-sounds/Audio/lowFrequency_explosion_000.ogg',.45,.0,1.25)])
mix('hurt_0',.30,[('Audio/impactPunch_heavy_004.ogg',.8,0,.85),('rpg-audio/Audio/cloth3.ogg',.35,0,1.0)])
mix('drop_0',.50,[('rpg-audio/Audio/metalPot1.ogg',.5,0,1.0),('Audio/impactBell_heavy_000.ogg',.25,.025,1.5)])
mix('pickup_0',.28,[('rpg-audio/Audio/handleCoins.ogg',1,0,1.0)])
mix('equip_0',.28,[('rpg-audio/Audio/bookClose.ogg',.7,0,1.0),('rpg-audio/Audio/metalLatch.ogg',.35,.01,1.0)])
mix('step_0',.22,[('Audio/footstep_concrete_000.ogg',1,0,1.0)])
mix('step_1',.22,[('Audio/footstep_concrete_003.ogg',1,0,1.0)])
mix('ambience',4.0,[('sci-fi-sounds/Audio/spaceEngineLow_000.ogg',.7,0,.55),('rpg-audio/Audio/creak1.ogg',.10,.5,.6)],peak=.22)
for pack,p in [('Impact','License.txt'),('RPG','rpg-audio/License.txt'),('Sci-fi','sci-fi-sounds/License.txt')]:
    shutil.copy2(BASE/p,OUT/('LICENSE-Kenney-'+pack+'.txt'))
ledger={'creator':'Kenney','license':'CC0 1.0 Universal','pages':['https://kenney.nl/assets/impact-sounds','https://kenney.nl/assets/rpg-audio','https://kenney.nl/assets/sci-fi-sounds'],'method':'Mono48kPCM16, selected licensed source layers, rate variation, edge fades, DC removal and per-cue peak normalization. No synthesized sine cues. Ambience remains designed drone candidate, not field-recording claim.','source_sha256':sources,'products':products,'actual_hearing':'Not certified by waveform validation; needs real listening in game.'}
(OUT/'AUDIO-LEDGER.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
(Path(__file__).parent/'audio-build-execution.json').write_text(json.dumps({'commands':commands,'products':products},indent=2)+'\n')
print(json.dumps({'products':len(products),'clipped_samples':sum(p['clipped_samples'] for p in products),'max_peak':max(p['peak'] for p in products)}))
