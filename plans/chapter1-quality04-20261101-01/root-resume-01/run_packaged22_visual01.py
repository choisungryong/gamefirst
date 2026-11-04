from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full22/runtime/visual01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full22/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];capture=exe.parent/'qa-captures/visual22-01';assert not capture.exists()
cmd=[str(exe),'--script',str(H/'packaged22_visual.gd'),'--resolution','1920x1080','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'packaged22_visual.gd')},indent=2),encoding='utf-8');print('packaged22-visual',p.pid,flush=True);code=p.wait(timeout=240)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8');assert code==0 and (O/'stderr.txt').stat().st_size==0
rows=[json.loads(s.split('PACKAGED22_VISUAL ',1)[1]) for s in (O/'stdout.txt').read_text(encoding='utf-8').splitlines() if 'PACKAGED22_VISUAL ' in s];assert len(rows)==1
d=rows[0];assert d['same_complete_core'] and 'quality22' in d['world_script'] and 'quality22' in d['fx_script'] and len(d['shots'])==3
shutil.copytree(capture,O/'captures');assert sha(exe)==build['sha256']
(O/'RESULT.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print('PASS ACTUAL22 VISUAL',flush=True)
