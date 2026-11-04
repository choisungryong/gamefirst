extends "res://replay.gd"
var observed: Dictionary={}
var modal_checks := 0
var cold_hidden := 0
var paid_releases := 0
var core_checks := 0
func _process(delta: float) -> void:
	super._process(delta)
	if not armed:return
	for actor in actors.actors.values():
		if not actor.has_meta("minion19"):continue
		var pose: Dictionary=actor.get_meta("minion19_pose",{})
		var clip := String(pose.get("clip","none"))
		observed[clip]=int(observed.get(clip,0))+1
		var entity: Dictionary=actors._entity(actor)
		if entity.state=="recover" and actors._demon19_attacks.has(entity.id) and clip in ["slam","fan"]:
			assert(float(pose.time)>=actors.RELEASE_TIME);paid_releases+=1
		var key := "%d:%d"%[entity.generation,entity.id]
		if actors._cold_corpses.has(key) and float(actors._cold_corpses[key].age)>.23:
			assert(not entity.elite and entity.kind!="elite")
			for mat in actor.get_meta("minion19").materials:assert(mat.albedo_color.a<.001)
			cold_hidden+=1
	if modal_checks==0 and age>1.0:
		var snapshot: Dictionary=run.snapshot().duplicate(true)
		var mode_: String=run.mode
		for modal in ["paused","choice","inventory","equipment"]:
			run.mode=modal
			var before: Dictionary={}
			for key in actors.actors:
				var actor: Node3D=actors.actors[key]
				if actor.has_meta("minion19"):before[key]={"pose":actor.get_meta("minion19_pose",{}).duplicate(true),"death":actor.get_meta("minion19").death_age}
			var cold_before: Dictionary=actors._cold_corpses.duplicate(true)
			actors.sync(run,.2)
			for key in before:
				var actor: Node3D=actors.actors[key]
				assert(before[key].pose==actor.get_meta("minion19_pose",{}))
				assert(before[key].death==actor.get_meta("minion19").death_age)
			assert(cold_before==actors._cold_corpses)
			modal_checks+=1
		run.mode=mode_
		assert(snapshot==run.snapshot());core_checks+=1
func _print_result() -> void:
	super._print_result()
	_save("semantics",{"observed_frames":observed,"modal_checks":modal_checks,"core_checks":core_checks,"paid_release_frames":paid_releases,"cold_hidden_frames":cold_hidden,"scope":"30s fixed60 earned replay; modal suspension and cold materials checked against actual entities; no manual or performance claim."})
