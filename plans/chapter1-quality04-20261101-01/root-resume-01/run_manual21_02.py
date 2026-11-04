from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full21/runtime/manual02';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full21/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];capture=exe.parent/'qa-captures/manual02';assert not capture.exists()
cmd=[str(exe),'--script',str(H/'manual21_observer.gd'),'--max-fps','120','--','--chapter1-profile-off','--chapter1-qa-ignore-focus','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=1800']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'manual21_observer.gd')},indent=2),encoding='utf-8');print('manual21',p.pid,flush=True);code=p.wait(timeout=1920)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8')
if capture.exists():shutil.copytree(capture,O/'captures')
rows=[json.loads(s.split('MANUAL21_FINAL ',1)[1]) for s in (O/'stdout.txt').read_text(encoding='utf-8').splitlines() if 'MANUAL21_FINAL ' in s]
if rows:(O/'RESULT.json').write_text(json.dumps(rows[-1],ensure_ascii=False,indent=2),encoding='utf-8')
assert sha(exe)==build['sha256'];assert code==0 and (O/'stderr.txt').stat().st_size==0;print('MANUAL TERMINAL',flush=True)
