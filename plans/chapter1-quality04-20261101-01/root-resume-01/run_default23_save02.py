from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full23/runtime/default-save02';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full23/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];capture=exe.parent/'qa-captures/default23-save02';assert not capture.exists()
def execute(label,cmd):
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe)},indent=2),encoding='utf-8');print(label,p.pid,flush=True);code=p.wait(timeout=240)
 report={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(report),encoding='utf-8');assert code==0 and report['stderr_bytes']==0
execute('preflight',[str(exe),'--headless','--script',str(H/'default23_preflight.gd')])
pre=[json.loads(s.split('DEFAULT23_PREFLIGHT ',1)[1]) for s in (O/'preflight.stdout.txt').read_text(encoding='utf-8').splitlines() if 'DEFAULT23_PREFLIGHT ' in s];assert len(pre)==1 and not pre[0]['exists']
profile=Path(pre[0]['path']);assert profile.parent.name=='AshenCloisterChapterOneQuality23' and not profile.exists()
(O/'preflight.json').write_text(json.dumps(pre[0],indent=2),encoding='utf-8')
execute('check-observer',[str(exe),'--headless','--check-only','--script',str(H/'default23_native.gd')])
execute('native',[str(exe),'--script',str(H/'default23_native.gd'),'--fixed-fps','60','--','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=30'])
rows=[json.loads(s.split('DEFAULT23_FINAL ',1)[1]) for s in (O/'native.stdout.txt').read_text(encoding='utf-8').splitlines() if 'DEFAULT23_FINAL ' in s];assert len(rows)==1
d=rows[0];assert d['mode']=='victory' and d['profile_path']=='user://chapter-one-profile-v1.json' and d['profile_available'] and d['profile']['revision']==1 and len(d['profile']['items'])==34 and d['profile']['completed_runs']==1
assert read(profile)==d['profile'];shutil.copy2(profile,O/'profile-after.json');shutil.copytree(capture,O/'captures')
(O/'RESULT.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');assert sha(exe)==build['sha256'];print('PASS DEFAULT23 SAVE',flush=True)
