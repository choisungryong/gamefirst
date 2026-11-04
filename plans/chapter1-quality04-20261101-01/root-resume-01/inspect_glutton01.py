import bpy,json
from pathlib import Path
OUT=Path('C:/Project/game-research/art-sources/oga-glutton-20261101-01/inspect-01.json')
assert not OUT.exists()
def vec(v):return list(v)
data={'blender':bpy.app.version_string,'scene':{'fps':bpy.context.scene.render.fps,'start':bpy.context.scene.frame_start,'end':bpy.context.scene.frame_end},'objects':[],'images':[],'actions':[],'materials':[]}
for o in bpy.data.objects:
 row={'name':o.name,'type':o.type,'location':vec(o.location),'scale':vec(o.scale),'rotation':vec(o.rotation_euler),'parent':o.parent.name if o.parent else None,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None}
 if o.type=='ARMATURE':row['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'deform':b.use_deform,'head':vec(b.head_local),'tail':vec(b.tail_local)}for b in o.data.bones];row['constraints']=[{'bone':p.name,'types':[c.type for c in p.constraints]}for p in o.pose.bones if p.constraints]
 if o.type=='MESH':
  o.data.calc_loop_triangles();row.update(vertices=len(o.data.vertices),triangles=len(o.data.loop_triangles),groups=[g.name for g in o.vertex_groups],modifiers=[{'type':m.type,'object':m.object.name if hasattr(m,'object')and m.object else None}for m in o.modifiers],materials=[m.name if m else None for m in o.data.materials],bounds=[vec(o.matrix_world@__import__('mathutils').Vector(p))for p in o.bound_box],unweighted=[v.index for v in o.data.vertices if sum(g.weight for g in v.groups)<.001])
 if o.animation_data:row['nla']=[{'name':t.name,'strips':[{'name':s.name,'action':s.action.name if s.action else None,'start':s.frame_start,'end':s.frame_end}for s in t.strips]}for t in o.animation_data.nla_tracks]
 data['objects'].append(row)
for im in bpy.data.images:data['images'].append({'name':im.name,'size':vec(im.size),'packed':bool(im.packed_file),'filepath':im.filepath})
for a in bpy.data.actions:data['actions'].append({'name':a.name,'range':vec(a.frame_range),'curves':len(a.fcurves) if hasattr(a,'fcurves')else None,'markers':[{'name':m.name,'frame':m.frame}for m in a.pose_markers]})
for m in bpy.data.materials:
 data['materials'].append({'name':m.name,'use_nodes':m.use_nodes,'diffuse':list(m.diffuse_color),'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if hasattr(n,'image')and n.image else None}for n in m.node_tree.nodes] if m.use_nodes else []})
with OUT.open('x',encoding='utf-8')as f:json.dump(data,f,indent=2)
print('GLUTTON_INVENTORY',json.dumps({'objects':len(data['objects']),'actions':data['actions'],'images':data['images']}))
