from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17b/runtime/boundary01';assert not OUT.exists();OUT.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=read(B/'full17b/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256']
capture=exe.parent/'qa-captures/boundary01';assert not capture.exists()
cmd=[str(exe),'--script',str(Path(__file__).with_name('boundary17b.gd')),'--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=2','--chapter1-capture-dir='+str(capture)]
with (OUT/'stdout.txt').open('xb') as o,(OUT/'stderr.txt').open('xb') as e:
 p=subprocess.Popen(cmd,stdout=o,stderr=e);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':build['sha256']},indent=2));print(p.pid,flush=True);code=p.wait(timeout=60)
execution={'exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(execution,indent=2));assert code==0 and execution['stderr_bytes']==0
shutil.copytree(capture,OUT/'captures');rows=(OUT/'stdout.txt').read_text(encoding='utf-8').splitlines();result=next(json.loads(s.split('BOUNDARY17B ',1)[1]) for s in rows if 'BOUNDARY17B ' in s)
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');assert result['core_boundary_19'] and result['all_stones_outside_walkable_plus_0_8'] and result['core_queries_unchanged'] and result['stones']==114 and result['stone_batches']==6
print(json.dumps(result),flush=True)
