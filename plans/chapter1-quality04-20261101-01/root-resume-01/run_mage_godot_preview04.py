from pathlib import Path
import json,subprocess,shutil,re
HERE=Path(__file__).resolve().parent
STAGE=Path('C:/Project/game-research/build-staging/mage-gltf-research-20261101-02');assert not STAGE.exists();STAGE.mkdir()
source=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01/gltf-preview-04/mage_animated.glb')
shutil.copy2(source,STAGE/source.name);shutil.copy2(HERE/'mage_godot_preview.gd',STAGE/'preview.gd')
(STAGE/'project.godot').write_text('''config_version=5
[application]
config/name="Mage Rig Research Only"
run/main_scene="res://Preview.tscn"
[display]
window/size/viewport_width=1024
window/size/viewport_height=768
window/stretch/mode="canvas_items"
[rendering]
renderer/rendering_method="forward_plus"
''',encoding='utf-8')
(STAGE/'Preview.tscn').write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://preview.gd" id="1"]
[node name="Preview" type="Node3D"]
script=ExtResource("1")
''',encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('gpu',[])]:
 command=[engine,'--path',str(STAGE)]+args
 r=subprocess.run(command,capture_output=True,timeout=120)
 report={'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),'stage':str(STAGE),'scope':'Research preview, not runtime art adoption or performance test'}
 with (HERE/('mage-godot04-'+label+'-execution.json')).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
 print(json.dumps(report))
 assert r.returncode==0 and not re.search(r'(?:ERROR|Parse Error)',report['stdout']+report['stderr'])
