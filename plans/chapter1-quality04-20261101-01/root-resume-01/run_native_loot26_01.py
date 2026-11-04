from pathlib import Path
import json,hashlib,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full26/runtime/native-loot01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=read(B/'full26/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];script=H/'native_loot26.gd';runtime=exe.parent/'qa-probe/native-loot01';assert not runtime.exists()
for label,args in [('check',['--headless','--check-only','--script',str(script)]),('native',['--script',str(script),'--windowed','--resolution','1920x1080','--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--native-loot26-dir='+str(runtime)])]:
 cmd=[str(exe)]+args
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(script)},indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=210)
 report={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(report));assert code==0 and report['stderr_bytes']==0
import shutil
shutil.copytree(runtime,O/'proof');d=read(O/'proof/RESULT.json');assert d['pickup_tick']>=d['checkpoint'] and d['name_and_node_removed'] and not d['pilot'] and d['profile_off'] and d['native_inputs'] and d['audio_save_result']==0;assert sha(exe)==build['sha256'];print('PASS ACTUAL26 NATIVE PICKUP',flush=True)
