from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'cold16/actor-exclusions04';STAGE=Path('C:/Project/game-research/build-staging/chapter1-cold16-actor-exclusions04')
assert not OUT.exists() and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
source=json.loads((BASE/'cold16/actors01/after-source.json').read_text(encoding='utf-8'));old=Path(source['stage']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in source['pins'].items():
 assert sha(old/n)==h
 p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(Path(__file__).with_name('cold_actor16_exclusions.gd'),STAGE/'exclusions.gd')
(STAGE/'Exclusions.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://exclusions.gd" id="1"]\n[node name="Exclusions" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
(OUT/'source.json').write_text(json.dumps({'stage':str(STAGE),'pins':{str(p.relative_to(STAGE)).replace('\\','/'):sha(p) for p in STAGE.rglob('*') if p.is_file()}},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--editor','--import']),('fixtures',['res://Exclusions.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.frost'])]:
 with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
  p=subprocess.run([engine,'--verbose','--headless','--path',str(STAGE)]+args,stdout=o,stderr=e,timeout=120)
 result={'exit':p.returncode,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};(OUT/(label+'-execution.json')).write_text(json.dumps(result,indent=2));print(label,result,flush=True);assert p.returncode==0 and result['stderr_bytes']==0
shutil.copy2(STAGE/'exclusions-result.json',OUT/'RESULT.json')



