import runpy,json
from pathlib import Path
D=runpy.run_path(r"C:\Project\d2r-combat-baseline\plans\chapter1-c2-20261031-01\art\inspect_action_atlases.py")
inspect=D["inspect"]; ACT=D["ACT"]
frames,r=inspect("elite",16,4); ppm=132.0
for i,f in enumerate(frames): f.update(pixels_per_meter=ppm,duration=.12,texture="res://chapter1/art/actors/elite.png",direction=["south","east","north","west"][i//4])
meta={"schema":1,"kind":"elite","source_type":"independent_generated_2d_sprite_atlas","texture":"res://chapter1/art/actors/elite.png","columns":4,"rows":4,"pixels_per_meter":ppm,"alpha_cutoff":.15,"directions":["south","east","north","west"],"frames":frames,"frames_by_direction":{d:list(range(i*4,i*4+4)) for i,d in enumerate(["south","east","north","west"])},"states":{"idle":[1],"move":[0,1,2,3],"cast":[],"hit":[],"death":[]},"notes":["2.5D raster candidate, not rigged 3D. Dedicated idle clip not supplied; idle uses one walk keyframe.","Attack/hit/death south-facing only; engine scale visual check required."]}
acts,ar=inspect("elite_actions",12,3)
import numpy as np
ap=round(ppm*np.median([f["region"][3] for f in acts[:4]])/np.median([f["region"][3] for f in frames[:4]]),3)
for f in acts: f.update(pixels_per_meter=ap,duration=.12,texture="res://chapter1/art/actors/elite_actions.png",direction="south"); meta["frames"].append(f)
meta["states"].update(cast=list(range(16,20)),attack=list(range(16,20)),hit=list(range(20,24)),death=list(range(24,28)))
(ACT/"elite.json").write_text(json.dumps(meta,indent=2)+"\n")
(ACT.parent.parent.parent/"plans/chapter1-c2-20261031-01/art/ELITE-INSPECTION.json").write_text(json.dumps([r,ar],indent=2)+"\n")
print(json.dumps([{k:v for k,v in x.items() if k!="frames"} for x in [r,ar]],indent=2))

