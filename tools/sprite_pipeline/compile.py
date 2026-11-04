"""Compile authored sprite sheets into immutable, previewable Godot actor assets.
No changes to the active chapter assembly, combat rules or existing assets.
"""
from pathlib import Path
import argparse, copy, hashlib, json, math, re, shutil
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
DIRECTIONS = ('south', 'east', 'north', 'west')
ROLES = ('hero', 'walker', 'ranged', 'charger', 'elite')
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def require(test, message):
    if not test: raise ValueError(message)
def finite(value): return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
def validate(doc, textures):
    require(doc.get('kind') in ROLES, 'Unknown actor role')
    require(finite(doc.get('pixels_per_meter')) and doc['pixels_per_meter'] > 0, 'pixels_per_meter must be positive')
    require(isinstance(doc.get('frames'),list) and bool(doc['frames']), 'No authored frames supplied')
    for index,frame in enumerate(doc['frames']):
        path=frame.get('texture',doc.get('texture')); require(path in textures, f'Frame {index}: missing PNG {path}')
        region=frame.get('region',[]); require(len(region)==4 and all(finite(x) for x in region), f'Frame {index}: invalid region')
        x,y,w,h=region; size=textures[path]['size'];require(min(x,y)>=0 and min(w,h)>0 and x+w<=size[0] and y+h<=size[1],f'Frame {index}: region outside PNG')
        require(len(frame.get('feet',[]))==2 and all(finite(x) for x in frame['feet']),f'Frame {index}: missing foot anchor')
        require(finite(frame.get('duration',.125)) and frame.get('duration',.125)>0,f'Frame {index}: invalid duration')
        require(finite(frame.get('pixels_per_meter',doc['pixels_per_meter'])) and frame.get('pixels_per_meter',doc['pixels_per_meter'])>0,f'Frame {index}: invalid scale')
    clips={**{'move_'+d:ids for d,ids in doc.get('frames_by_direction',{}).items()},**doc.get('states',{})}
    for direction in DIRECTIONS: require(bool(clips.get('move_'+direction)),f'Missing authored move_{direction}')
    for name,ids in clips.items():
        require(isinstance(ids,list) and bool(ids),f'{name}: empty clip')
        require(all(isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(doc['frames']) for i in ids),f'{name}: invalid frame reference')
    release=doc.get('release_frame')
    if release is not None:
        cast=clips.get('cast',clips.get('cast_south',[]));require(isinstance(release,int) and 0<=release<len(cast),'release_frame outside authored cast clip')
    warnings=[]
    for action in ('idle','cast','hit','death'):
        if action not in clips and not all(action+'_'+d in clips for d in DIRECTIONS): warnings.append(f'{action}: incomplete authored action/directions; preview fallback only, no new poses invented')
    return clips,warnings

