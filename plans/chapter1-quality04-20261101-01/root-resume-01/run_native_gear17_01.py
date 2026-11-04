from pathlib import Path
import subprocess,json,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17/runtime/native-gear01';assert not OUT.exists();OUT.mkdir(parents=True)
build=json.loads((B/'full17/build/build.json').read_text(encoding='utf-8'));exe=Path(build['exe']);assert hashlib.sha256(exe.read_bytes()).hexdigest()==build['sha256']
cmd=[str(exe),'--script',str(Path(__file__).with_name('native_gear17.gd')),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-qa-ignore-focus','--chapter1-quit-after=180']
with (OUT/'stdout.txt').open('xb') as o,(OUT/'stderr.txt').open('xb') as e:
 p=subprocess.Popen(cmd,stdout=o,stderr=e);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'sha256':build['sha256']},indent=2),encoding='utf-8');print(p.pid,flush=True);code=p.wait(timeout=240)
(OUT/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size},indent=2),encoding='utf-8');print(code,flush=True)
