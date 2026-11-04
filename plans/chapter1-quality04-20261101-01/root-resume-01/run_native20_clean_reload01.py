from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full20/runtime/native-clean-reload01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full20/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256']
profile=exe.parent/'plans/chapter1-quality04-20261101-01/qa-native20-clean01/profile.json';before=profile.read_bytes();state=read(profile);assert len(state['items'])==34 and state['revision']==1;shutil.copy2(profile,O/'profile-before.json')
capture=exe.parent/'qa-captures/native-clean-reload01';assert not capture.exists()
cmd=[str(exe),'--script',str(H/'native20_clean01.gd'),'--max-fps','120','--','--native20-reload','--chapter1-profile-off','--chapter1-qa-ignore-focus','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=2']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'native20_clean01.gd')},indent=2),encoding='utf-8');print('native-clean-reload01',p.pid,flush=True);code=p.wait(timeout=30)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8');assert code==0 and (O/'stderr.txt').stat().st_size==0
logs=(O/'stdout.txt').read_text(encoding='utf-8');boot=json.loads(next(s.split('NATIVE20_READY ',1)[1] for s in logs.splitlines() if 'NATIVE20_READY ' in s));assert boot['items']==34 and boot['revision']==1
assert profile.read_bytes()==before;shutil.copy2(profile,O/'profile-after.json');shutil.copytree(capture,O/'captures')
(O/'RESULT.json').write_text(json.dumps({'loaded_items':34,'revision':1,'unchanged_profile':True,'exe_preserved':sha(exe)==build['sha256'],'scope':'Actual package20 QA absolute-path profile reload/menu capture; no default-user-path/manual/fullrun approval.'},indent=2),encoding='utf-8');print('PASS',flush=True)
