"""Create a new opt-in visual role registry from compiled sprite manifests."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
ROLES=('hero','walker','ranged','charger','elite')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def require(ok,note):
    if not ok:raise ValueError(note)
def build(bindings,releases,output,allow_missing=False):
    output=Path(output);require(not output.exists(),'Refusing to overwrite an existing role registry');slots={};warnings=[]
    for role,path in bindings.items():
        require(role in ROLES,'Unknown role '+role);path=Path(path);manifest=read(path);require(manifest['role']==role,'Asset and target role differ')
        base=manifest['resource_base'];require(base.startswith('res://') and '..' not in base,'Invalid resource base');actor_path=(ROOT/base[6:]/manifest['actor']).resolve();require(actor_path==(path.parent/manifest['actor']).resolve(),'Asset is not installed at its declared resource base');actor=read(actor_path);require(actor['kind']==role,'Compiled actor role differs')
        for texture in manifest['textures'].values():require(hashlib.sha256((path.parent/texture['file']).read_bytes()).hexdigest()==texture['sha256'],'Texture differs from compiled manifest')
        clips=actor['clips'];cast=clips.get('cast',clips.get('cast_south',[]));release=releases.get(role,actor.get('release_frame',-1))
        if cast:require(isinstance(release,int) and 0<=release<len(cast),'Specify --release '+role+'=FRAME for the authored attack release')
        for action in ('cast','hit','death'):
            if action in clips:warnings.append(role+': '+action+' has common facing, not four directional poses')
            elif not all(action+'_'+d in clips for d in ('south','east','north','west')):
                require(allow_missing,'Missing authored combat action '+role+':'+action);warnings.append(role+': '+action+' missing; preview fallback')
        slots[role]={'asset':base+'/'+manifest['actor'],'release_frame':release,'allow_missing_preview':allow_missing}
    require(bool(slots),'Choose at least one role')
    doc={'schema':1,'preview_only':True,'bindings':slots,'warnings':warnings,'scope':'Only visual presenters selected. Unbound roles and final boss keep3D. No core or user save changes.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(doc,f,ensure_ascii=False,indent=2)
    return doc
def pairs(items,cast=str):
    result={}
    for text in items:
        key,value=text.split('=',1);require(key not in result,'Duplicate role '+key);result[key]=cast(value)
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bind',action='append',default=[],help='role=compiled manifest.json');ap.add_argument('--release',action='append',default=[],help='role=authored release frame');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--allow-missing-preview',action='store_true');a=ap.parse_args();doc=build(pairs(a.bind),pairs(a.release,int),a.output,a.allow_missing_preview);print(json.dumps(doc,ensure_ascii=False))
if __name__=='__main__':main()
