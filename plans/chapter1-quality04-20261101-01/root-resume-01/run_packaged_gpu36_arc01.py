from pathlib import Path
import json,subprocess,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=B/'full36/runtime/gpu-arc01';assert not OUT.exists();OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
build=read(B/'full36/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];script=HERE/'packaged_gpu36.gd'
def write(p,v):assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def run(label,args):
 cmd=[str(exe)]+args
 with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
  p=subprocess.Popen(cmd,stdout=o,stderr=e,cwd=exe.parent);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(script)});print(label,p.pid,flush=True);code=p.wait(timeout=510)
 report={'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,(label,report)
 return (OUT/(label+'.stdout.txt')).read_text(encoding='utf-8')
common=['--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-primary=chapter1.skill.arc','--chapter1-seed=90131','--chapter1-qa-ignore-focus']
smoke=run('observer-smoke',['--headless','--fixed-fps','60','--script',str(script)]+common+['--chapter1-quit-after=65'])
obs=[json.loads(s.split('PACKAGED36_GPU_OBSERVER ',1)[1]) for s in smoke.splitlines() if 'PACKAGED36_GPU_OBSERVER ' in s][-1]
write(OUT/'observer-smoke-result.json',obs);assert obs['counts']['epoch']==1
capture=exe.parent/'qa-captures/gpu-arc01';assert not capture.exists()
logs=run('gpu',['--script',str(script),'--max-fps','120']+common+['--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=450'])
shutil.copytree(capture,OUT/'captures')
rows=[json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for s in logs.splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in s];first=next(r for r in rows if r['mode']=='victory')
ref=next(r['snapshot'] for r in read(B/'balance36/normal01/RESULT.json')['results'] if r['primary']=='chapter1.skill.arc' and r['repetition']==0);keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];same={k:first[k]==ref[k] for k in keys};assert all(same.values())
obs=[json.loads(s.split('PACKAGED36_GPU_OBSERVER ',1)[1]) for s in logs.splitlines() if 'PACKAGED36_GPU_OBSERVER ' in s][-1]
assert not obs['mismatches'] and obs['pool_hits']>1000 and obs['pool_size']<=224
assert len(obs['zones'])==3 and all(z['columns_enabled'] and z['column_count']==33 and z['shadow_batches']==2 and z['world_script']=='res://chapter1/view/chapter_world_quality31d.gd' for z in obs['zones'].values())
assert obs['counts']['epoch']==1
assert {'common','magic','rare'}.issubset(set(obs['ground_rarities'].values())) and obs['plume_peak']>0 and obs['fx_script']=='res://chapter1/view/chapter_elements_quality36.gd'
assert obs['family34_seen_count']>1000 and obs['actor_script']=='res://chapter1/view/chapter_actors_quality36.gd'
assert obs['hud_script']=='res://chapter1/view/chapter_hud_quality36.gd' and len(obs['discovery_history'])>0
assert obs['core_script']=='res://chapter1/core/chapter_run_quality36.gd' and obs['stun_events']>0 and 0<obs['stun_visible_peak']<=48 and 0<=obs['world_unique_count']<=2
write(OUT/'RESULT.json',{'first_victory':first,'same10_as_source36':same,'observer':obs,'captures':len(list((OUT/'captures').glob('*.png'))),'scope':'Actual packaged36 GPU normal earned-growth policy. Not manual/heard audio/formal performance/final-art approval.'})
assert sha(exe)==build['sha256'];print('PASS GPU36',flush=True)
