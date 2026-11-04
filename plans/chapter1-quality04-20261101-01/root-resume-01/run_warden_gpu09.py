from pathlib import Path
import json,shutil,subprocess,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01/boss-research12'
OUT=BASE/'gpu09';STAGE=Path('C:/Project/game-research/build-staging/chapter1-warden-gpu-20261101-09')
assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
old=json.loads((BASE/'fixture03/stage-manifest.json').read_text(encoding='utf-8'));previous=Path(old['stage'])
for name in old['runtime_pins']:
 p=STAGE/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(previous/name,p)
shutil.copy2(ROOT/'chapter1/view/chapter_actors_quality12.gd',STAGE/'chapter1/view/chapter_actors_quality12.gd')
p=STAGE/'project.godot';p.write_text(p.read_text(encoding='utf-8').replace('WardenResearch12Fixture03','WardenResearch13GPU09'),encoding='utf-8')
shutil.copy2(Path(__file__).with_name('warden_gpu_probe13b.gd'),STAGE/'visibility_probe.gd')
(STAGE/'VisibilityProbe.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://visibility_probe.gd" id="1"]\n[node name="VisibilityProbe" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
(STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/gpu09').mkdir(parents=True)
with(OUT/'stage-manifest.json').open('x',encoding='utf-8')as f:json.dump({'stage':str(STAGE),'scope':'Current posed-capsule coverage and stopped-core death probe; no normal play or performance','runtime_pins':{str(p.relative_to(STAGE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in STAGE.rglob('*')if p.is_file()}},f,indent=2)
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
(STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/gpu09/captures').mkdir()
for label,args in [('import',['--editor','--import']),('check',['--check-only','--script','res://visibility_probe.gd']),('probe',['res://VisibilityProbe.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus'])]:
 command=[engine]+([] if label=='probe' else ['--headless'])+['--path',str(STAGE)]+args
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(command,stdout=stdout,stderr=stderr)
  with(OUT/(label+'-launch.json')).open('x',encoding='utf-8')as f:json.dump({'pid':p.pid,'command':command},f,indent=2)
  print(json.dumps({'label':label,'pid':p.pid}),flush=True)
  try:code=p.wait(timeout=120)
  except subprocess.TimeoutExpired:p.kill();p.wait();raise
 with(OUT/(label+'-execution.json')).open('x',encoding='utf-8')as f:json.dump({'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size},f,indent=2)
 print(json.dumps({'label':label,'actual_exit':code,'stderr':(OUT/(label+'.stderr.txt')).read_text(encoding='utf-8',errors='replace')[:1600]}),flush=True)
 if code!=0 or (OUT/(label+'.stderr.txt')).stat().st_size:raise RuntimeError(label)
result=STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/gpu09/result.json'
shutil.copy2(result,OUT/'result.json')
print((OUT/'result.json').read_text(encoding='utf-8'))

shutil.copytree(STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/gpu09/captures',OUT/'captures')
