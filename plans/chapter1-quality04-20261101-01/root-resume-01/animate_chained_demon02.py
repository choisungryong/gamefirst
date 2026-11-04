"""Own FK poses for the public Mophs rig, not a claim of original author clips.
Blender4.5.15 --disable-autoexec, from preview-01 derived material file only.
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
SOURCE=Path('C:/Project/game-research/art-sources/oga-chained-demon-20261101-01')
OUT=SOURCE/'motion-02';assert not OUT.exists();OUT.mkdir()
scene=bpy.context.scene;rig=bpy.data.objects['Rig'];mesh=bpy.data.objects['ChainedDemon']
rig.animation_data_clear();rig.hide_set(False);rig.hide_viewport=False
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4);pb.rotation_mode='QUATERNION'
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
root=rig.data.edit_bones.new('RootMotion');root.head=(0,0,0);root.tail=(0,0,1);root.use_deform=True
for name in ['Spine1','Hip.L','Hips.R']:rig.data.edit_bones[name].parent=root
bpy.ops.object.mode_set(mode='OBJECT')
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4);pb.rotation_mode='QUATERNION'
bpy.context.view_layer.update()
foot_rest={s:rig.pose.bones['Foot.'+s].tail.copy()for s in ['L','R']}
def reset():
 for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
def rotate(name,axis,angle):
 pb=rig.pose.bones[name];head=pb.head.copy()
 pb.matrix=Matrix.Translation(head)@Matrix.Rotation(math.radians(angle),4,axis)@Matrix.Translation(-head)@pb.matrix
 bpy.context.view_layer.update()
def aim(name,direction):
 pb=rig.pose.bones[name];head=pb.head.copy();q=(pb.tail-pb.head).normalized().rotation_difference(Vector(direction).normalized())
 pb.matrix=Matrix.Translation(head)@q.to_matrix().to_4x4()@Matrix.Translation(-head)@pb.matrix
 bpy.context.view_layer.update()
def shift(name,delta):
 pb=rig.pose.bones[name];pb.location=pb.bone.matrix_local.to_3x3().inverted()@Vector(delta)
 bpy.context.view_layer.update()
def ease(t):return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))
def ready(phase=0):
 for side,sign in [('L',1),('R',-1)]:
  aim('Arm.'+side,(sign*.39,-.05,-.92));aim('Forearm.'+side,(sign*.32,-.50,-.80))
  for i in range(5):rotate('Chain.'+side+('.%03d'%i if i else ''),'X',math.sin(phase+i*.45)*3)
def arms(style,k):
 for side,sign in [('L',1),('R',-1)]:
  rest=Vector((sign*.39,-.05,-.92));fore=Vector((sign*.32,-.50,-.80))
  if style=='slam':target=Vector((sign*.42,.04,.91));hand=Vector((sign*.18,-.80,.5))
  elif style=='slam_release':target=Vector((sign*.31,-.76,-.57));hand=Vector((sign*.1,-.67,-.74))
  elif style=='fan':target=Vector((sign*.82,-.3,.44))if side=='R'else Vector((sign*.5,-.1,-.8));hand=Vector((sign*.15,-.86,.48))
  else:target=Vector((sign*.15,-.97,.1))if side=='R'else Vector((sign*.6,-.5,-.5));hand=Vector((0,-.99,.1))
  aim('Arm.'+side,rest.lerp(target,k));aim('Forearm.'+side,fore.lerp(hand,k))
def pose(clip,t):
 reset();phase=t*math.tau;ready(phase)
 if clip in ['idle','walk']:
  rotate('Spine2','X',-2+math.sin(phase)*1.5)
  if clip=='walk':
   shift('Spine1',(0,-.12,-.08+.10*math.cos(phase*2)))
   for side,off in [('L',0),('R',math.pi)]:
    a=phase+off
    rotate('Thigh.'+side,'X',19*math.cos(a));rotate('FirstKnee.'+side,'X',-12*max(0,math.sin(a)))
    aim('Foot.'+side,(0,-.42,-.91))
    current=rig.pose.bones['Foot.'+side].tail.copy();target=foot_rest[side]+Vector((0,1.4*math.cos(a),.65*max(0,math.sin(a))))
    shift('Hip.L'if side=='L'else'Hips.R',target-current)
    rotate('Arm.'+side,'X',7*math.cos(a))
 elif clip.startswith('windup_'):
  style=clip.split('_')[1];k=ease(t);arms(style,k);rotate('Spine2','X',-9*k);rotate('Head','X',-9*k)
 elif clip in ['slam','fan']:
  style=clip
  if t<.22:
   k=ease(t/.22);arms(style,1);arms(style+'_release',k)
  else:arms(style+'_release',1-ease((t-.22)/.78))
  rotate('Spine2','X',18*math.sin(t*math.pi));rotate('Head','X',10*math.sin(t*math.pi))
 elif clip=='hit':
  k=math.sin(t*math.pi);rotate('Spine2','X',-11*k);rotate('Head','X',-14*k)
 elif clip=='death':
  k=ease(t);rotate('Spine2','X',12*k);arms('slam_release',.55*k)
 bpy.context.view_layer.update()
clips={'idle':49,'walk':49,'windup_slam':37,'windup_fan':37,'slam':25,'fan':25,'hit':13,'death':45}
samples={};foot_report=[]
for clip,count in clips.items():
 frames=[]
 for f in range(count):
  t=f/(count-1);pose(clip,t)
  matrices={p.name:p.matrix.copy()for p in rig.pose.bones}
  if clip=='death':
   k=ease(t);rotation=Matrix.Rotation(math.radians(-82)*k,4,'X')@Matrix.Rotation(math.radians(17)*k,4,'Z')
   evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());points=[rotation@(mesh.matrix_world@v.co)for v in evaluated.data.vertices]
   lift=max(0,.02-min(v.z for v in points));trans=Matrix.Translation((0,0,lift))@rotation
   matrices={name:trans@m for name,m in matrices.items()}
  frames.append(matrices)
  if clip=='walk'and f in [0,12,24,36,48]:foot_report.append({'frame':f,'left':list(rig.pose.bones['Foot.L'].tail),'right':list(rig.pose.bones['Foot.R'].tail)})
 samples[clip]=frames
def depth(pb):return 0 if pb.parent is None else 1+depth(pb.parent)
bones=sorted(rig.pose.bones,key=depth)
rig.animation_data_create();max_error=0.0
for clip,frames in samples.items():
 action=bpy.data.actions.new(clip);rig.animation_data.action=action
 for f,matrices in enumerate(frames,1):
  for pb in bones:pb.matrix=matrices[pb.name]
  bpy.context.view_layer.update()
  max_error=max(max_error,max(abs(pb.matrix[r][c]-matrices[pb.name][r][c])for pb in bones for r in range(4)for c in range(4)))
  for pb in bones:
   pb.keyframe_insert('location',frame=f);pb.keyframe_insert('rotation_quaternion',frame=f);pb.keyframe_insert('scale',frame=f)
 track=rig.animation_data.nla_tracks.new();track.name=clip;strip=track.strips.new(clip,1,action);strip.action_frame_start=1;strip.action_frame_end=len(frames)
 rig.animation_data.action=None
assert max_error<.0003,max_error
root_obj=bpy.data.objects.new('DemonMetres',None);scene.collection.objects.link(root_obj);rig.parent=root_obj;root_obj.scale=(3.4/13,)*3
scene.render.fps=40
for o in bpy.context.selected_objects:o.select_set(False)
for o in [root_obj,rig,mesh]:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'chained_demon_animated_source.blend'))
target=OUT/'chained_demon_animated.glb'
bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_bake_animation=True,export_def_bones=True,export_cameras=False,export_lights=False,export_extras=False,export_yup=True,export_influence_nb=8)
report={'source':'../extracted/Chained_Demon/ChainedDemon.blend','author':'Mophs','license':'CC-BY3.0 selected alternative','scope':'Own authored eight clips on public rig; source unnamed Action was visually constant in8 samples. Not runtime/art approval.','clips':clips,'fps':40,'bones_blender':len(rig.data.bones),'height_target_m':3.4,'maximum_bake_error_source_units':max_error,'walk_feet':foot_report,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'changes':['new RootMotion parent','ready/stride/windup/slam/fan/recoil/ground-safe fall authored in code','packed legacy diffuse converted to PBR','edge-split disabled, smooth shading','metre scaling']}
with(OUT/'REPORT.json').open('x',encoding='utf-8')as f:json.dump(report,f,indent=2)
print('CHAINED_DEMON_MOTION_DONE',json.dumps({'glb':str(target),'sha256':report['sha256'],'bytes':report['bytes'],'clips':8,'bones':report['bones_blender'],'max_bake_error':max_error}))
