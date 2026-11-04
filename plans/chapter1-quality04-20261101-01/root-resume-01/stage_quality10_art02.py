from pathlib import Path
import json,shutil,subprocess,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/quality10-art02'
STAGE=Path('C:/Project/game-research/build-staging/chapter1-quality10-art02')
assert not OUT.exists() and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
previous=json.loads((OUT.parent/'rigged-hero-05/rigged05.source.json').read_text(encoding='utf-8'))
names=list(previous['source_before_injections'])+['chapter1/view/chapter_world_quality10.gd','chapter1/view/chapter_grass_quality10.gdshader']
for name in names:
 dest=STAGE/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
shutil.copy2(Path(previous['stage'])/'project.godot',STAGE/'project.godot')
p=STAGE/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('res://chapter1/view/chapter_actors.gd','res://chapter1/view/rigged_hero_actors.gd').replace('res://chapter1/view/chapter_world.gd','res://chapter1/view/chapter_world_quality10.gd'),encoding='utf-8')
p=STAGE/'chapter1/view/cloister_world_quality03.gd';p.write_text(p.read_text(encoding='utf-8').replace('moon.shadow_enabled=false','moon.shadow_enabled=true;moon.light_cull_mask=3'),encoding='utf-8')
with(OUT/'stage-manifest.json').open('x',encoding='utf-8')as f:json.dump({'stage':str(STAGE),'runtime_pins':{str(p.relative_to(STAGE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in STAGE.rglob('*')if p.is_file()}},f,indent=2)
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,cmd in [('import',[ENGINE,'--headless','--path',str(STAGE),'--editor','--import']),('preview',[ENGINE,'--path',str(STAGE),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-capture-dir='+str(STAGE/'plans/chapter1-quality04-20261101-01/quality10-art02/captures'),'--chapter1-quit-after=42'])]:
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr)
  with(OUT/(label+'.launch.json')).open('x',encoding='utf-8')as f:json.dump({'pid':p.pid,'command':cmd},f,indent=2)
  print(json.dumps({'label':label,'pid':p.pid}),flush=True)
  try:code=p.wait(timeout=180)
  except subprocess.TimeoutExpired:p.kill();p.wait();raise
 with(OUT/(label+'.execution.json')).open('x',encoding='utf-8')as f:json.dump({'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size},f,indent=2)
 if code!=0 or (OUT/(label+'.stderr.txt')).stat().st_size:raise RuntimeError((label,code))
capture=STAGE/'plans/chapter1-quality04-20261101-01/quality10-art02/captures'
if capture.exists():shutil.copytree(capture,OUT/'captures')
print(json.dumps({'complete':True}))

