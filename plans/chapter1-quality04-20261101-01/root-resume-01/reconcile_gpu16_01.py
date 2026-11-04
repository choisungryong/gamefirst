from pathlib import Path
import json,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';P=B/'full16/runtime/gpu-cold01';OUT=B/'full16/runtime/gpu-cold01-review';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
logs=(P/'stdout.txt').read_text(encoding='utf-8').splitlines()
rows=[json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for s in logs if 'FULL_CHAPTER_RUNTIME_RESULT ' in s]
observers=[json.loads(s.split('PACKAGED16_GPU_OBSERVER ',1)[1]) for s in logs if 'PACKAGED16_GPU_OBSERVER ' in s]
first=next(r for r in rows if r['mode']=='victory');ref=read(B/'full16/build/full-frost-proof.json')['first_victory']
keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid']
same={k:first[k]==ref[k] for k in keys};assert all(same.values())
assert read(P/'execution.json')=={'actual_exit':0,'stderr_bytes':0}
launch=read(P/'launch.json');exe=Path(launch['command'][0]);assert sha(exe)==launch['exe_sha256']
report={'execution':read(P/'execution.json'),'first_victory':first,'same10_as_packaged_headless':same,'states':[{'mode':r['mode'],'tick':r['tick'],'kills':r['kills'],'epoch':r['epoch']} for r in rows],'observer_counts':observers[0]['counts'],'observer_valid':False,'helper_success':False,'reason':'Observer counts epoch=-1, shatters=1, cold_death_cause=0 do not satisfy helper expectations epoch1/shatters840. Preserve raw script/log; no duplicate run. Actual game first victory independently matches 10 packaged headless states. Do not claim package840 based on this observer.','capture_count':len(list((P/'captures').glob('*.png'))),'pins':{n:sha(P/n) for n in ['launch.json','execution.json','stdout.txt','stderr.txt']},'scope':'Completed actual packagedGPU normal earned-growth cold run; not manual/audio/performance/final art approval.'}
(OUT/'RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['first_victory','pins']},ensure_ascii=False))
