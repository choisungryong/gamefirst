from pathlib import Path
import json,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full14/cold-reference13';assert not OUT.exists();OUT.mkdir()
exe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-13/AshenCloister-Chapter1.exe'
cmd=[str(exe),'--headless','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=500']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'pid':p.pid}),flush=True);code=p.wait(timeout=180)
report={'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(report,indent=2),encoding='utf-8');assert code==0 and not report['stderr_bytes'],report
def victory(path):return next(json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1])for s in path.read_text(encoding='utf-8').splitlines()if 'FULL_CHAPTER_RUNTIME_RESULT 'in s and json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1])['mode']=='victory')
a=victory(OUT/'stdout.txt');b=victory(BASE/'full14/runtime/gpu-cold01/stdout.txt')
keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];same={k:a[k]==b[k]for k in keys};assert all(same.values()),same
(OUT/'COMPARISON.json').write_text(json.dumps({'same':same,'before13':a,'after14':b,'scope':'Same primary frost and seed90131, packaged13 headless fixed60 vs14 realGPU normal policy; no manual/performance or same-seed comparison with old09seed71'},indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({'same':same,'tick':b['tick'],'kills':b['kills']}),flush=True)
