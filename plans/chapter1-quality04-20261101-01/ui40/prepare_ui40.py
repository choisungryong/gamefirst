"""Prepare a bounded HUD40 fixture stage; does not launch Godot or touch profiles."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
STAGE=Path('C:/Project/game-research/build-staging/chapter1-ui40-preview-20261111-01')
manifest=json.loads((ROOT/'plans/chapter1-quality04-20261101-01/ui38/package38/closure.json').read_text())
paths=manifest['runtime_source_files']+['chapter1/view/ui40/chapter_hud_quality40.gd']
assert len(paths)==167 and not STAGE.exists()
STAGE.mkdir()
pins={}
for name in paths:
    source=ROOT/name;target=STAGE/name
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    pins[name]=hashlib.sha256(source.read_bytes()).hexdigest()
project=(ROOT/'project.godot').read_text(encoding='utf-8')
project=project.replace('run/main_scene="res://Baseline.tscn"','run/main_scene="res://chapter1/ChapterOne.tscn"')
project=project.replace('config/name="D2R Combat Baseline"','config/name="UI40 Preview"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterUI40Preview20261111"')
(STAGE/'project.godot').write_text(project,encoding='utf-8')
assembly=STAGE/'chapter1/chapter_one_view.gd'
text=assembly.read_text(encoding='utf-8')
assert text.count('res://chapter1/view/ui38/chapter_hud_quality38.gd')==1
assembly.write_text(text.replace('res://chapter1/view/ui38/chapter_hud_quality38.gd','res://chapter1/view/ui40/chapter_hud_quality40.gd'),encoding='utf-8')
shutil.copy2(HERE/'ui40_probe.gd',STAGE/'ui40_probe.gd')
(HERE/'PREPARATION.json').write_text(json.dumps({'stage':str(STAGE),'source_count':len(paths),'source_pins':pins,'scope':'Actual38 world+UI40 synthetic read-only fixtures, no profile access or GPU launched'},indent=2),encoding='utf-8')
print(json.dumps({'stage':str(STAGE),'source_count':len(paths),'no_engine_launched':True}))
