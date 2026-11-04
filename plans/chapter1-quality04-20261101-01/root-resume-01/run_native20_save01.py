from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full20/runtime/native-save01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full20/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256']
profile=exe.parent/'plans/chapter1-quality04-20261101-01/qa-native20/profile.json';assert not profile.exists()
capture=O/'captures';capture.mkdir()
cmd=[str(exe),'--script',str(H/'native20_save.gd'),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=180']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'native20_save.gd'),'qa_profile':str(profile)},indent=2),encoding='utf-8');print('native-save01',p.pid,flush=True);code=p.wait(timeout=300)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8')
if profile.exists():shutil.copy2(profile,O/'profile-after-first-exit.json')
assert sha(exe)==build['sha256'];assert code==0 and (O/'stderr.txt').stat().st_size==0
print('NATIVE TERMINAL',flush=True)
