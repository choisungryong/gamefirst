from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full26/runtime/manual01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full26/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];capture=exe.parent/'qa-captures/manual01';assert not capture.exists()
profile_pins=read(B/'full23/runtime/default-profile-preserved.json');profile_root=Path(profile_pins['path']);assert all(sha(profile_root/n)==v for n,v in profile_pins['pins'].items())
cmd=[str(exe),'--script',str(H/'manual26_observer.gd'),'--max-fps','120','--','--chapter1-profile-off','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=3600']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'manual26_observer.gd')},indent=2),encoding='utf-8');print('manual26',p.pid,flush=True);code=p.wait(timeout=3720)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8')
if capture.exists():shutil.copytree(capture,O/'captures')
rows=[json.loads(s.split('MANUAL26_FINAL ',1)[1]) for s in (O/'stdout.txt').read_text(encoding='utf-8').splitlines() if 'MANUAL26_FINAL ' in s]
if rows:(O/'RESULT.json').write_text(json.dumps(rows[-1],ensure_ascii=False,indent=2),encoding='utf-8')
assert all(sha(profile_root/n)==v for n,v in profile_pins['pins'].items());assert sha(exe)==build['sha256'];assert code==0 and (O/'stderr.txt').stat().st_size==0;print('MANUAL TERMINAL',flush=True)
