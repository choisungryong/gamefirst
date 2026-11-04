"""Read-only PNG geometry analysis; writes atlas metadata, never changes image pixels."""
from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage
import json, hashlib
ROOT=Path(r"C:\Project\d2r-combat-baseline")
ACT=ROOT/"chapter1/art/actors"
def inspect(name,count,rows):
 p=ACT/(name+".png"); im=Image.open(p); a=np.asarray(im.getchannel("A"))
 labels,n=ndimage.label(a>=32); boxes=ndimage.find_objects(labels); comps=[]
 for i,s in enumerate(boxes):
  if s is None: continue
  area=int(np.sum(labels[s]==i+1))
  if area>300: comps.append((i+1,area,s))
 comps=sorted(comps,key=lambda t:-t[1])[:count]
 if len(comps)!=count: raise ValueError((name,len(comps),count))
 comps.sort(key=lambda t:(t[2][0].start+t[2][0].stop)/2)
 ordered=[]
 for r in range(rows):
  ordered.extend(sorted(comps[r*4:r*4+4],key=lambda t:(t[2][1].start+t[2][1].stop)/2))
 frames=[]; foreign=0
 ids={t[0] for t in ordered}
 for ident,area,(ys,xs) in ordered:
  own=labels[ys,xs]==ident; h,w=own.shape
  bottom=own[max(0,h-max(12,int(h*.06))):,:]; xx=np.where(bottom)[1]
  foot=float(np.median(xx)) if len(xx) else w/2
  frames.append({"region":[xs.start,ys.start,w,h],"feet":[foot,float(h)]})
  foreign+=int(np.sum(np.isin(labels[ys,xs],list(ids-{ident}))))
 return frames,{"file":str(p.relative_to(ROOT)),"width":im.width,"height":im.height,"mode":im.mode,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"major_components":len(comps),"foreign_component_pixels_in_regions":foreign,"transparent_fraction":float(np.mean(a==0)),"frames":frames}
reports=[]
for kind in ("walker","ranged","charger"):
 meta=json.loads((ACT/(kind+".json")).read_text())
 frames,report=inspect(kind+"_actions",12,3)
 old_height=np.median([f["region"][3] for f in meta["frames"][:4]])
 new_height=np.median([f["region"][3] for f in frames[:4]])
 ppm=round(meta["pixels_per_meter"]*new_height/old_height,3)
 meta["frames"]=meta["frames"][:16]
 for f in frames:
  f.update(pixels_per_meter=ppm,duration=.12,texture="res://chapter1/art/actors/"+kind+"_actions.png",direction="south")
  meta["frames"].append(f)
 meta["states"].update(cast=list(range(16,20)),attack=list(range(16,20)),hit=list(range(20,24)),death=list(range(24,28)))
 meta["notes"].append("Attack/cast, hit and death are actual distinct south-facing action poses only; four-direction action clips are not supplied. Action scale calibrated by median standing height ratio; verify perceived size in engine.")
 (ACT/(kind+".json")).write_text(json.dumps(meta,indent=2)+"\n")
 reports.append(report)
out=ROOT/"plans/chapter1-c2-20261031-01/art/ENEMY-ACTIONS-INSPECTION.json"
out.write_text(json.dumps(reports,indent=2)+"\n")
print(json.dumps([{k:v for k,v in r.items() if k!="frames"} for r in reports],indent=2))

