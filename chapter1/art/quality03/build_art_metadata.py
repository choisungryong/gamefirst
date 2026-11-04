"""Copies original generated pixels unchanged; analyzes alpha only to author metadata."""
from pathlib import Path
import hashlib, json, shutil
from PIL import Image
import numpy as np
from scipy import ndimage

OUT=Path(__file__).resolve().parent
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_new(p,data):
    assert not p.exists(), f"Preserve existing output: {p}"
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

spec=json.loads((OUT/"GENERATION-PROMPTS.json").read_text(encoding="utf-8"))
ledger=[]
for key,rec in spec.items():
    src=Path(rec["original"]); dest=OUT/rec["target"]
    assert not dest.exists(),dest
    shutil.copy2(src,dest)
    assert digest(src)==digest(dest)
    im=Image.open(dest)
    ledger.append(dict(key=key,path=dest.name,original=str(src),sha256=digest(dest),original_sha256=digest(src),width=im.width,height=im.height,mode=im.mode,prompt=rec["prompt"],generation_mode="built-in image_gen.imagegen; source pixels copied unchanged",rights="Independently generated project artwork; no third-party license or CC0 assertion",status="Candidate art; real-engine visual approval pending"))
im=Image.open(OUT/"cloister_props_v01.png")
alpha=np.asarray(im.getchannel("A"))
regions=[
("pillar_whole",[138,35,121,333],4.1,"stone"),
("pillar_broken",[479,115,161,256],2.6,"stone"),
("arch",[762,12,292,368],5.8,"stone"),
("wall",[1116,93,306,278],2.4,"stone"),
("grave_cross",[96,417,193,306],1.6,"grave"),
("grave_slab",[400,503,304,214],.85,"grave"),
("brazier",[812,431,162,302],2.2,"brazier"),
("tree",[1076,371,361,381],5.5,"foliage"),
("roots",[20,763,338,302],1.15,"foliage"),
("shrub_a",[405,760,298,286],.85,"foliage"),
("shrub_b",[756,805,311,236],.70,"foliage"),
("rubble",[1108,813,320,227],.9,"stone")]
props=[]; inspection=[]
labels,n=ndimage.label(alpha>38)
sizes=np.bincount(labels.ravel())
major=set(np.flatnonzero(sizes>3000).tolist());major.discard(0)
for name,r,height,category in regions:
    x,y,w,h=r
    assert x>=0 and y>=0 and x+w<=im.width and y+h<=im.height
    crop=alpha[y:y+h,x:x+w]
    ids=set(np.unique(labels[y:y+h,x:x+w]).tolist()) & major
    assert len(ids)==1,(name,ids)
    ident=next(iter(ids))
    full_count=int(sizes[ident]); inside=int(np.count_nonzero(labels[y:y+h,x:x+w]==ident))
    assert inside==full_count,(name,"major component clipped",inside,full_count)
    # Metadata footprint only. All prop pixels remain in the source PNG.
    feet=[w*.5,h-7.0]
    if name=="arch":feet=[w*.5,h-22.0]
    if name=="tree":feet=[w*.5,h-24.0]
    props.append(dict(id=name,region=r,feet=feet,height_m=height,category=category))
    inspection.append(dict(id=name,major_component=ident,major_pixels=full_count,inside_pixels=inside,neighbor_major_pixels=0,opaque_pixels=int(np.count_nonzero(crop>38))))
write_new(OUT/"cloister_props_v01.json",dict(schema=1,source_type="independent_generated_2d_prop_atlas",texture="res://chapter1/art/quality03/cloister_props_v01.png",width=im.width,height=im.height,columns=4,rows=3,alpha_cutoff=.15,props=props,notes=["Variable regions, not uniform cell slicing.","Foot anchors/height_m require actual camera review.","Tree extends across nominal row boundary but supplied region contains its entire major connected component with no neighbor."]))
write_new(OUT/"PROP-INSPECTION.json",dict(alpha_min=int(alpha.min()),alpha_max=int(alpha.max()),transparent_pixels=int(np.count_nonzero(alpha==0)),major_components=len(major),props=inspection,scope="Read-only alpha/component metadata analysis; not image pixel editing or visual approval"))
write_new(OUT/"ASSET-LEDGER-v01.json",dict(schema=1,assets=ledger,metadata_sha256=digest(OUT/"cloister_props_v01.json"),limitations=["Tile seam repetition and camera-scale approval remain engine tasks.","Raster atlas; not rigged 3D geometry.","Prop footprint anchors are authored initial values."]))
print(json.dumps(dict(assets=[x["path"] for x in ledger],props=len(props),major_components=len(major),copied_original_hash_match=True)))

