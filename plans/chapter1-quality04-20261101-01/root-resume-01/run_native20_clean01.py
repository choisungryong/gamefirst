from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full20/runtime/native-clean01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full20/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256']
profile=exe.parent/'plans/chapter1-quality04-20261101-01/qa-native20-clean01/profile.json';assert not profile.exists()
capture=exe.parent/'qa-captures/native-clean01';assert not capture.exists()
cmd=[str(exe),'--script',str(H/'native20_clean01.gd'),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=20']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'native20_clean01.gd'),'qa_profile':str(profile)},indent=2),encoding='utf-8');print('native-clean01',p.pid,flush=True);code=p.wait(timeout=180)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8')
assert code==0 and (O/'stderr.txt').stat().st_size==0
shutil.copy2(profile,O/'profile-after-exit.json');shutil.copytree(capture,O/'captures')
logs=(O/'stdout.txt').read_text(encoding='utf-8');rows=[json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for s in logs.splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in s];first=next(r for r in rows if r['mode']=='victory')
ref=read(B/'full19/runtime/gpu-cold01/RESULT.json')['first_victory'];same={k:first[k]==ref[k] for k in ['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid']};assert all(same.values())
state=read(profile);assert len(state['items'])==34 and state['completed_runs']==1 and state['revision']==1
(O/'RESULT.json').write_text(json.dumps({'same10_as_full19':same,'profile_items':34,'completed_runs':1,'revision':1,'exe_preserved':sha(exe)==build['sha256'],'scope':'Actual package20 normal earned ending replay after23830 reconstruction; external QA path rebound to verified absolute physical location; quiet save/captures, not default user path/manual/fullrun/performance.'},indent=2),encoding='utf-8');print('PASS',flush=True)
