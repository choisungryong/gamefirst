from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full21/runtime/native-input01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full21/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];capture=exe.parent/'qa-captures/native-input01';assert not capture.exists()
cmd=[str(exe),'--script',str(H/'native_input21.gd'),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=360']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'native_input21.gd')},indent=2),encoding='utf-8');print('native-input21',p.pid,flush=True);code=p.wait(timeout=480)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8');assert code==0 and (O/'stderr.txt').stat().st_size==0
rows=[json.loads(s.split('NATIVE21_CLICK ',1)[1]) for s in (O/'stdout.txt').read_text(encoding='utf-8').splitlines() if 'NATIVE21_CLICK ' in s]
assert {r['zone'] for r in rows}=={1,2} and all(r['correct_target'] and r['moved_toward'] for r in rows)
shutil.copytree(capture,O/'captures');assert sha(exe)==build['sha256']
(O/'RESULT.json').write_text(json.dumps({'records':rows,'scope':'Actual package21/native mouse event -> target -> normal controller movement in two later-zone checkpoint fixtures. No manual/fullrun/performance approval.'},ensure_ascii=False,indent=2),encoding='utf-8');print('PASS',flush=True)
