import bpy,json,hashlib
from pathlib import Path
SOURCE=Path('C:/Project/game-research/art-sources/oga-chained-demon-20261101-01')
OUT=SOURCE/'material-05';assert not OUT.exists();OUT.mkdir()
mesh=bpy.data.objects['ChainedDemon'];rig=bpy.data.objects['Rig'];root=bpy.data.objects['DemonMetres']
assert not mesh.data.validate(),'motion04 saved mesh should already be valid'
original=mesh.data.materials[0]
materials=[]
for name,metal,rough in [('WardenSkin',0,.84),('WardenMask',.35,.62),('WardenChain',.64,.46)]:
 m=original.copy();m.name=name;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;materials.append(m)
mesh.data.materials.clear()
for m in materials:mesh.data.materials.append(m)
groups={g.index:g.name for g in mesh.vertex_groups}
counts={m.name:0 for m in materials}
for face in mesh.data.polygons:
 head=chain=0
 for index in face.vertices:
  v=mesh.data.vertices[index]
  head+=sum(g.weight for g in v.groups if groups[g.group]=='Head')
  chain+=sum(g.weight for g in v.groups if groups[g.group].startswith('Chain.'))
 head/=len(face.vertices);chain/=len(face.vertices)
 face.material_index=2 if chain>.65 else (1 if head>.65 else 0);counts[materials[face.material_index].name]+=1
for o in bpy.context.selected_objects:o.select_set(False)
for o in [root,rig,mesh]:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'chained_warden_source.blend'))
target=OUT/'chained_warden.glb'
bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_bake_animation=True,export_def_bones=True,export_cameras=False,export_lights=False,export_extras=False,export_yup=True,export_influence_nb=8)
with(OUT/'REPORT.json').open('x',encoding='utf-8')as f:json.dump({'scope':'Research. Same own8clips as motion04; head/chain/skin separated by source weights for metal/skin response, same original diffuse pixels. Not runtime adoption or art approval.','source':'../motion-04/chained_demon_animated_source.blend','source_weight_clamp_notes':'Motion04 mesh validation clamped original vertices100/104 group66 and442/446 group71 (weights1.000497/1.021464 from raw log); GLTF normalizes final influences. Original files unchanged.','material_face_counts':counts,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size},f,indent=2)
print('WARDEN_MATERIAL_EXPORT',json.dumps({'glb':str(target),'faces':counts,'bytes':target.stat().st_size}))
