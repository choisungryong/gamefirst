"""Independent headless verifier. Only new evidence paths are written."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import wave
import array

ROOT=Path('C:/Project/d2r-combat-baseline')
OUT=Path(__file__).resolve().parent
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):
    path=OUT/name
    assert not path.exists(),f'Preserve evidence: {path}'
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def pins():
    fx=json.loads((ROOT/'plans/chapter1-quality-20261031-01/fx/source-manifest.json').read_text(encoding='utf-8'))
    core=json.loads((ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json').read_text(encoding='utf-8'))
    if isinstance(core,list):core={r['path']:r['sha256'] for r in core}
    old=json.loads((ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json').read_text(encoding='utf-8'))
    world=sorted(set(p.relative_to(ROOT).as_posix() for p in (ROOT/'chapter1/view').glob('cloister_*')))
    groups={}
    for name,expected in [('fx33',fx),('core9',core),('baseline51',old)]:
        current={p:sha(ROOT/p) for p in expected}
        groups[name]={'count':len(current),'current':current,'mismatches':[p for p in expected if current[p]!=expected[p]]}
    groups['world-current']={'current':{p:sha(ROOT/p) for p in world if not p.endswith('.uid')}}
    return groups

def run(label,args):
    command=[str(ENGINE),'--headless','--path',str(ROOT),'--script','res://plans/chapter1-quality-20261031-01/verification-01/independent.gd','--']+args
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=100)
    record={'command':command,'cwd':str(ROOT),'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    write(label+'-execution.json',record)
    return record

def main():
    assert not (OUT/'pins-before.json').exists()
    write('pins-before.json',pins())
    old=ROOT/'plans/chapter1-c2-20261031-01/verification-view-02/independent_view.gd'
    base=old.read_text(encoding='utf-8')
    (OUT/'base-v02.gd.txt').write_bytes(old.read_bytes())
    base=base.replace('check(buttons(view.hud.modal).size()==3,"three actual menu start buttons")','check(buttons(view.hud.modal).filter(func(b):return b.text.ends_with("으로 시작")).size()==3,"three actual menu start buttons plus separate motion control")')
    base=base.replace('var initial_seed: int=view.seed_','exercise_motion(run)\n\tvar initial_seed: int=view.seed_')
    base=base.replace('if "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional verifier failure")','exercise_quality()\n\tif "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional verifier failure")')
    base=base.replace('view.queue_free()\n\tawait process_frame','view.free();view=null;run=null\n\tawait process_frame')
    fixture=base+'\n'+(OUT/'extra.gd.txt').read_text(encoding='utf-8')
    assert not (OUT/'independent.gd').exists()
    (OUT/'independent.gd').write_text(fixture,encoding='utf-8')
    positive=run('positive',[])
    negative=run('negative',['--prove-failure'])
    audio=[]
    ledger=json.loads((ROOT/'chapter1/art/quality03_audio/AUDIO-LEDGER.json').read_text(encoding='utf-8'))
    for path in sorted((ROOT/'chapter1/art/quality03_audio').glob('*.wav')):
        with wave.open(str(path),'rb') as w:
            channels=w.getnchannels();rate=w.getframerate();width=w.getsampwidth();frames=w.getnframes();raw=w.readframes(frames)
        assert width==2
        samples=array.array('h');samples.frombytes(raw)
        peak=max(abs(x) for x in samples)/32768
        clips=sum(x in (-32768,32767) for x in samples)
        audio.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'channels':channels,'rate':rate,'width':width,'frames':frames,'duration':frames/rate,'peak':peak,'clipped_samples':clips})
    write('audio-independent.json',{'files':audio,'ledger_license':ledger['license'],'pages':ledger['pages'],'scope':'Independent PCM measurements; not auditory quality approval.'})
    after=pins();write('pins-after.json',after)
    success=positive['actual_exit']==0 and negative['actual_exit']==1 and all(not after[g]['mismatches'] for g in ('fx33','core9','baseline51')) and all(r['clipped_samples']==0 and r['channels']==1 and r['rate']==48000 for r in audio)
    write('execution-summary.json',{'success':success,'positive_exit':positive['actual_exit'],'negative_exit':negative['actual_exit'],'audio_files':len(audio),'world_still_integration_pending':True})
    print(json.dumps({'success':success,'positive_exit':positive['actual_exit'],'negative_exit':negative['actual_exit']}))
    return 0 if success else 1
if __name__=='__main__':sys.exit(main())
