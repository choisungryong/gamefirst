from pathlib import Path
import json,hashlib,subprocess,wave,array,sys,re
ROOT=Path('C:/Project/d2r-combat-baseline')
OUT=Path(__file__).resolve().parent
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 p=OUT/n
 assert not p.exists(),f'Preserve prior evidence: {p}'
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def manifest(p):
 d=json.loads((ROOT/p).read_text(encoding='utf-8'))
 return {r['path']:r['sha256'] for r in d} if isinstance(d,list) else d
def pins():
 groups={}
 for name,path in [('fx33','plans/chapter1-quality-20261031-01/fx/v02/source-manifest.json'),('world6','plans/chapter1-quality-20261031-01/world/verification02/source-manifest.json'),('core9','chapter1/evidence/core-pilot-20261031-03/source-manifest.json'),('baseline51','evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json')]:
  expected=manifest(path);current={p:sha(ROOT/p) for p in expected}
  groups[name]={'count':len(current),'current':current,'mismatches':[p for p in expected if current[p]!=expected[p]]}
 extra={
  'builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe':'111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188',
  'builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe':'5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29',
  'C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/equipment-v1.json':'b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353',
  'C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/progress-v1.json':'56a9d80654774ec7fc013e1a1e4c7b614243c796f4d02d5af77059ab9849b227'}
 current={p:sha(ROOT/p) for p in extra}
 groups['exe-save4']={'count':4,'current':current,'mismatches':[p for p in extra if current[p]!=extra[p]]}
 return groups
def run(label,script,args=[]):
 command=[str(ENGINE),'--headless','--path',str(ROOT),'--script','res://'+script,'--']+args
 r=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=100)
 record={'command':command,'cwd':str(ROOT),'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')}
 write(label+'-execution.json',record)
 return record
def main():
 write('pins-before.json',pins())
 base=(OUT.parent/'verification-01/independent.gd').read_text(encoding='utf-8')
 assert 'FileAccess.WRITE' not in base and 'store_string' not in base
 base=base.replace('check(view.world.art_status.get("props",0)<=500,"decorative props count bounded in authored composition")','check(view.world.art_status.get("props",0)<=700,"decorative props count bounded including dense low vegetation")')
 base=base.replace('exercise_quality()\n\tif "--prove-failure"','exercise_quality()\n\texercise_world_revision()\n\tawait exercise_layout()\n\tif "--prove-failure"')
 fixture=base+'\n'+(OUT/'extra.gd.txt').read_text(encoding='utf-8')
 assert not (OUT/'independent.gd').exists()
 (OUT/'independent.gd').write_text(fixture,encoding='utf-8')
 script=(OUT/'independent.gd').relative_to(ROOT).as_posix()
 pos=run('positive',script);neg=run('negative',script,['--prove-failure'])
 audio=[]
 for p in sorted((ROOT/'chapter1/art/quality03_audio').glob('*.wav')):
  with wave.open(str(p),'rb') as w:
   ch=w.getnchannels();rate=w.getframerate();width=w.getsampwidth();frames=w.getnframes();raw=w.readframes(frames)
  a=array.array('h');a.frombytes(raw)
  audio.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'channels':ch,'rate':rate,'width':width,'frames':frames,'peak':max(abs(x) for x in a)/32768,'clipped_samples':sum(x in (-32768,32767) for x in a)})
 write('audio-independent.json',audio)
 after=pins();write('pins-after.json',after)
 success=pos['actual_exit']==0 and neg['actual_exit']==1 and all(not v['mismatches'] for v in after.values()) and len(audio)==20 and all(x['channels']==1 and x['rate']==48000 and x['width']==2 and not x['clipped_samples'] for x in audio)
 write('execution-summary.json',{'success':success,'positive_exit':pos['actual_exit'],'negative_exit':neg['actual_exit'],'audio_count':len(audio),'source_unchanged':json.loads((OUT/'pins-before.json').read_text(encoding='utf-8'))==after,'scope':'Independent headless synthetic fixtures and source/PCM audit. No GPU/performance/hearing/fun approval.'})
 print(json.dumps({'success':success,'positive_exit':pos['actual_exit'],'negative_exit':neg['actual_exit']}))
 return 0 if success else 1
if __name__=='__main__':sys.exit(main())
