from pathlib import Path
import shutil,json,subprocess
ROOT=Path('C:/Project/game-research/art-sources/oga-skeleton-outlaw-20261101-01')
OUT=ROOT/'godot-import01';STAGE=Path('C:/Project/game-research/build-staging/skeleton-outlaw-import-20261101-01')
assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
src=ROOT/'extracted/SkeletonOutlaw'
for p in [src/'Source Model/SkeletonOutlaw.fbx',src/'Textures/Axe00.png',src/'Textures/SkeletonOutlaw00.png']:
 target=STAGE/'art'/p.name;target.parent.mkdir(exist_ok=True);shutil.copy2(p,target)
(STAGE/'project.godot').write_text('config_version=5\n[application]\nconfig/name="SkeletonOutlaw art import research"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',encoding='utf-8')
cmd=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--headless','--path',str(STAGE),'--editor','--import']
r=subprocess.run(cmd,capture_output=True,timeout=180)
with(OUT/'execution.json').open('x',encoding='utf-8')as f:json.dump({'command':cmd,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),'scope':'Isolated native ufbx import of author ASCII FBX. No proprietary converter or root-wide import.'},f,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:1800],'stage':str(STAGE)}))
