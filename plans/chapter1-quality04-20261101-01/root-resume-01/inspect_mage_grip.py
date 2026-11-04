import bpy,json
from pathlib import Path
OUT=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01/grip-inspection-01.json');assert not OUT.exists()
rig=bpy.data.objects['control_armature'];result={}
for name in ['fist_r','fist_l','finger_pinky_control_r','finger_ring_control_r','finger_index.03.R','thumb_control_r']:
 pb=rig.pose.bones[name];items=[]
 for c in pb.constraints:
  fields={}
  for key in ['type','transform_channel','min','max','frame_start','frame_end','min_x','max_x','min_y','max_y','min_z','max_z','owner_space','target_space','subtarget']:
   if hasattr(c,key):fields[key]=getattr(c,key)
  if hasattr(c,'action'):fields['action']=c.action.name if c.action else None
  items.append(fields)
 result[name]={'location':list(pb.location),'constraints':items}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
