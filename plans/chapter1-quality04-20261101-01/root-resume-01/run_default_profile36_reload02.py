from pathlib import Path
import json,subprocess,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full36/runtime/default-profile-reload02';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins=read(B/'full36/USER-PRESERVATION-ADDENDUM01.json')['user_pins'];assert all(sha(Path(n))==h for n,h in pins.items());build=read(B/'full36/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];script=H/'default_profile36_reload02.gd'
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 cmd=[str(exe),'--headless','--verbose','--script',str(script)];p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'observer_sha256':sha(script),'exe_sha256':sha(exe)},indent=2));code=p.wait(timeout=60)
r={'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size};(O/'execution.json').write_text(json.dumps(r));assert all(sha(Path(n))==h for n,h in pins.items());(O/'PRESERVATION.json').write_text(json.dumps({'all23_29_36_pins_unchanged':True}));print(r,flush=True);assert r=={'exit':0,'stderr_bytes':0},r
assert read(O/'RESULT.json')['same_profile_after_process_restart'];print('ACTUAL36 SEPARATE-PROCESS DEFAULT LOAD QUIET',flush=True)
