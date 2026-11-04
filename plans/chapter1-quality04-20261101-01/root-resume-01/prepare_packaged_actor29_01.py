from pathlib import Path
H=Path(__file__).parent
s=(H/'packaged_actor28.gd').read_text(encoding='utf-8').replace('Actual28','Actual29')
s=s.replace('func _finish() -> void:', '''var shadow_mesh_count := 0
var shadow_mesh_off := 0
func _count_shadows(node: Node) -> void:
	if node is MeshInstance3D:
		shadow_mesh_count+=1
		if node.cast_shadow!=GeometryInstance3D.SHADOW_CASTING_SETTING_ON:shadow_mesh_off+=1
	for child in node.get_children():_count_shadows(child)
func _finish() -> void:
	for actor in view.actors._pool25_root.get_children():
		if actor.has_meta("minion19"):_count_shadows(actor.get_meta("minion19").model)
	for actor in view.actors.actors.values():
		if actor.has_meta("minion19"):_count_shadows(actor.get_meta("minion19").model)''')
s=s.replace('"hit_blends":blends,','"hit_blends":blends,"shadow_mesh_count":shadow_mesh_count,"shadow_mesh_off":shadow_mesh_off,')
s=s.replace('same and blends>0 else 1','same and blends>0 and shadow_mesh_count>=224 and shadow_mesh_off==0 else 1')
p=H/'packaged_actor29.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(H/'run_packaged_hud27_01.py').read_text(encoding='utf-8').replace('full27','full29').replace('boss-phase01','shadow01').replace('packaged_hud27.gd','packaged_actor29.gd').replace('--hud27-dir=','--actor28-dir=').replace('chapter1.skill.frost','chapter1.skill.ember').replace('PASS ACTUAL27 BOSS PHASE','PASS ACTUAL29 LIVE SHADOW')
p=H/'run_packaged_actor29_01.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print('ACTUAL29 OBSERVER PREPARED; GPU NOT STARTED')
