from pathlib import Path
HERE=Path(__file__).parent
s=(HERE/'animate_chained_demon03.py').read_text(encoding='utf-8').replace("OUT=SOURCE/'motion-03'","OUT=SOURCE/'motion-04'")
s=s.replace("rig.animation_data_clear();rig.hide_set(False);rig.hide_viewport=False",'''before_counts={'vertices':len(mesh.data.vertices),'faces':len(mesh.data.polygons),'edges':len(mesh.data.edges)}
before_faces={tuple(p.vertices)for p in mesh.data.polygons}
mesh_changed=mesh.data.validate(verbose=True)
after_counts={'vertices':len(mesh.data.vertices),'faces':len(mesh.data.polygons),'edges':len(mesh.data.edges)}
validation={'changed':mesh_changed,'before':before_counts,'after':after_counts,'removed_faces':[list(p)for p in sorted(before_faces-{tuple(p.vertices)for p in mesh.data.polygons})]}
assert not mesh.data.validate(),'Derived mesh must validate before bake/export'
rig.animation_data_clear();rig.hide_set(False);rig.hide_viewport=False''')
start=s.index('def arms(style,k):');end=s.index('def pose(clip,t):')
s=s[:start]+'''def arm_vectors(style,side,sign):
 rest=Vector((sign*.39,-.05,-.92));fore=Vector((sign*.32,-.50,-.80))
 if style=='ready':return rest,fore
 if style=='slam':return Vector((sign*.42,.04,.91)),Vector((sign*.18,-.80,.5))
 if style=='slam_release':return Vector((sign*.31,-.76,-.57)),Vector((sign*.1,-.67,-.74))
 if style=='fan':return (Vector((sign*.82,-.3,.44))if side=='R'else Vector((sign*.5,-.1,-.8))),Vector((sign*.15,-.86,.48))
 return (Vector((sign*.15,-.97,.1))if side=='R'else Vector((sign*.6,-.5,-.5))),Vector((0,-.99,.1))
def arms(style,k,from_style='ready'):
 for side,sign in [('L',1),('R',-1)]:
  start_arm,start_fore=arm_vectors(from_style,side,sign);target_arm,target_fore=arm_vectors(style,side,sign)
  aim('Arm.'+side,start_arm.lerp(target_arm,k));aim('Forearm.'+side,start_fore.lerp(target_fore,k))
'''+s[end:]
s=s.replace("k=ease(t/.22);arms(style,1);arms(style+'_release',k)","k=ease(t/.22);arms(style+'_release',k,style)")
s=s.replace("else:arms(style+'_release',1-ease((t-.22)/.78))","else:arms('ready',ease((t-.22)/.78),style+'_release')")
s=s.replace("rotate('Spine2','X',18*math.sin(t*math.pi));rotate('Head','X',10*math.sin(t*math.pi))","bend=(-9+(18+9)*ease(t/.22))if t<.22 else 18*(1-ease((t-.22)/.78))\n  rotate('Spine2','X',bend);rotate('Head','X',bend*.65)")
s=s.replace("'maximum_bake_error_source_units':max_error,","'maximum_bake_error_source_units':max_error,'mesh_validation':validation,")
target=HERE/'animate_chained_demon04.py';assert not target.exists();target.write_text(s,encoding='utf-8')
print(str(target))
