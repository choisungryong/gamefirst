from pathlib import Path
import subprocess,json,shutil
HERE=Path(__file__).parent;STAGE=Path('C:/Project/game-research/build-staging/rigged-hero-20261101-04')
OUT=HERE/'occlusion-fixture02';assert not OUT.exists();OUT.mkdir()
target=STAGE/'occlusion_fixture.gd';shutil.copy2(HERE/target.name,target);target.write_text(target.read_text(encoding='utf-8').replace('occlusion-fixture02/captures','occlusion-fixture02/captures'),encoding='utf-8')
(STAGE/'OcclusionFixture.tscn').write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://occlusion_fixture.gd" id="1"]
[node name="OcclusionFixture" type="Node3D"]
script=ExtResource("1")
''',encoding='utf-8')
command=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--path',str(STAGE),'res://OcclusionFixture.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=6.2']
r=subprocess.run(command,capture_output=True,timeout=60)
with (OUT/'execution.json').open('x',encoding='utf-8') as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
source=STAGE/'plans/chapter1-quality04-20261101-01/rigged-hero-04/occlusion-fixture02/captures'
if source.exists():shutil.copytree(source,OUT/'captures')
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:1200]}))

