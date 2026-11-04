extends "res://replay.gd"
var captured: Dictionary={}
func _process(delta: float) -> void:
	super._process(delta)
	if not armed:return
	for actor in actors.actors.values():
		if not actor.has_meta("minion19"):continue
		var e: Dictionary=actors._entity(actor)
		var pose: Dictionary=actor.get_meta("minion19_pose",{})
		var clip := String(pose.get("clip",""))
		if clip not in ["windup_slam","windup_fan","slam","fan"]:continue
		var key := String(e.kind)+"-"+String(e.state)+"-"+clip
		if captured.has(key):continue
		captured[key]={"tick":run.tick,"id":e.id,"position":e.position,"direction":e.attack_direction,"pose":pose.duplicate(true),"state":e.state,"hero":run.hero.position}
		_capture_attack19(key)
func _capture_attack19(key: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://attack-shots")
	get_viewport().get_texture().get_image().save_png("res://attack-shots/"+key+".png")
func _print_result() -> void:
	super._print_result()
	_save("attacks",{"captured":captured,"scope":"Actual normal policy/earned build attack frames in30s fixed60 GPU; no staged combat entity changes, no manual/performance claim."})
