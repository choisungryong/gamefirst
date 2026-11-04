import bpy,json,math
from pathlib import Path
ROOT=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01')
OUT=ROOT/'weight-inspection-01.json';assert not OUT.exists()
mesh=bpy.data.objects['mage'];rig=bpy.data.objects['deform_armature']
bones={b.name for b in rig.data.bones};valid={g.index:g.name for g in mesh.vertex_groups if g.name in bones}
unbound=[];bad=[];sums=[]
for v in mesh.data.vertices:
 weights=[(valid[g.group],g.weight) for g in v.groups if g.group in valid and g.weight>0.000001]
 total=sum(w for _,w in weights);sums.append(total)
 if total<.001:unbound.append({'index':v.index,'co':list(v.co),'groups':[(mesh.vertex_groups[g.group].name,g.weight) for g in v.groups]})
 if abs(total-1)>.01:bad.append(v.index)
data={'vertices':len(mesh.data.vertices),'unbound_count':len(unbound),'unbound':unbound,'sum_outside_0_99_1_01':len(bad),'bad_sum_vertices':bad,'min_sum':min(sums),'max_sum':max(sums),'invalid_groups':[g.name for g in mesh.vertex_groups if g.name not in bones]}
OUT.write_text(json.dumps(data,indent=2),encoding='utf-8');print('MAGE_WEIGHTS',json.dumps({k:v for k,v in data.items() if k not in ['unbound','bad_sum_vertices']}))
