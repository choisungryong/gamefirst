"""Own-game GPU offline comparison. Never modify an archived stage or build."""
from pathlib import Path
import json,shutil,subprocess,hashlib,time
ROOT=Path('C:/Project/d2r-combat-baseline')
OUT=ROOT/'plans/chapter1-quality04-20261101-01/rigged-hero-05'
assert not OUT.exists();OUT.mkdir()
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
closure=json.loads((OUT.parent/'full09/build/closure.json').read_text(encoding='utf-8'))['runtime_source_files']
freeze=json.loads((OUT.parent/'full09/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert all(sha(ROOT/name)==digest for name,digest in freeze.items())
extras=['chapter1/view/rigged_hero_actors.gd','chapter1/view/ember_staff_visual.gd','chapter1/art/rigged_mage/v01/mage_animated.glb','chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md']
project_source=Path('C:/Project/game-research/build-staging/rigged-hero-20261101-04/project.godot')
def write(p,data):
 with p.open('x',encoding='utf-8')as f:json.dump(data,f,indent=2,ensure_ascii=False)
def run(label,cmd,timeout=180):
 start=time.time()
 with (OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr)
  write(OUT/(label+'.launch.json'),{'pid':p.pid,'command':cmd})
  print(json.dumps({'label':label,'pid':p.pid}),flush=True)
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   p.kill();code=p.wait();write(OUT/(label+'.timeout.json'),{'timeout':timeout,'forced_exit':code});raise
 result={'actual_exit':code,'wall_seconds':time.time()-start,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size}
 write(OUT/(label+'.execution.json'),result)
 if code!=0 or result['stderr_bytes']!=0:raise RuntimeError((label,result))
 return result
results={}
for variant in ['sprite09','rigged05']:
 stage=Path('C:/Project/game-research/build-staging/hero-comparison-20261101-05-'+variant)
 assert not stage.exists();stage.mkdir()
 names=closure+(extras if variant=='rigged05' else [])
 for name in names:
  dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
 before={name:sha(stage/name)for name in names}
 project=project_source.read_text(encoding='utf-8').replace('viewport_width=1600','viewport_width=1280').replace('viewport_height=900','viewport_height=720').replace('window_width_override=1440','window_width_override=1280').replace('window_height_override=810','window_height_override=720')
 (stage/'project.godot').write_text(project,encoding='utf-8')
 if variant=='rigged05':
  p=stage/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('res://chapter1/view/chapter_actors.gd','res://chapter1/view/rigged_hero_actors.gd'),encoding='utf-8')
  p=stage/'chapter1/view/cloister_world_quality03.gd';p.write_text(p.read_text(encoding='utf-8').replace('moon.shadow_enabled=false','moon.shadow_enabled=true;moon.light_cull_mask=3'),encoding='utf-8')
 pins={str(p.relative_to(stage)).replace('\\','/'):sha(p)for p in stage.rglob('*')if p.is_file()}
 write(OUT/(variant+'.source.json'),{'stage':str(stage),'source_before_injections':before,'runtime_pins':pins,'scope':'same core09, visual presenter and mesh lights/shadow changes only'})
 run(variant+'-import',[ENGINE,'--headless','--path',str(stage),'--editor','--import'])
 movie=OUT/(variant+'.avi')
 run(variant+'-movie',[ENGINE,'--path',str(stage),'--write-movie',str(movie),'--fixed-fps','30','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-seed=90131','--chapter1-qa-ignore-focus','--chapter1-quit-after=24'])
 rows=(OUT/(variant+'-movie.stdout.txt')).read_text(encoding='utf-8',errors='replace').splitlines()
 result=json.loads(next(row.split(' ',1)[1]for row in rows if row.startswith('FULL_CHAPTER_RUNTIME_RESULT ')))
 write(OUT/(variant+'.state.json'),result)
 assert all(sha(stage/name)==digest for name,digest in pins.items())
 results[variant]={'movie':str(movie),'sha256':sha(movie),'state':result}
assert results['sprite09']['state']==results['rigged05']['state'],'Same input should have identical gameplay state'
write(OUT/'COMPARISON.json',{'gameplay_states_identical':True,'seed':90131,'offline_fixed_fps':30,'duration_requested':24,'results':results,'scope':'GPU offline movie; not real-time performance or manual/audio approval'})
print(json.dumps({'complete':True,'gameplay_states_identical':True}),flush=True)
