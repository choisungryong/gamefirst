from pathlib import Path
import json,subprocess,shutil
HERE=Path(__file__).parent
STAGE=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-11')
OUT=HERE/'visual-fixture';assert not OUT.exists();OUT.mkdir()
target=STAGE/'plans/chapter1-quality04-20261101-01/full11/visual_fixture.gd';assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/target.name,target)
scene=STAGE/'VisualFixture.tscn';assert not scene.exists()
scene.write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://plans/chapter1-quality04-20261101-01/full11/visual_fixture.gd" id="1"]\n[node name="VisualFixture" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
command=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--path',str(STAGE),'res://VisualFixture.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=7.7']
r=subprocess.run(command,capture_output=True,timeout=60)
with(OUT/'execution.json').open('x',encoding='utf-8')as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
source=STAGE/'plans/chapter1-quality04-20261101-01/full11/visual-fixture/captures'
if source.exists():shutil.copytree(source,OUT/'captures')
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:2000]}))
