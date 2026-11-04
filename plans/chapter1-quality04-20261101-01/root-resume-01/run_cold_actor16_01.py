from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline'); BASE=ROOT/'plans/chapter1-quality04-20261101-01'; HERE=Path(__file__).parent
OUT=BASE/'cold16/actors01'; assert not OUT.exists(); OUT.mkdir()
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def run(label,cmd):
 with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
  p=subprocess.Popen(cmd,stdout=o,stderr=e);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(label,p.pid,flush=True); code=p.wait(timeout=240)
 result={'exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),result)
 assert code==0 and result['stderr_bytes']==0,(label,result)
pins=json.loads((BASE/'cold16/normal01/source.json').read_text(encoding='utf-8'));old=Path(pins['stage']);results={}
freeze=json.loads((BASE/'full14/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/n)==h for n,h in freeze.items())
exe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'
assert sha(exe)=='5fa58077545ea3cc3c0d55bc6abbd5bc57eab32bdd78c8ccdbfa398ca28f5952'
for variant in ['before','after']:
 stage=Path('C:/Project/game-research/build-staging/chapter1-cold16-actors01-'+variant);assert not stage.exists();stage.mkdir()
 for n,h in pins['pins'].items():
  assert sha(old/n)==h
  p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
 if variant=='after':
  n='chapter1/view/chapter_actors_quality16.gd';shutil.copy2(ROOT/n,stage/n)
  p=stage/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('chapter_actors_quality12.gd','chapter_actors_quality16.gd'),encoding='utf-8')
 shutil.copy2(HERE/'cold_actor16_replay.gd',stage/'actor_replay.gd')
 (stage/'ActorReplay.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://actor_replay.gd" id="1"]\n[node name="ActorReplay" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
 frozen={str(p.relative_to(stage)).replace('\\','/'):sha(p) for p in stage.rglob('*') if p.is_file()};write(OUT/(variant+'-source.json'),{'stage':str(stage),'pins':frozen})
 run(variant+'-import',[ENGINE,'--headless','--path',str(stage),'--editor','--import'])
 run(variant+'-check',[ENGINE,'--headless','--path',str(stage),'--check-only','--script','res://actor_replay.gd'])
 run(variant+'-gpu',[ENGINE,'--path',str(stage),'res://ActorReplay.tscn','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-qa-ignore-focus','--chapter1-quit-after=8'])
 results[variant]={}
 for name in ['start','end','checks']:
  value=json.loads((stage/(name+'.json')).read_text(encoding='utf-8'));results[variant][name]=value;write(OUT/(variant+'-'+name+'.json'),value)
 shutil.copytree(stage/'shots',OUT/(variant+'-shots'))
 assert all(sha(stage/n)==h for n,h in frozen.items())
assert results['before']['start']==results['after']['start']
assert results['before']['end']==results['after']['end']
assert results['after']['checks'] and all(results['after']['checks'].values()),results['after']['checks']
assert all(sha(ROOT/n)==h for n,h in freeze.items()) and sha(exe)=='5fa58077545ea3cc3c0d55bc6abbd5bc57eab32bdd78c8ccdbfa398ca28f5952'
write(OUT/'RESULT.json',{'same_full_core_start_and_end':True,'candidate14_preserved':True,'checks':results['after']['checks'],'scope':'Same cold16 rules, defaultHP/earned growth/ordinary policy seed90131. Resimulated to tick3240, clear cosmetics, then 8s GPU fixed60 replay. Not realtime/fullchapter/manual/audio/performance/art approval.'})
print('PASS',flush=True)
