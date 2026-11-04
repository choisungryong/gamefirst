from pathlib import Path
H=Path(__file__).parent
s=(H/'prepare_actor28_01.py').read_text(encoding='utf-8')
s=s.replace('actor28/fixture01','actor28/fixture02').replace('chapter1-actor28-fixture01','chapter1-actor28-fixture02')
s=s.replace("target=R/'chapter1/view/chapter_actors_quality28.gd';assert not target.exists();", "target=R/'chapter1/view/chapter_actors_quality28.gd';")
anchor="target=R/'chapter1/view/chapter_actors_quality28.gd'"
insertion='''source=source.replace('  rig.set_bone_pose(index,original.interpolate_with(pose,weight))', '''+repr('''  var blended := original.interpolate_with(pose,weight)
  if HIT28_BONES[i]=="Spine1":
   var recoil_axis := (rig.get_bone_global_rest(index).basis.inverse()*Vector3.RIGHT).normalized()
   blended.basis=blended.basis*Basis(recoil_axis,-.28*weight)
  rig.set_bone_pose(index,blended)''')+''')
'''
s=s.replace(anchor,insertion+anchor)
target=H/'prepare_actor28_02.py';assert not target.exists();target.write_text(s,encoding='utf-8');exec(compile(s,str(target),'exec'))
