from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;BASE=B/'full26/audio';BASE.mkdir(exist_ok=True);read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=read(B/'full26/build/build.json');exe=Path(build['exe']);script=H/'audio26_observer.gd';assert sha(exe)==build['sha256']
for primary in ['ember','frost','arc']:
 o=BASE/(primary+'01');runtime=exe.parent/('qa-probe/audio-'+primary+'01');assert not o.exists() and not runtime.exists();o.mkdir();shutil.copy2(script,o/script.name)
 for label,args in [('check',['--headless','--check-only','--script',str(script)]),('gpu',['--script',str(script),'--resolution','1920x1080','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-seed=90131','--chapter1-primary=chapter1.skill.'+primary,'--audio26-dir='+str(runtime)])]:
  cmd=[str(exe)]+args
  with (o/(label+'.stdout.txt')).open('xb') as out,(o/(label+'.stderr.txt')).open('xb') as err:
   p=subprocess.Popen(cmd,stdout=out,stderr=err);(o/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(script)},indent=2));print(primary,label,p.pid,flush=True);code=p.wait(timeout=150)
  d={'exit':code,'stderr_bytes':(o/(label+'.stderr.txt')).stat().st_size};(o/(label+'-execution.json')).write_text(json.dumps(d));assert code==0 and d['stderr_bytes']==0
 shutil.copytree(runtime,o/'proof');assert read(o/'proof/RESULT.json')['same_complete_core'];assert sha(exe)==build['sha256'];print(primary,'PASS',flush=True)
