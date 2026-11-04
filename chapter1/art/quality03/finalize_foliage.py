"""Final new foliage metadata and preserved rejected run attempts; never alters PNG pixels."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image
import numpy as np
from scipy import ndimage
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
spec=json.loads((OUT/"GENERATED-FOLIAGE-RUN.json").read_text(encoding="utf-8"))
records={}
for key,r in spec.items():
    dst=OUT/r["target"];src=Path(r["original"]);assert not dst.exists()
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(dst)==sha(src)
    im=Image.open(dst)
    records[key]=dict(key=key,path=r["target"],original=str(src),sha256=sha(dst),original_sha256=sha(src),width=im.width,height=im.height,mode=im.mode,prompt=r["prompt"],reference_inputs=r.get("reference_inputs",[]),generation_mode="built-in image_gen.imagegen; PNG pixels copied unchanged",rights="Independently generated project artwork; no third-party or CC0 license assertion",status=r.get("status","Candidate art; real-engine approval pending"))
im=Image.open(OUT/"cloister_foliage_v01.png");a=np.asarray(im.getchannel("A"));lab,n=ndimage.label(a>38);sizes=np.bincount(lab.ravel())
parts=[]
for i,sl in enumerate(ndimage.find_objects(lab),1):
    if sizes[i]<=3000:continue
    x,y,w,h=sl[1].start,sl[0].start,sl[1].stop-sl[1].start,sl[0].stop-sl[0].start
    row=int((y+h*.5)/(im.height/2));col=int((x+w*.5)/(im.width/4))
    parts.append((row,col,i,[x,y,w,h]))
assert len(parts)==8
parts.sort()
ids=["grass_a","grass_b","fern_a","grass_bent","grass_leaf","fern_moss","grass_sedge","fern_grass"]
heights=[.68,.78,.62,.74,.58,.52,.82,.62]
props=[];inspection=[];coverage=np.zeros(a.shape,bool)
major={p[2] for p in parts}
for ix,(row,col,ident,r) in enumerate(parts):
    x,y,w,h=r;pad=3;rx=max(0,x-pad);ry=max(0,y-pad);rw=min(im.width,x+w+pad)-rx;rh=min(im.height,y+h+pad)-ry
    region=lab[ry:ry+rh,rx:rx+rw];near=set(np.unique(region).tolist()) & major;assert near=={ident},(ids[ix],near)
    assert np.count_nonzero(region==ident)==sizes[ident]
    coverage[ry:ry+rh,rx:rx+rw]=True
    props.append(dict(id=ids[ix],region=[rx,ry,rw,rh],feet=[rw*.5,rh-7.0],height_m=heights[ix],category="foliage"))
    inspection.append(dict(id=ids[ix],component=int(ident),pixels=int(sizes[ident]),neighbor_major_pixels=0))
new(OUT/"cloister_foliage_v01.json",dict(schema=1,source_type="independent_generated_2d_foliage_atlas",texture="res://chapter1/art/quality03/cloister_foliage_v01.png",width=im.width,height=im.height,columns=4,rows=2,alpha_cutoff=.15,props=props,notes=["Dense realistic 2.5D grass/fern clusters; not 3D foliage geometry.","No attached ground tile or cast shadow.","Initial heights/feet require actual camera and overlap review."]))
new(OUT/"FOLIAGE-INSPECTION.json",dict(width=im.width,height=im.height,alpha_min=int(a.min()),alpha_max=int(a.max()),transparent_pixels=int(np.count_nonzero(a==0)),major_components=8,unassigned_visible_minor_pixels=int(np.count_nonzero((a>38)&~coverage)),components=inspection,scope="Alpha-only metadata analysis. Major components fully contained, no neighboring major pixels. Tiny detached alpha fragments may be trimmed."))
old=json.loads((OUT/"ASSET-LEDGER-v03.json").read_text(encoding="utf-8"))
assets=old["assets"]+[records["foliage"]]
for r in assets:
    assert sha(OUT/r["path"])==r["sha256"]==sha(Path(r["original"]))
rejected=[records["run_attempt01"],records["run_attempt02"]]
for r in rejected:r["reason"]="Visual inspection found repeated leading foot across phases; cape/stance variation does not establish genuine alternating run contacts or suspension."
metas={p.name:sha(p) for p in [OUT/"cloister_props_v01.json",OUT/"hero_cast_v01.json",OUT/"cloister_foliage_v01.json"]}
new(OUT/"ASSET-LEDGER-v04.json",dict(schema=1,accepted_for_runtime_trial=assets,rejected_attempts=rejected,metadata_sha256=metas,png_copies_original_hash_match=True,scope="Five new adopted trial PNGs and two rejected animation attempts. Existing art and old ledgers preserved.",limitations=old["limitations"]+["Eight-frame directional run not supplied: both32-pose attempts failed visible leg alternation; hero_run_v01.json deliberately absent.","Existing4-frame walk remains runtime fallback; do not advertise a finished run cycle."]))
new(OUT/"ART-METADATA-RECOVERY.json",dict(first_script="finalize_art_metadata.py",first_actual_exit=1,first_error="FileNotFoundError: wrong parent selected project/art/actors/hero.json instead of chapter1/art/actors/hero.json",retained_first_source=True,recovery_script="finalize_art_metadata_v02.py",recovery_actual_exit=0,recovery_changes=["Correct read-only reference path.","If the already copied PNG exists, verify exact original SHA256 instead of replacing it."],game_bug=False,image_pixels_changed=False))
print(json.dumps(dict(adopted_pngs=5,rejected_run_attempts=2,foliage_props=8,neighbor_major_pixels=0,visible_minor_pixels_outside_regions=int(np.count_nonzero((a>38)&~coverage)),all_png_original_hashes_match=True)))

