"""Bake own control poses into the public mage's deform rig, then export GLB.
Run against motion-preview-01/mage_motion_research.blend, --disable-autoexec.
All derivatives are research assets until actual Godot visual comparison.
"""
import bpy, math, json, hashlib
from mathutils import Vector
from pathlib import Path
OUT=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01/gltf-preview-03')
assert not OUT.exists();OUT.mkdir()
scene=bpy.context.scene;rig=bpy.data.objects['control_armature'];deform=bpy.data.objects['deform_armature'];mesh=bpy.data.objects['mage']
for obj in [rig,deform,mesh]:
    if obj.animation_data:obj.animation_data_clear()
def reset():
    for pb in rig.pose.bones:
        pb.location=(0,0,0);pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
def shift(name,v):
    pb=rig.pose.bones[name];pb.location=pb.bone.matrix_local.to_3x3().inverted()@Vector(v)
def base():
    for side,sign in [('L',1),('R',-1)]:
        shift('hand_target.'+side,(-sign*.23,-.10,-.13));shift('elbow_target.'+side,(0,-.25,0))
def pose(clip,f,count):
    reset();base();t=(f-1)/(count-1);phase=t*math.tau
    if clip=='run':
        for side,off,sign in [('L',0,1),('R',math.pi,-1)]:
            a=phase+off
            shift('foot_control.'+side,(0,.36*math.cos(a),.15*max(0,math.sin(a))))
            shift('hand_target.'+side,(-sign*.23,-.10-.15*math.cos(a),-.08+.03*math.sin(a)))
        shift('body',(0,0,.012+.018*math.cos(phase*2)))
        rig.pose.bones['spine.02'].rotation_euler=(math.radians(8),0,math.radians(3)*math.cos(phase))
    elif clip=='idle':
        shift('body',(0,0,.005+.007*math.sin(phase)))
        rig.pose.bones['spine.02'].rotation_euler=(math.radians(2)*math.sin(phase),0,0)
    elif clip=='cast':
        # 0-.2 anticipation, .2-.45 release, .45-1 recovery; real cast events
        # must seek to release and cannot retroactively delay core damage.
        k=min(1,t/.25) if t<=.25 else max(0,(1-t)/.75)
        shift('hand_target.R',(.23,-.10-.60*k,-.13+.43*k))
        shift('hand_target.L',(-.23,-.10-.30*k,-.13+.20*k))
        rig.pose.bones['spine.02'].rotation_euler=(math.radians(7)*k,0,math.radians(-9)*k)
    elif clip=='hit':
        k=math.sin(t*math.pi)
        shift('body',(0,.045*k,-.025*k));rig.pose.bones['spine.02'].rotation_euler=(math.radians(-13)*k,0,0)
    elif clip=='death':
        k=t*t*(3-2*t)
        shift('body',(0,.32*k,-.87*k));rig.pose.bones['body'].rotation_euler=(math.radians(-68)*k,0,math.radians(12)*k)
    bpy.context.view_layer.update()
clips={'idle':49,'run':25,'cast':25,'hit':13,'death':37}
sampled={};checks=[]
for clip,count in clips.items():
    frames=[]
    for f in range(1,count+1):
        pose(clip,f,count)
        frames.append({p.name:p.matrix.copy() for p in deform.pose.bones})
    sampled[clip]=frames
# Constraint evaluation is now frozen into transforms. Discard controls and
# legacy source actions in this NEW derived file, never in source.
for pb in deform.pose.bones:
    for c in list(pb.constraints):pb.constraints.remove(c)
    pb.rotation_mode='QUATERNION'
bpy.data.objects.remove(rig,do_unlink=True)
for action in list(bpy.data.actions):bpy.data.actions.remove(action)
deform.animation_data_create()
for clip,frames in sampled.items():
    action=bpy.data.actions.new(clip);action.use_fake_user=True;deform.animation_data.action=action
    for f,matrices in enumerate(frames,1):
        for pb in deform.pose.bones:
            kwargs={}
            if pb.parent:kwargs={'parent_matrix':matrices[pb.parent.name],'parent_matrix_local':pb.parent.bone.matrix_local}
            pb.matrix_basis=pb.bone.convert_local_to_pose(matrices[pb.name],pb.bone.matrix_local,invert=True,**kwargs)
            pb.keyframe_insert('location',frame=f);pb.keyframe_insert('rotation_quaternion',frame=f);pb.keyframe_insert('scale',frame=f)
        bpy.context.view_layer.update()
        # Verify no parent/scale conversion drift in the baked armature.
        worst=max(max(abs(pb.matrix[r][c]-matrices[pb.name][r][c]) for r in range(4) for c in range(4)) for pb in deform.pose.bones)
        assert worst<.002,(clip,f,worst)
        checks.append(worst)
    track=deform.animation_data.nla_tracks.new();track.name=clip
    strip=track.strips.new(clip,1,action);strip.name=clip;strip.action_frame_start=1;strip.action_frame_end=len(frames)
    track.mute=True
    deform.animation_data.action=None
# NLA_TRACKS exporter evaluates one named track at a time, regardless of mute.
for track in deform.animation_data.nla_tracks:track.mute=False
scene.render.fps=40;scene.frame_start=1;scene.frame_end=49
# Apply centimetres -> metres through one neutral parent, preserving bind poses.
root=bpy.data.objects.new('MageMetres',None);scene.collection.objects.link(root);root.scale=(.01,.01,.01)
deform.parent=root;mesh.parent=deform
bpy.ops.object.select_all(action='DESELECT')
for collection in bpy.data.collections:collection.hide_viewport=False
for obj in [root,mesh,deform]:
    obj.hide_viewport=False;obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=deform
props=bpy.ops.export_scene.gltf.get_rna_type().properties
assert 'NLA_TRACKS' in [e.identifier for e in props['export_animation_mode'].enum_items]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mage_animated_source.blend'))
gltf=OUT/'mage_animated.glb'
bpy.ops.export_scene.gltf(filepath=str(gltf),export_format='GLB',use_selection=True,export_animations=True,
    export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,
    export_bake_animation=True,export_def_bones=True,export_cameras=False,export_lights=False,
    export_extras=False,export_yup=True,export_influence_nb=8)
report={'source':'../mage_final.blend','derived_blend':'mage_animated_source.blend','output':gltf.name,
 'sha256':hashlib.sha256(gltf.read_bytes()).hexdigest(),'bytes':gltf.stat().st_size,'clips':clips,
 'fps':40,'bones':len(deform.data.bones),'maximum_bake_matrix_error_source_units':max(checks),
 'license':'CC-BY-SA-3.0','authors':'thecubber; original rig credited to Julius/OGA',
 'changes':'Legacy material conversion, own IK poses baked into deformation skeleton, metre root. Research only, not runtime adoption.',
 'documentation':['https://docs.blender.org/manual/en/3.2/addons/import_export/scene_gltf2.html','https://docs.godotengine.org/en/4.5/tutorials/animation/animation_tree.html']}
(OUT/'REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('MAGE_GLTF_DONE',json.dumps(report))
