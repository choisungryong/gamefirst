from pathlib import Path
import shutil,json,subprocess,hashlib
ROOT=Path('C:/Project/game-research/art-sources/oga-skeleton-outlaw-20261101-01')
OUT=ROOT/'godot-convert02';STAGE=Path('C:/Project/game-research/build-staging/skeleton-outlaw-import-20261101-02')
assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
src=ROOT/'extracted/SkeletonOutlaw';art=STAGE/'art';art.mkdir()
shutil.copy2(src/'Source Model/SkeletonOutlaw.fbx',art/'SkeletonOutlaw.fbx')
shutil.copy2(src/'Textures/SkeletonOutlaw00.png',art/'Atlas.png')
shutil.copy2(src/'Textures/Axe00.png',art/'Axe00.png')
clips=['Idle00','Idle01','Walk00','Run00','Attack00','Attack01','Attack02','Damage00','Dead01']
for name in clips:shutil.copy2(src/('Animations/SkeletonOutlaw@'+name+'.fbx'),art/(name+'.fbx'))
shutil.copy2(Path(__file__).with_name('convert_skeleton_outlaw02.gd'),STAGE/'convert.gd')
(STAGE/'project.godot').write_text('config_version=5\n[application]\nconfig/name="SkeletonOutlaw art conversion02"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--editor','--import']),('convert',['--script','res://convert.gd'])]:
 command=[engine,'--headless','--path',str(STAGE)]+args
 r=subprocess.run(command,capture_output=True,timeout=180)
 with(OUT/(label+'-execution.json')).open('x',encoding='utf-8')as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
 print(json.dumps({'label':label,'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:1500]}),flush=True)
 if r.returncode!=0 or r.stderr:raise RuntimeError(label+' failed or reported errors')
shutil.copytree(STAGE/'derived',OUT/'derived')
with(OUT/'OUTPUT.json').open('x',encoding='utf-8')as f:json.dump({'glb':{'sha256':hashlib.sha256((OUT/'derived/skeleton_outlaw.glb').read_bytes()).hexdigest(),'bytes':(OUT/'derived/skeleton_outlaw.glb').stat().st_size},'texture_alias':'Atlas.png is exact SkeletonOutlaw00.png copy; author FBX refers to missing old basename','stage':str(STAGE)},f,indent=2)
