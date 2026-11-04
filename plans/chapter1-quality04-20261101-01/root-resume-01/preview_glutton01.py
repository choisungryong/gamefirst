import bpy,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path('C:/Project/game-research/art-sources/oga-glutton-20261101-01/preview-01');assert not OUT.exists();OUT.mkdir()
scene=bpy.context.scene;rig=bpy.data.objects['glutton_armature'];mesh=bpy.data.objects['glutton.lopoly']
mat=bpy.data.materials.new('Glutton_PBR_derived_01');mat.use_nodes=True
n=mat.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.68
albedo=n.new('ShaderNodeTexImage');albedo.image=bpy.data.images['gluttonPaint.png'];albedo.image.colorspace_settings.name='sRGB'
mat.node_tree.links.new(albedo.outputs['Color'],p.inputs['Base Color'])
normal=n.new('ShaderNodeTexImage');normal.image=bpy.data.images['paint'];normal.image.colorspace_settings.name='Non-Color'
nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.7
mat.node_tree.links.new(normal.outputs['Color'],nm.inputs['Color']);mat.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
mesh.data.materials.clear();mesh.data.materials.append(mat)
for face in mesh.data.polygons:face.material_index=0;face.use_smooth=True
for obj in list(bpy.data.objects):
 if obj.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(obj,do_unlink=True)
scene.frame_set(0);bpy.context.view_layer.update()
evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
points=[evaluated.matrix_world@v.co for v in evaluated.data.vertices]
bottom=min(v.z for v in points);top=max(v.z for v in points)
center=Vector(((min(v.x for v in points)+max(v.x for v in points))*.5,(min(v.y for v in points)+max(v.y for v in points))*.5,(bottom+top)*.5))
height=top-bottom
scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world=bpy.data.worlds.new('ResearchWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.21,.28,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
def light(name,offset,energy,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=height*.8;d.color=color
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=center+Vector(offset)*height;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
light('WarmKey',(1,-1.4,1.6),height*height*95,(1,.81,.64));light('ColdRim',(-1,1,1.1),height*height*115,(.48,.68,1));light('SoftFill',(-.2,-1.5,.3),height*height*25,(.75,.84,1))
d=bpy.data.cameras.new('ResearchCamera');o=bpy.data.objects.new('ResearchCamera',d);scene.collection.objects.link(o);scene.camera=o
o.location=center+Vector((1,-1.7,1.1))*height;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=height*1.35
scene.view_settings.view_transform='AgX'
records=[]
for frame in [0,6,12,18]:
 scene.frame_set(frame);bpy.context.view_layer.update()
 scene.render.filepath=str(OUT/('walk-%02d.png'%frame));bpy.ops.render.render(write_still=True)
 records.append({'frame':frame,'feet':{side:list(rig.matrix_world@rig.pose.bones['leg_'+side+'.002'].tail)for side in ['L','R']}})
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'glutton_material_research.blend'))
with(OUT/'REPORT.json').open('x',encoding='utf-8')as f:json.dump({'scope':'Public CC0 research preview, not runtime adoption or final art approval','source':'../glutton_final.blend','bounds_z':[bottom,top],'height_source_units':height,'frames':records,'changes':'Legacy Blender Internal to PBR using source packed diffuse/normal; smooth shading; author walk unchanged'},f,indent=2)
print('GLUTTON_PREVIEW_DONE',str(OUT))
