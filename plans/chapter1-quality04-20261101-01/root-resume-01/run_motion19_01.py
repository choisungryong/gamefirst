from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=B/'motion19/replay01';assert not OUT.exists();OUT.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';old=Path(read(B/'full18/build/closure.json')['stage']);pins=read(B/'full18/build/staging-manifest.json');results={}
freeze=read(B/'full18/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def run(label,args,stage):
 with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
  cmd=[engine,'--path',str(stage)]+args;p=subprocess.Popen(cmd,stdout=o,stderr=e);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(label,p.pid,flush=True);code=p.wait(timeout=180)
 report={'exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,(label,report)
for variant in ['sprite18','rig19']:
 stage=Path('C:/Project/game-research/build-staging/chapter1-motion19-replay01-'+variant);assert not stage.exists();stage.mkdir()
 for n,h in pins.items():
  assert sha(old/n)==h
  p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
 if variant=='rig19':
  for n in ['chapter1/view/chapter_actors_motion19.gd','assets/actors/Skeleton_Minion.glb','assets/licenses/skeletons-LICENSE.txt','presentation/skinned_mesh_batch.gd']:
   p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
  p=stage/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('chapter_actors_quality17.gd','chapter_actors_motion19.gd'),encoding='utf-8')
 shutil.copy2(HERE/'motion19_replay.gd',stage/'replay.gd');(stage/'Replay.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://replay.gd" id="1"]\n[node name="Replay" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
 frozen={str(p.relative_to(stage)).replace('\\','/'):sha(p) for p in stage.rglob('*') if p.is_file()};write(OUT/(variant+'-source.json'),{'stage':str(stage),'pins':frozen})
 run(variant+'-import',['--headless','--editor','--import'],stage)
 run(variant+'-check',['--headless','--check-only','--script','res://replay.gd'],stage)
 run(variant+'-gpu',['res://Replay.tscn','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=8'],stage)
 results[variant]={}
 for name in ['start','end','visual']:
  p=stage/('motion19-'+name+'.json');results[variant][name]=read(p);shutil.copy2(p,OUT/(variant+'-'+name+'.json'))
 shutil.copytree(stage/'motion19-shots',OUT/(variant+'-shots'));assert all(sha(stage/n)==h for n,h in frozen.items())
same={key:results['sprite18'][key]==results['rig19'][key] for key in ['start','end']};assert all(same.values());assert results['rig19']['visual']['rigs']>0
assert all(sha(R/n)==h for n,h in freeze.items())
write(OUT/'RESULT.json',{'same_full_core':same,'rig_visual':results['rig19']['visual'],'candidate18_freeze_preserved':True,'scope':'Both normal-policy defaultHP/earned growth core replays from6500ticks then8s fixed60GPU. No game-rule changes, no manual/fullrun/performance/art approval.'});print('PASS',flush=True)
