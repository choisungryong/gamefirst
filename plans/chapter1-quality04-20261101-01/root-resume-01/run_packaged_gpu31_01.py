from pathlib import Path
import json,subprocess,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=B/'full31/runtime/gpu-cold01';assert not OUT.exists();OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
build=read(B/'full31/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];script=HERE/'packaged_gpu31.gd'
def write(p,v):assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def run(label,args):
 cmd=[str(exe)]+args
 with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
  p=subprocess.Popen(cmd,stdout=o,stderr=e,cwd=exe.parent);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(script)});print(label,p.pid,flush=True);code=p.wait(timeout=510)
 report={'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,(label,report)
 return (OUT/(label+'.stdout.txt')).read_text(encoding='utf-8')
common=['--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-qa-ignore-focus']
smoke=run('observer-smoke',['--headless','--fixed-fps','60','--script',str(script)]+common+['--chapter1-quit-after=65'])
obs=[json.loads(s.split('PACKAGED31_GPU_OBSERVER ',1)[1]) for s in smoke.splitlines() if 'PACKAGED31_GPU_OBSERVER ' in s][-1]
write(OUT/'observer-smoke-result.json',obs);assert obs['counts']['epoch']==1 and obs['counts']['shatters']>0
capture=exe.parent/'qa-captures/gpu-cold01';assert not capture.exists()
logs=run('gpu',['--script',str(script),'--max-fps','120']+common+['--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=450'])
shutil.copytree(capture,OUT/'captures')
rows=[json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for s in logs.splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in s];first=next(r for r in rows if r['mode']=='victory')
ref=read(B/'full16/build/full-frost-proof.json')['first_victory'];keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];same={k:first[k]==ref[k] for k in keys};assert all(same.values())
obs=[json.loads(s.split('PACKAGED31_GPU_OBSERVER ',1)[1]) for s in logs.splitlines() if 'PACKAGED31_GPU_OBSERVER ' in s][-1]
assert not obs['mismatches'] and obs['pool_hits']>1000 and obs['pool_size']<=224
assert len(obs['zones'])==3 and all(z['columns_enabled'] and z['column_count']==33 and z['shadow_batches']==2 and z['world_script']=='res://chapter1/view/chapter_world_quality31d.gd' for z in obs['zones'].values())
write(OUT/'RESULT.json',{'first_victory':first,'same10_as_packaged16':same,'observer':obs,'captures':len(list((OUT/'captures').glob('*.png'))),'scope':'Actual packaged31 GPU normal earned-growth policy. Not manual/heard audio/formal performance/final-art approval.'})
assert obs['counts']['epoch']==1 and obs['counts']['shatters']==840
assert sha(exe)==build['sha256'];print('PASS GPU31',flush=True)
