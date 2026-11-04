import bpy,json
from pathlib import Path
from mathutils import Vector
SOURCE=Path('C:/Project/game-research/art-sources/oga-chained-demon-20261101-01')
OUT=SOURCE/'preview-01';assert not OUT.exists();OUT.mkdir()
scene=bpy.context.scene;rig=bpy.data.objects['Rig'];mesh=bpy.data.objects['ChainedDemon']
mat=bpy.data.materials.new('ChainedDemon_PBR_derived_01');mat.use_nodes=True
n=mat.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.78
albedo=n.new('ShaderNodeTexImage');albedo.image=bpy.data.images.load(str(SOURCE/'extracted/Chained_Demon/diffuse.png'),check_existing=True);albedo.image.pack();albedo.image.colorspace_settings.name='sRGB'
mat.node_tree.links.new(albedo.outputs['Color'],p.inputs['Base Color'])
mesh.data.materials.clear();mesh.data.materials.append(mat)
for face in mesh.data.polygons:face.material_index=0;face.use_smooth=True
for m in mesh.modifiers:
 if m.type=='EDGE_SPLIT':m.show_viewport=False;m.show_render=False
for obj in list(bpy.data.objects):
 if obj.type in {'CAMERA','LIGHT','EMPTY'}:bpy.data.objects.remove(obj,do_unlink=True)
height=13.0;center=Vector((0,0,6.4))
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world=bpy.data.worlds.new('ResearchWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.21,.28,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
def light(name,offset,energy,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=height*.8;d.color=color
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=center+Vector(offset)*height;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
light('WarmKey',(1,-1.4,1.6),height*height*80,(1,.81,.64));light('ColdRim',(-1,1,1.1),height*height*95,(.48,.68,1));light('SoftFill',(-.2,-1.5,.3),height*height*25,(.75,.84,1))
d=bpy.data.cameras.new('ResearchCamera');o=bpy.data.objects.new('ResearchCamera',d);scene.collection.objects.link(o);scene.camera=o
o.location=center+Vector((1,-1.7,1.1))*height;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=height*1.65
scene.view_settings.view_transform='AgX'
records=[]
for frame in [1,25,50,75,100,125,150,175]:
 scene.frame_set(frame);bpy.context.view_layer.update()
 scene.render.filepath=str(OUT/('source-action-%03d.png'%frame));bpy.ops.render.render(write_still=True)
 records.append({'frame':frame,'bones':{n:list(rig.pose.bones[n].rotation_quaternion)for n in ['Spine1','Arm.L','Thigh.L','Head']}})
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'chained_demon_material_research.blend'))
with(OUT/'REPORT.json').open('x',encoding='utf-8')as f:json.dump({'scope':'Author describes unanimated rig, but file includes unnamed Action1..175. Sampled to identify actual content; not certified combat clips or runtime adoption.','source':'../extracted/Chained_Demon/ChainedDemon.blend','frames':records,'changes':'Legacy material to packed PBR diffuse, smooth shading/edge split disabled in new derived file'},f,indent=2)
print('CHAINED_DEMON_PREVIEW_DONE',str(OUT))
