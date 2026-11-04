from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=B/'presentation17/review01';assert not OUT.exists();OUT.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(B/'full16/build/staging-manifest.json');old=Path(read(B/'full16/build/closure.json')['stage']);engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def run(label,args,stage):
 with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
  cmd=[engine,'--path',str(stage)]+args;p=subprocess.Popen(cmd,stdout=o,stderr=e);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(label,p.pid,flush=True);code=p.wait(timeout=180)
 report={'exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,(label,report)
results={}
for variant in ['before16','after17']:
 stage=Path('C:/Project/game-research/build-staging/chapter1-presentation17-review01-'+variant);assert not stage.exists();stage.mkdir()
 for n,h in pins.items():
  assert sha(old/n)==h
  p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
 if variant=='after17':
  for name in ['chapter_hud_quality17.gd','equipment_sigil_quality17.gd','chapter_actors_quality17.gd','chapter_world_quality17.gd']:shutil.copy2(R/'chapter1/view'/name,stage/'chapter1/view'/name)
  p=stage/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8')
  for a,b in [('chapter_hud_quality16','chapter_hud_quality17'),('chapter_actors_quality16','chapter_actors_quality17'),('chapter_world_quality10','chapter_world_quality17')]:s=s.replace(a,b)
  p.write_text(s,encoding='utf-8')
 shutil.copy2(HERE/'presentation17_review.gd',stage/'review.gd');(stage/'Review.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://review.gd" id="1"]\n[node name="Review" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
 frozen={str(p.relative_to(stage)).replace('\\','/'):sha(p) for p in stage.rglob('*') if p.is_file()};write(OUT/(variant+'-source.json'),{'stage':str(stage),'pins':frozen})
 run(variant+'-import',['--headless','--editor','--import'],stage)
 run(variant+'-check',['--headless','--check-only','--script','res://review.gd'],stage)
 results[variant]={}
 for scenario,seconds in [('combat',4),('ending',5)]:
  run(variant+'-'+scenario,['res://Review.tscn','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after='+str(seconds),'--review-scenario='+scenario],stage)
  results[variant][scenario]={}
  for name in ['start','end','checks']:
   p=stage/(scenario+'-'+name+'.json');results[variant][scenario][name]=read(p);shutil.copy2(p,OUT/(variant+'-'+p.name))
  shutil.copytree(stage/(scenario+'-shots'),OUT/(variant+'-'+scenario+'-shots'))
 assert all(sha(stage/n)==h for n,h in frozen.items())
same={s:{p:results['before16'][s][p]==results['after17'][s][p] for p in ['start','end']} for s in ['combat','ending']}
write(OUT/'RESULT.json',{'same_core':same,'after_checks':results['after17']['ending']['checks'],'scope':'Normal earned-growth pilot90131 core resimulated to54s/near victory then short fixed60 GPU presentation replay. No HP/item grants, not realtime/fullchapter/manual/audio/performance approval.'})
assert all(v for row in same.values() for v in row.values())
assert all(results['after17']['ending']['checks'].values())
print('PASS',flush=True)
