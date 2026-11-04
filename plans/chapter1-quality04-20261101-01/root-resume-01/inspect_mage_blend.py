import bpy,json
from pathlib import Path
OUT=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01/inspect-01.json')
assert not OUT.exists()
data={'blender_version':bpy.app.version_string,'file':bpy.data.filepath,'objects':[],'materials':[],'images':[],'actions':[]}
for obj in bpy.data.objects:
    item={'name':obj.name,'type':obj.type,'location':list(obj.location),'rotation':list(obj.rotation_euler),'scale':list(obj.scale),'dimensions':list(obj.dimensions)}
    if obj.type=='ARMATURE':
        item['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'deform':b.use_deform} for b in obj.data.bones]
        item['constraints']={p.name:[{'name':c.name,'type':c.type} for c in p.constraints] for p in obj.pose.bones if p.constraints}
    elif obj.type=='MESH':
        item['vertices']=len(obj.data.vertices);item['polygons']=len(obj.data.polygons)
        item['materials']=[m.name if m else None for m in obj.data.materials]
        item['vertex_groups']=[g.name for g in obj.vertex_groups]
        item['modifiers']=[{'name':m.name,'type':m.type} for m in obj.modifiers]
    data['objects'].append(item)
for mat in bpy.data.materials:
    data['materials'].append({'name':mat.name,'use_nodes':mat.use_nodes,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in mat.node_tree.nodes] if mat.node_tree else []})
for image in bpy.data.images:
    data['images'].append({'name':image.name,'path':image.filepath,'size':list(image.size),'packed_bytes':image.packed_file.size if image.packed_file else 0})
for action in bpy.data.actions:data['actions'].append({'name':action.name,'frame_range':list(action.frame_range)})
with OUT.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print('MAGE_INSPECTION',json.dumps({'objects':len(data['objects']),'armatures':[o['name'] for o in data['objects'] if o['type']=='ARMATURE'],'images':data['images'],'actions':data['actions']}))
