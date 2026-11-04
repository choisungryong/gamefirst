"""Derived-art research only. Run on the immutable OGA blend with autoexec disabled.
Author own in-place IK poses; never claim supplied animation or alter source.
"""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
OUT=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01/motion-preview-01')
assert not OUT.exists()
OUT.mkdir()
scene=bpy.context.scene
rig=bpy.data.objects['control_armature']; deform=bpy.data.objects['deform_armature']; mesh=bpy.data.objects['mage']
for obj in bpy.data.objects:
    if obj.animation_data:obj.animation_data_clear()
for pb in rig.pose.bones:
    pb.location=(0,0,0);pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
scene.frame_set(1);bpy.context.view_layer.update()
# Repair legacy Blender Internal materials using the source's packed images.
mat=bpy.data.materials.new('Mage_PBR_derived_01');mat.use_nodes=True
n=mat.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.68
albedo=n.new('ShaderNodeTexImage');albedo.image=bpy.data.images['color.tga']
mat.node_tree.links.new(albedo.outputs['Color'],p.inputs['Base Color'])
normal=n.new('ShaderNodeTexImage');normal.image=bpy.data.images['normal.tga'];normal.image.colorspace_settings.name='Non-Color'
nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.65
mat.node_tree.links.new(normal.outputs['Color'],nm.inputs['Color']);mat.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
mesh.data.materials.clear();mesh.data.materials.append(mat)
def shift(name,v):
    pb=rig.pose.bones[name]
    pb.location=pb.bone.matrix_local.to_3x3().inverted() @ Vector(v)
def pose(frame):
    # One 24-frame stride at 40fps: 0.6 seconds, alternating support/swing feet.
    phase=2*math.pi*(frame-1)/24
    for side,offset,sign in [('L',0,1),('R',math.pi,-1)]:
        a=phase+offset
        # A grounded return stroke and a lifted forward swing. Negative Y faces front.
        y=.28*math.cos(a);lift=.14*max(0,math.sin(a))
        shift('foot_control.'+side,(0,y,lift))
        shift('hand_target.'+side,(-sign*.19,-.10-.14*math.cos(a),-.10+.03*math.sin(a)))
        shift('elbow_target.'+side,(0,-.25,0))
    shift('body',(0,0,.018+.024*math.cos(2*phase)))
    rig.pose.bones['spine.02'].rotation_euler=(math.radians(7),0,math.radians(3)*math.cos(phase))
    rig.pose.bones['head'].rotation_euler=(0,0,0)
    for name in ['body','hand_target.L','hand_target.R','foot_control.L','foot_control.R','elbow_target.L','elbow_target.R','spine.02']:
        pb=rig.pose.bones[name];pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_euler',frame=frame)
for f in range(1,26):pose(f)
rig.animation_data.action.name='Run_IK_authored_research_01'
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.render.fps=40;scene.frame_start=1;scene.frame_end=24
scene.world=bpy.data.worlds.new('PreviewWorld');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.24,.32,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for obj in list(bpy.data.objects):
    if obj.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(obj,do_unlink=True)
def light(name,loc,energy,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector((0,0,110))-obj.location).to_track_quat('-Z','Y').to_euler()
light('WarmKey',(200,-260,380),2700000,220,(1,.80,.59))
light('CoolRim',(-200,100,260),3500000,150,(.45,.65,1))
light('FrontFill',(0,-300,140),900000,200,(.65,.78,1))
data=bpy.data.cameras.new('PreviewCamera');camera=bpy.data.objects.new('PreviewCamera',data);scene.collection.objects.link(camera)
camera.location=(290,-440,330);target=Vector((0,0,100));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO';data.ortho_scale=245;scene.camera=camera
scene.view_settings.view_transform='AgX'
data_out={'scope':'Research, not runtime adoption. Source rigged model has no certified run clip. Own IK cycle authored here. CC-BY-SA3.0 derivative.', 'source':'../mage_final.blend','frames':[]}
for f in [1,7,13,19]:
    scene.frame_set(f);bpy.context.view_layer.update()
    data_out['frames'].append({'frame':f,'feet':{s:list((rig.matrix_world @ rig.pose.bones['tarsal.'+s].matrix).translation) for s in ['L','R']}})
    scene.render.filepath=str(OUT/('run_%02d.png'%f));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mage_motion_research.blend'))
(OUT/'REPORT.json').write_text(json.dumps(data_out,indent=2),encoding='utf-8')
print('MAGE_PREVIEW_DONE',str(OUT))
