from pathlib import Path
import json, shutil, hashlib, subprocess
ROOT=Path('C:/Project/d2r-combat-baseline')
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-quality03-before-20261031-02/source')
STAGE=Path('C:/Project/game-research/build-staging/chapter1-quality03-world-preview01')
PROOF=ROOT/'plans/chapter1-quality-20261031-01/world/preview01'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
assert not STAGE.exists() and not PROOF.exists()
STAGE.mkdir(parents=True);PROOF.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'plans/chapter1-c2-20261031-01/package-candidate02/source-manifest.json').read_text(encoding='utf-8'))
for name,expected in manifest.items():
    src=BACKUP/name; assert sha(src)==expected
    dst=STAGE/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
shutil.copy2(BACKUP/'project.godot',STAGE/'project.godot')
overrides=['chapter1/view/cloister_world.gd','chapter1/view/cloister_world_quality03.gd','chapter1/view/cloister_ground_quality03.gdshader','chapter1/view/cloister_props_quality03.gdshader','chapter1/view/cloister_actors.gd']
overrides += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'chapter1/art/quality03').glob('*') if p.is_file() and p.suffix in ('.png','.json')]
for name in overrides:
    dst=STAGE/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dst)
pins={str(p.relative_to(STAGE)).replace('\\','/'):sha(p) for p in STAGE.rglob('*') if p.is_file()}
(PROOF/'staging-manifest.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
CAPTURE=STAGE/'plans/chapter1-c2-20261031-01/world-preview01'
CAPTURE.mkdir(parents=True)
(CAPTURE.parent/'.gdignore').write_text('',encoding='utf-8')
for label,command in [
    ('import',[str(ENGINE),'--headless','--path',str(STAGE),'--editor','--import']),
    ('gpu',[str(ENGINE),'--path',str(STAGE),'--resolution','1920x1080','--log-file',str(PROOF/'godot.log'),'res://chapter1/Chapter1.tscn','--','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-seed=90131','--chapter1-quit-after=25','--chapter1-capture-dir='+str(CAPTURE)])]:
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    (PROOF/(label+'-execution.json')).write_text(json.dumps({'command':command,'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'scope':'Isolated authored world/actor preview only; old FX/glue and normal-input driver. Not formal performance or quality approval.'},ensure_ascii=False,indent=2),encoding='utf-8')
    assert result.returncode==0,(label,result.stderr)
for path in CAPTURE.glob('*.png'):shutil.copy2(path,PROOF/path.name)
print(json.dumps({'proof':str(PROOF),'images':[p.name for p in PROOF.glob('*.png')]}))
