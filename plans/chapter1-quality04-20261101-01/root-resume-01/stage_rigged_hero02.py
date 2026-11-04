from pathlib import Path
import json,shutil,subprocess,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent
OLD=HERE.parent/'rigged-hero-01';OUT=OLD.with_name('rigged-hero-02')
STAGE=Path('C:/Project/game-research/build-staging/rigged-hero-20261101-02');assert not OUT.exists() and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
manifest=json.loads((OLD/'stage-manifest.json').read_text(encoding='utf-8'));oldstage=Path(manifest['stage'])
pins={}
for name in manifest['source_pins_before_stage_injections']:
 target=STAGE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 pins[name]=hashlib.sha256(target.read_bytes()).hexdigest()
shutil.copy2(oldstage/'project.godot',STAGE/'project.godot')
p=STAGE/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8').replace('res://chapter1/view/chapter_actors.gd','res://chapter1/view/rigged_hero_actors.gd');p.write_text(s,encoding='utf-8')
p=STAGE/'chapter1/view/cloister_world_quality03.gd';s=p.read_text(encoding='utf-8').replace('moon.shadow_enabled=false','moon.shadow_enabled=true;moon.light_cull_mask=3');p.write_text(s,encoding='utf-8')
with (OUT/'stage-manifest.json').open('x',encoding='utf-8') as f:json.dump({'stage':str(STAGE),'source_pins_before_stage_injections':pins,'changes':'Hero live-mesh light layer2 key/fill; moon layer3 actual shadows; raw source09 core unchanged','prior':str(OLD)},f,indent=2)
runner=(OLD/'run_preview.py').read_text(encoding='utf-8').replace('rigged-hero-20261101-01','rigged-hero-20261101-02').replace('rigged-hero-01','rigged-hero-02')
(OUT/'run_preview.py').write_text(runner,encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
command=[engine,'--headless','--path',str(STAGE),'--editor','--import'];r=subprocess.run(command,capture_output=True,timeout=180)
with (OUT/'import-execution.json').open('x',encoding='utf-8') as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')}))
