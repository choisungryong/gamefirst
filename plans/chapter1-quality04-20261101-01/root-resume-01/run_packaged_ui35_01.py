from pathlib import Path
import json,hashlib,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full35/runtime/ui01';H=Path(__file__).parent
assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full35/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256']
script=H/'packaged_ui35.gd'
cmd=[str(exe),'--script',str(script),'--resolution','1920x1080','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(script)},indent=2));print('GPU',p.pid,flush=True);code=p.wait(timeout=180)
r={'actual_exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size};(O/'execution.json').write_text(json.dumps(r));assert r=={'actual_exit':0,'stderr_bytes':0},r
assert read(O/'RESULT.json')['core_unchanged']
a=read(B/'full35/ADOPTION.json');preserved={'source35':all(sha(R/n)==h for n,h in read(B/'full35/FINAL-SOURCE-FREEZE.json').items()),'previous_exes':all(sha(R/n)==h for n,h in a['preserved_exes'].items()),'user_pins':all(sha(Path(n))==h for n,h in a['user_pins'].items())};assert all(preserved.values());(O/'PRESERVATION.json').write_text(json.dumps(preserved,indent=2));print('PACKAGED UI35 QUIET; VISUAL REVIEW PENDING',flush=True)
