from pathlib import Path
import json,subprocess,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01/boss-research12'
OUT=BASE/'fixture03';STAGE=Path('C:/Project/game-research/build-staging/chapter1-warden-research-20261101-03')
assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
old=json.loads((BASE/'stage-manifest.json').read_text(encoding='utf-8'));previous=Path(old['stage'])
for name in old['runtime_pins']:
 target=STAGE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(previous/name,target)
for name in ['chapter1/view/chapter_actors_quality12.gd','chapter1/art/chained_warden/v01/chained_demon_animated.glb','chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md']:
 shutil.copy2(ROOT/name,STAGE/name)
shutil.copy2(Path(__file__).with_name('warden_fixture12.gd'),STAGE/'warden_fixture.gd')
p=STAGE/'warden_fixture.gd';p.write_text(p.read_text(encoding='utf-8').replace('fixture01/captures','fixture03/captures'),encoding='utf-8')
p=STAGE/'project.godot';p.write_text(p.read_text(encoding='utf-8').replace('Ashen Cloister ChapterOne Quality11','Warden visual research12').replace('AshenCloisterChapterOneQuality11','AshenCloisterWardenResearch12Fixture03'),encoding='utf-8')
with(OUT/'stage-manifest.json').open('x',encoding='utf-8')as f:json.dump({'stage':str(STAGE),'changes':['separate mask/chain/skin response, darker body and1.15 model scale; paused/frozen pose guard and73bone freeze check','unique research user/log namespace, all profiles still off'],'runtime_pins':{str(p.relative_to(STAGE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in STAGE.rglob('*')if p.is_file()}},f,indent=2)
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://warden_fixture.gd']),('fixture',['res://WardenFixture.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=15.3'])]:
 command=[engine,'--path',str(STAGE)]+args
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(command,stdout=stdout,stderr=stderr)
  with(OUT/(label+'-launch.json')).open('x',encoding='utf-8')as f:json.dump({'pid':p.pid,'command':command},f,indent=2)
  print(json.dumps({'label':label,'pid':p.pid}),flush=True)
  try:code=p.wait(timeout=120)
  except subprocess.TimeoutExpired:p.kill();p.wait();raise
 with(OUT/(label+'-execution.json')).open('x',encoding='utf-8')as f:json.dump({'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size},f,indent=2)
 print(json.dumps({'label':label,'actual_exit':code,'stderr':(OUT/(label+'.stderr.txt')).read_text(encoding='utf-8',errors='replace')[:1800]}),flush=True)
 if code!=0 or (OUT/(label+'.stderr.txt')).stat().st_size:raise RuntimeError(label)
capture=STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/fixture03/captures'
if capture.exists():shutil.copytree(capture,OUT/'captures')
