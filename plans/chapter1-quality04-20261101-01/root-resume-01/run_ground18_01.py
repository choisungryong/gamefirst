from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=B/'ground18/matrix01';STAGE=Path('C:/Project/game-research/build-staging/chapter1-ground18-matrix01');assert not OUT.exists() and not STAGE.exists();OUT.mkdir(parents=True);STAGE.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path(read(B/'full17b/build/closure.json')['stage']);pins=read(B/'full17b/build/staging-manifest.json')
for n,h in pins.items():
 assert sha(old/n)==h
 p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
n='chapter1/view/chapter_world_quality18.gd';shutil.copy2(R/n,STAGE/n)
p=STAGE/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('chapter_world_quality17.gd','chapter_world_quality18.gd'),encoding='utf-8')
shutil.copy2(HERE/'ground18_matrix.gd',STAGE/'matrix.gd');(STAGE/'Matrix.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://matrix.gd" id="1"]\n[node name="Matrix" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
frozen={str(p.relative_to(STAGE)).replace('\\','/'):sha(p) for p in STAGE.rglob('*') if p.is_file()};(OUT/'source.json').write_text(json.dumps({'stage':str(STAGE),'pins':frozen},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://matrix.gd']),('gpu',['res://Matrix.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus'])]:
 with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
  cmd=[engine,'--path',str(STAGE)]+args;p=subprocess.Popen(cmd,stdout=o,stderr=e);(OUT/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result={'exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};(OUT/(label+'-execution.json')).write_text(json.dumps(result,indent=2));assert code==0 and result['stderr_bytes']==0,(label,result)
shutil.copy2(STAGE/'ground18-result.json',OUT/'RESULT.json');shutil.copytree(STAGE/'ground18-shots',OUT/'shots');assert all(sha(STAGE/n)==h for n,h in frozen.items());print('PASS',flush=True)
