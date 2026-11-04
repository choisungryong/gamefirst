from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full23/runtime/default-reload01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full23/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256']
profile=Path(read(B/'full23/runtime/default-save02/RESULT.json')['default_path']);assert profile.parent.name=='AshenCloisterChapterOneQuality23'
state=read(profile);assert len(state['items'])==34 and state['revision']==1;shutil.copy2(profile,O/'profile-before.json')
capture=exe.parent/'qa-captures/default23-reload01';assert not capture.exists()
check=subprocess.run([str(exe),'--headless','--check-only','--script',str(H/'default23_reload.gd')],capture_output=True)
(O/'check.stdout.txt').write_bytes(check.stdout);(O/'check.stderr.txt').write_bytes(check.stderr);assert check.returncode==0 and not check.stderr
cmd=[str(exe),'--script',str(H/'default23_reload.gd'),'--max-fps','120','--','--default23-reload','--chapter1-qa-ignore-focus','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=600']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'default23_reload.gd')},indent=2),encoding='utf-8');print('default23-reload01',p.pid,flush=True);code=p.wait(timeout=660)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8');assert code==0 and (O/'stderr.txt').stat().st_size==0
logs=(O/'stdout.txt').read_text(encoding='utf-8');boot=json.loads(next(s.split('DEFAULT23_READY ',1)[1] for s in logs.splitlines() if 'DEFAULT23_READY ' in s));assert boot['items']==34 and boot['revision']==1
after=read(profile);assert after['revision']==2 and len(after['items'])==34 and after['completed_runs']==1 and len(after['equipped'])==1 and 'ring' in after['equipped']
gear=json.loads(next(s.split('DEFAULT23_RUNGEAR ',1)[1] for s in logs.splitlines() if 'DEFAULT23_RUNGEAR ' in s));assert 'ring' in gear['equipped']
shutil.copy2(profile,O/'profile-after.json');shutil.copytree(capture,O/'captures')
(O/'RESULT.json').write_text(json.dumps({'loaded_items':34,'before_revision':1,'after_revision':2,'selected':after['equipped'],'run_gear':gear,'default_path':str(profile),'scope':'Actual23 default user:// reload, actual native stash ring selection/save and starting-gear import. Not manual/fullrun or all save failures.'},ensure_ascii=False,indent=2),encoding='utf-8');print('PASS DEFAULT23 RELOAD/UI',flush=True)
