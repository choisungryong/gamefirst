extends "res://chapter1/view/chapter_elements_quality16.gd"
## After actual victory, expire only the combat presentation, retaining loot.
var _ending20_age := 0.0
var _ending20_active := false
const ENDING20_NODES := ["projectiles","shards","impacts","plumes","telegraph","telegraph_fill","beams","arc_surface","ice_batch","ice_fragment_batch","ward_rings","ward_fill","contact_batch"]
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	if run.mode=="victory":_ending20_active=true
	if not _ending20_active:return
	if run.mode=="victory":_ending20_age+=maxf(0,delta)
	var fade := smoothstep(.08,.55,_ending20_age)
	for name_ in ENDING20_NODES:
		var node: GeometryInstance3D=get(name_)
		node.transparency=fade
		if fade>=1:node.visible=false
	if fade>=1:shadows.multimesh.visible_instance_count=1
func reset() -> void:
	super.reset();_ending20_age=0;_ending20_active=false
	for name_ in ENDING20_NODES:
		var node: GeometryInstance3D=get(name_)
		if is_instance_valid(node):node.transparency=0;node.visible=true
