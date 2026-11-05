from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'equipment35/svg01';S=Path('C:/Project/game-research/build-staging/chapter1-equipment35-svg01');assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir();(S/'art').mkdir()
for p in (R/'chapter1/art/equipment_icons35').glob('*.svg'):shutil.copy2(p,S/'art'/p.name)
(S/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Equipment35 SVG raster check"\n',encoding='utf-8')
(S/'render.gd').write_text('''extends SceneTree
func _initialize() -> void:
 DirAccess.make_dir_recursive_absolute("res://proof")
 var checks: Dictionary={}
 for name_ in ["weapon","body","ring","charm"]:
  var image := Image.new()
  var error := image.load_svg_from_string(FileAccess.get_file_as_string("res://art/"+name_+".svg"),2.0)
  checks[name_]=error==OK and image.get_width()==192 and image.get_height()==192
  if error==OK:image.save_png("res://proof/"+name_+".png")
 var f := FileAccess.open("res://proof/RESULT.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"scope":"Godot headless SVG parser rasterization only; no HUD/interaction/art adoption approval."}));f.close()
 var passed := true
 for value in checks.values():passed=passed and bool(value)
 quit(0 if passed else 1)
''',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2),encoding='utf-8');engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';cmd=[engine,'--headless','--path',str(S),'--script','res://render.gd']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:r=subprocess.run(cmd,stdout=out,stderr=err,timeout=30)
d=dict(exit=r.returncode,stderr_bytes=(O/'stderr.txt').stat().st_size);(O/'execution.json').write_text(json.dumps(d));assert d==dict(exit=0,stderr_bytes=0),d;shutil.copytree(S/'proof',O/'proof');assert all(sha(S/n)==h for n,h in pins.items());print(d)
