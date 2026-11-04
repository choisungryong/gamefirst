"""Finalize new quality03 art without editing any PNG pixels or old art."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image
import numpy as np
from scipy import ndimage
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
hero_spec=json.loads((OUT/"GENERATED-HERO.json").read_text(encoding="utf-8"))
dest=OUT/hero_spec["target"]
if dest.exists():assert sha(dest)==sha(Path(hero_spec["original"]))
else:shutil.copy2(hero_spec["original"],dest)
im=Image.open(dest);a=np.asarray(im.getchannel("A"));lab,n=ndimage.label(a>38);sizes=np.bincount(lab.ravel())
major=[(i,s) for i,s in enumerate(ndimage.find_objects(lab),1) if sizes[i]>3000]
assert len(major)==16
dirs=["south","east","north","west"]; ordered={}
for i,s in major:
    x0,y0,x1,y1=s[1].start,s[0].start,s[1].stop,s[0].stop
    col=min(3,int((x0+x1)*.5/(im.width/4)));row=min(3,int((y0+y1)*.5/(im.height/4)))
    assert (row,col) not in ordered
    ordered[row,col]=(i,[x0,y0,x1-x0,y1-y0])
old=json.loads((ROOT/"art/actors/hero.json").read_text())
frames=[];inspection=[]; ppms={}
for row,direction in enumerate(dirs):
    prior=np.median([old["frames"][i]["region"][3] for i in old["frames_by_direction"][direction]])
    ppm=round(119*ordered[row,0][1][3]/prior,3);ppms[direction]=ppm
    for col in range(4):
        ident,r=ordered[row,col];x,y,w,h=r
        margin=6; rx=max(0,x-margin);ry=max(0,y-margin);rw=min(im.width,x+w+margin)-rx;rh=min(im.height,y+h+margin)-ry
        frame_labels=lab[ry:ry+rh,rx:rx+rw]
        other=[i for i,_ in major if i!=ident and np.any(frame_labels==i)]
        assert not other
        assert np.count_nonzero(frame_labels==ident)==sizes[ident]
        yy,xx=np.where((lab==ident)&(np.indices(lab.shape)[0]>=y+h-12))
        anchor_x=float(np.median(xx));anchor_y=float(y+h)
        frames.append(dict(region=[rx,ry,rw,rh],feet=[round(anchor_x-rx,3),round(anchor_y-ry,3)],pixels_per_meter=ppm,duration=[.07,.10,.09,.10][col],texture="res://chapter1/art/quality03/hero_cast_v01.png",direction=direction,phase=["ready","anticipation","release","recovery"][col]))
        inspection.append(dict(direction=direction,phase=col,component=int(ident),pixels=int(sizes[ident]),neighbor_major_pixels=0))
meta=dict(schema=1,kind="hero_cast",source_type="independent_generated_2d_directional_cast_atlas",texture="res://chapter1/art/quality03/hero_cast_v01.png",columns=4,rows=4,width=im.width,height=im.height,pixels_per_meter=128.0,alpha_cutoff=.15,directions=dirs,frames=frames,frames_by_direction={d:list(range(i*4,i*4+4)) for i,d in enumerate(dirs)},states={"cast_"+d:list(range(i*4,i*4+4)) for i,d in enumerate(dirs)},notes=["Directional raster cast candidate, not rigged 3D.","Four successive cast poses per facing: ready, anticipation, release, recovery.","Constant scale within each direction; scale matched to previous hero walk atlas by ready-pose height.","Existing walk/hit/death sheets unchanged. Feet and transitions require engine visual review."])
new(OUT/"hero_cast_v01.json",meta)
new(OUT/"HERO-CAST-INSPECTION.json",dict(width=im.width,height=im.height,major_components=16,transparent_pixels=int(np.count_nonzero(a==0)),pixels_per_meter_by_direction=ppms,frames=inspection,scope="Alpha-only metadata analysis; PNG bytes copied unchanged. No motion quality approval implied."))
prompts=json.loads((OUT/"GENERATION-PROMPTS.json").read_text(encoding="utf-8"))
prompts["soil"]=json.loads((OUT/"GENERATED-SOIL.json").read_text(encoding="utf-8"))
prompts["hero_cast"]=hero_spec
assets=[]
for key,rec in prompts.items():
    p=OUT/rec["target"];o=Path(rec["original"])
    assert sha(p)==sha(o),(p,o)
    src=Image.open(p)
    assets.append(dict(key=key,path=p.name,original=str(o),sha256=sha(p),original_sha256=sha(o),width=src.width,height=src.height,mode=src.mode,prompt=rec["prompt"],reference_inputs=rec.get("reference_inputs",[]),generation_mode="built-in image_gen.imagegen; all PNG pixels preserved unchanged",rights="Independently generated project artwork; no third-party or CC0 license asserted",status="Art supplied for actual runtime integration trial; final quality approval remains open"))
new(OUT/"ASSET-LEDGER-v03.json",dict(schema=1,assets=assets,metadata={p.name:sha(p) for p in [OUT/"cloister_props_v01.json",OUT/"hero_cast_v01.json"]},scope="Four new raster assets for quality03; existing art/old ledger untouched",limitations=["Materials requested seamless; runtime edge/repetition check required.","Props are 2.5D billboards, not physical 3D geometry.","Height and feet anchors initially authored; verify occlusion/grounding at game camera.","Hero directional cast has four poses/facing; temporal coherence and moving-cast transition must be reviewed in-game.","Existing enemy and hero hit/death action direction limitations remain."]))
print(json.dumps(dict(assets=4,hero_cast_frames=16,pixels_per_meter=ppms,original_hash_matches=True,metadata_neighbor_major_pixels=0)))