def compile_asset(doc, source_files, destination, asset_id, resource_base):
    require(re.fullmatch(r'[a-z][a-z0-9_-]{1,63}',asset_id) is not None,'Use a lowercase asset ID with letters, digits, _ or -')
    require(resource_base.startswith('res://') and '..' not in resource_base,'Invalid Godot resource base')
    destination=Path(destination);require(not destination.exists(),'Refusing to overwrite an existing asset output')
    doc=copy.deepcopy(doc); textures={}
    for key,path in source_files.items():
        path=Path(path);require(path.is_file() and path.suffix.lower()=='.png',f'Missing PNG: {path}')
        with Image.open(path) as im:
            require(im.format=='PNG',f'Not a PNG: {path}');im.load();require('A' in im.getbands() and im.getchannel('A').getextrema()[0]<255,f'Transparent PNG required: {path}');size=list(im.size)
        textures[key]={'source':str(path.resolve()),'sha256':sha(path),'size':size}
    clips,warnings=validate(doc,textures)
    renamed={key:f'atlas-{i:02d}.png' for i,key in enumerate(sorted(textures))}
    resource_base=resource_base.rstrip('/')
    destination.mkdir(parents=True)
    for key,record in textures.items():
        shutil.copy2(record['source'],destination/renamed[key]);record['file']=renamed[key]
    default=doc.get('texture',next(iter(textures)))
    doc['texture']=resource_base+'/'+renamed[default]
    for frame in doc['frames']: frame['texture']=resource_base+'/'+renamed[frame.get('texture',default)]
    doc.update(asset_id=asset_id,schema=1,clips=clips,animation_pipeline='authored-sprite-v1')
    (destination/'actor.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest={'schema':1,'id':asset_id,'role':doc['kind'],'resource_base':resource_base,'actor':'actor.json','textures':textures,'clips':{k:len(v) for k,v in clips.items()},'warnings':warnings,'scope':'Authored frame registration and sampling only. Combat timing/damage stay in core. Missing poses are not generated. Active3D chapter unchanged.'}
    (destination/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

def legacy(path,destination,asset_id,resource_base):
    path=Path(path);doc=load(path);files={}
    keys={doc['texture']}|{f.get('texture',doc['texture']) for f in doc['frames']}
    for key in keys:
        require(key.startswith('res://'),'Legacy input must use repository res:// texture paths')
        p=(ROOT/key[6:]).resolve();require(p.is_relative_to(ROOT),'Texture escaped project');files[key]=p
    return compile_asset(doc,files,destination,asset_id,resource_base)

def grid(spec):
    columns=spec['columns'];rows=spec['rows'];width,height=spec['image_size']
    require(all(isinstance(x,int) and x>0 for x in (columns,rows,width,height)),'Positive integer grid required')
    require(width%columns==0 and height%rows==0,'Image must divide into complete cells')
    cw,ch=width//columns,height//rows;frames=[];clips={};sheet=spec['sheet']
    for name,clip in spec['layout'].items():
        require(re.fullmatch(r'(move|idle|cast|hit|death)(_(south|east|north|west))?',name) is not None,'Unknown action '+name)
        row=clip['row'];count=clip.get('count',columns);start=clip.get('start',0);fps=clip.get('fps',8)
        require(all(isinstance(v,int) for v in (row,count,start)) and 0<=row<rows and count>0 and start>=0 and start+count<=columns,'Clip exceeds grid: '+name)
        require(finite(fps) and fps>0,'Positive clip FPS required')
        ids=[]
        for i in range(count):
            ids.append(len(frames));frames.append({'region':[(start+i)*cw,row*ch,cw,ch],'feet':spec.get('feet',[cw/2,ch-1]),'duration':1/fps,'texture':sheet})
        clips[name]=ids
    doc={'schema':1,'kind':spec['role'],'texture':sheet,'pixels_per_meter':spec.get('pixels_per_meter',150),'alpha_cutoff':.15,'frames':frames,'frames_by_direction':{d:clips['move_'+d] for d in DIRECTIONS if 'move_'+d in clips},'states':{k:v for k,v in clips.items() if not k.startswith('move_')},'source_type':'user_authored_sprite_sheet','notes':['Grid registration does not create absent action frames.']}
    if 'release_frame' in spec:doc['release_frame']=spec['release_frame']
    return doc

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--legacy',type=Path);ap.add_argument('--spec',type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--id',required=True);ap.add_argument('--resource-base',required=True);args=ap.parse_args()
    require(bool(args.legacy)!=bool(args.spec),'Choose --legacy or --spec')
    if args.legacy:result=legacy(args.legacy,args.output,args.id,args.resource_base)
    else:
        spec=load(args.spec);sheet=(args.spec.parent/spec['sheet']).resolve()
        with Image.open(sheet) as image:require(list(image.size)==spec['image_size'],'PNG dimensions differ from registration spec')
        doc=grid(spec);result=compile_asset(doc,{spec['sheet']:sheet},args.output,args.id,args.resource_base)
    print(json.dumps({'id':result['id'],'clips':result['clips'],'warnings':result['warnings']},ensure_ascii=False))
if __name__=='__main__':main()
