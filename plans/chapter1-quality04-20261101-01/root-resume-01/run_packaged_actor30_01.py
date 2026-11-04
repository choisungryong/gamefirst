from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
O=B/'full30/runtime/silhouette01';O.mkdir(parents=True,exist_ok=False)
build=json.loads((B/'full30/build/build.json').read_text());exe=Path(build['exe']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(exe)==build['sha256'];runtime=exe.parent/'qa-probe/silhouette01';assert not runtime.exists()
script=H/'packaged_actor30.gd';shutil.copy2(script,O/script.name)
for label,args in [('check',['--headless','--check-only','--script',str(script)]),('gpu',['--script',str(script),'--resolution','1920x1080','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--actor30-dir='+str(runtime)])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[str(exe)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
shutil.copytree(runtime,O/'proof');assert sha(exe)==build['sha256'];print('PASS ACTUAL30 LIVE SILHOUETTE',flush=True)
