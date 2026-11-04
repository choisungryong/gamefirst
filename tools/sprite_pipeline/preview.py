"""Launch an opt-in role registry in an isolated current-chapter source preview.
No full-chapter regression suite and no active product/save replacement.
"""
from pathlib import Path
import argparse,json,hashlib,shutil,subprocess,sys,importlib.util
ROOT=Path(__file__).resolve().parents[2]
PROOF=ROOT/'plans/chapter1-quality04-20261101-01/full30/build'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--registry',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--pilot',action='store_true');ap.add_argument('--headless',action='store_true');ap.add_argument('--quit-after',type=float,default=0);a=ap.parse_args()
    if a.output.exists():raise ValueError('Choose a new output directory; previous previews are preserved')
    doc=read(a.registry);bindings={};releases={}
    for role,slot in doc['bindings'].items():
        resource=slot['asset']
        if not resource.startswith('res://') or '..' in resource:raise ValueError('Only registered project assets are supported')
        actor=(ROOT/resource[6:]).resolve()
        if not actor.is_relative_to(ROOT) or actor.suffix!='.json':raise ValueError('Invalid registered actor path')
        bindings[role]=actor.parent/'manifest.json';releases[role]=slot.get('release_frame',-1)
    spec=importlib.util.spec_from_file_location('spriteroles',Path(__file__).with_name('roles.py'));roles=importlib.util.module_from_spec(spec);spec.loader.exec_module(roles)
    a.output.mkdir(parents=True);shutil.copy2(a.registry,a.output/'REQUESTED-REGISTRY.json');roles.build(bindings,releases,a.output/'sprite-preview-registry.json')
    stage=a.output/'stage';stage.mkdir();old=Path(read(PROOF/'closure.json')['stage']);pins=read(PROOF/'staging-manifest.json')
    for name,h in pins.items():
        if sha(old/name)!=h:raise ValueError('Current product stage changed: '+name)
        p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/name,p)
    for name in ['sprite_asset_presenter.gd','sprite_asset_presenter_v2.gd','sprite_role_registry.gd','sprite_role_actors_preview.gd']:shutil.copy2(ROOT/'chapter1/presentation'/name,stage/'chapter1/presentation'/name)
    for manifest_path in bindings.values():
        manifest=read(manifest_path);asset_dir=manifest_path.parent;relative=asset_dir.relative_to(ROOT);target=stage/relative;target.mkdir(parents=True,exist_ok=True)
        for name in ['actor.json','manifest.json']+[t['file'] for t in manifest['textures'].values()]:shutil.copy2(asset_dir/name,target/name)
    shutil.copy2(a.output/'sprite-preview-registry.json',stage/'sprite-preview-registry.json');shutil.copy2(Path(__file__).with_name('combat_preview.gd'),stage/'combat_preview.gd')
    project=stage/'project.godot';project.write_text(project.read_text(encoding='utf-8').replace('AshenCloisterChapterOneQuality30','AshenCloisterSpriteRolePreview'),encoding='utf-8')
    staged={str(p.relative_to(stage)).replace('\\','/'):sha(p) for p in stage.rglob('*') if p.is_file()};(a.output/'SOURCE.json').write_text(json.dumps(dict(stage=str(stage),pins=staged),indent=2))
    phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://combat_preview.gd'])]
    run=(['--headless'] if a.headless else [])+['--script','res://combat_preview.gd','--','--chapter1-profile-off']
    if a.pilot:run+=['--chapter1-start','--chapter1-pilot','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131']
    if a.quit_after>0:run+=['--chapter1-quit-after='+str(a.quit_after)]
    phases.append(('preview',run))
    for label,args in phases:
        with (a.output/(label+'.stdout.txt')).open('xb') as out,(a.output/(label+'.stderr.txt')).open('xb') as err:
            cmd=[str(ENGINE),'--path',str(stage)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(a.output/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait()
        result=dict(exit=code,stderr_bytes=(a.output/(label+'.stderr.txt')).stat().st_size);(a.output/(label+'-execution.json')).write_text(json.dumps(result));
        if code!=0:raise RuntimeError(label+' failed; inspect preserved raw logs')
    if not all(sha(stage/n)==h for n,h in staged.items()):raise RuntimeError('Preview sources changed')
    print('SPRITE ROLE PREVIEW CLOSED; SOURCES PRESERVED',flush=True)
if __name__=='__main__':main()
