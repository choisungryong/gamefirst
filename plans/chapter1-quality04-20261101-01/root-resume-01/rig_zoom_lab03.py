from pathlib import Path
import subprocess,json
HERE=Path(__file__).parent;OLD=HERE.parent/'rigged-hero-02'
STAGE=Path('C:/Project/game-research/build-staging/rigged-hero-20261101-02')
script=STAGE/'zoom_lab.gd';scene=STAGE/'ZoomLab.tscn';assert not script.exists() and not scene.exists()
script.write_text('''extends "res://chapter1/chapter_one_view.gd"
func _ready() -> void:
 super._ready()
 world.camera.size=8.0
''',encoding='utf-8')
scene.write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://zoom_lab.gd" id="1"]
[node name="ZoomLab" type="Node3D"]
script=ExtResource("1")
''',encoding='utf-8')
OUT=OLD/'zoom-lab03';assert not OUT.exists();OUT.mkdir()
capture=STAGE/'plans/chapter1-quality04-20261101-01/rigged-hero-02/zoom-lab03/captures'
cmd=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--path',str(STAGE),'res://ZoomLab.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=22']
r=subprocess.run(cmd,capture_output=True,timeout=90)
with (OUT/'execution.json').open('x',encoding='utf-8') as f:json.dump({'command':cmd,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),'scope':'Camera size8 pose/material inspection only; not normal-camera quality comparison'},f,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')}))
