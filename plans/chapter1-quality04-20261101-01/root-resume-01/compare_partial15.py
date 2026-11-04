from pathlib import Path
import json,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'elements15/compare14-partial01';assert not OUT.exists();OUT.mkdir()
exe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'
cmd=[str(exe),'--headless','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=190']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'pid':p.pid}),flush=True);code=p.wait(timeout=120)
r={'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(r,indent=2),encoding='utf-8');assert code==0 and not r['stderr_bytes'],r
def state(path):return[json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1])for s in path.read_text(encoding='utf-8').splitlines()if'FULL_CHAPTER_RUNTIME_RESULT 'in s][-1]
a=state(OUT/'stdout.txt');b=state(BASE/'elements15/normal01/gpu.stdout.txt');keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];same={k:a[k]==b[k]for k in keys};assert all(same.values()),same
(OUT/'RESULT.json').write_text(json.dumps({'same':same,'before14':a,'after_source15':b,'scope':'Same normal defaultHP/progression/pilot/coldseed90131,190seconds partial: packaged14headless vs source15actualGPU. Not15packaged/fullchapter/manual/performance proof.'},indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({'same':same,'tick':b['tick'],'kills':b['kills']}),flush=True)
