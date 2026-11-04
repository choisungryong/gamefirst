from pathlib import Path
import shutil,subprocess,json
SOURCE=Path('C:/Project/game-research/art-sources/oga-chained-demon-20261101-01')
OUT=SOURCE/'godot-preview04';STAGE=Path('C:/Project/game-research/build-staging/chained-demon-preview-20261101-04')
assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir();(STAGE/'art').mkdir()
shutil.copy2(SOURCE/'motion-04/chained_demon_animated.glb',STAGE/'art/chained_demon_animated.glb')
shutil.copy2(Path(__file__).with_name('demon_preview04.gd'),STAGE/'preview.gd')
(STAGE/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Chained demon own clips research"\nrun/main_scene="res://Preview.tscn"\n[display]\nwindow/size/viewport_width=960\nwindow/size/viewport_height=720\n[rendering]\nrenderer/rendering_method="forward_plus"\nanti_aliasing/quality/msaa_3d=2\n',encoding='utf-8')
(STAGE/'Preview.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://preview.gd" id="1"]\n[node name="Preview" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('preview',['--max-fps','60'])]:
 cmd=[engine,'--path',str(STAGE)]+args;r=subprocess.run(cmd,capture_output=True,timeout=90)
 with(OUT/(label+'-execution.json')).open('x',encoding='utf-8')as f:json.dump({'command':cmd,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
 print(json.dumps({'label':label,'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:1400]}),flush=True)
 if r.returncode!=0 or r.stderr:raise RuntimeError(label)
if (STAGE/'captures').exists():shutil.copytree(STAGE/'captures',OUT/'captures')
