extends "res://chapter1/chapter_one_view.gd"
var age := 0.0
var shots: Dictionary={}
var armed := false
var samples: Array[Dictionary]=[]
func _ready() -> void:
	super._ready()
	while run.tick<23830:run.step(full_pilot.decide())
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);hud.sync(run,0)
	_save20("start",run.snapshot());armed=true
func _save20(label: String,value: Variant) -> void:
	var f := FileAccess.open("res://ending20-"+label+".json",FileAccess.WRITE);f.store_string(JSON.stringify(value,"\t"));f.close()
func _process(delta: float) -> void:
	super._process(delta)
	if not armed:return
	age+=delta
	for at in [.8,1.35,1.75,2.1]:
		if age>=at and not shots.has(str(at)):
			shots[str(at)]=true
			var boss_pose: Dictionary={}
			for actor in actors.actors.values():
				if actor.has_meta("enemy_rig"):
					var model: Node3D=actor.get_meta("enemy_rig").model
					boss_pose={"dead_age":actor.get_meta("warden_death_age",-1),"rotation_z":model.rotation.z,"model_y":model.position.y,"collapse":actor.get_meta("warden20_collapse",-1)}
			samples.append({"at":at,"mode":run.mode,"boss":boss_pose,"fx_hidden":not effects.projectiles.visible,"reward_visible":hud.overlay.visible})
			_shot20(at)
func _shot20(at: float) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://ending20-shots")
	get_viewport().get_texture().get_image().save_png("res://ending20-shots/at-%.2f.png"%at)
func _print_result() -> void:
	super._print_result()
	if not armed:return
	var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
	var started: bool=reference.start(seed_,primary);assert(started)
	while reference.tick<run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==run.snapshot()
	var checks: Dictionary=_edge20() if age>2.5 else {}
	_save20("result",{"same_complete_core_as_normal_reference":same,"tick":run.tick,"mode":run.mode,"samples":samples,"checks":checks,"scope":"Normal-policy earned build resimulated to23830 then3s fixed60 GPU ending; separate synthetic modal/queue/reset checks after screenshots, no manual/full-run/performance claim."})
	assert(same)
func _edge20() -> Dictionary:
	var checks: Dictionary={}
	var snapshot: Dictionary=run.snapshot().duplicate(true)
	var original_mode: String=run.mode
	var boss: Node3D
	for actor in actors.actors.values():
		if actor.has_meta("enemy_rig"):boss=actor
	var boss_age: float=boss.get_meta("warden_death_age")
	var actor_age: float=actors._victory20_age
	var fx_age: float=effects._ending20_age
	for modal in ["paused","inventory","choice","equipment"]:
		run.mode=modal;actors.sync(run,.25);effects.sync(run,.25)
		checks[modal+"_ending_clock_held"]=boss.get_meta("warden_death_age")==boss_age and actors._victory20_age==actor_age and effects._ending20_age==fx_age
	var combat_hidden := true
	for name_ in effects.ENDING20_NODES:combat_hidden=combat_hidden and not effects.get(name_).visible
	checks.combat_fx_hidden=combat_hidden
	checks.all_other_actors_faded=true
	for actor in actors.actors.values():
		if actor.has_meta("enemy_rig"):continue
		if actor.has_meta("sprite"):checks.all_other_actors_faded=checks.all_other_actors_faded and actor.get_meta("sprite").modulate.a<.001
		elif actor.has_meta("minion19"):
			for mat in actor.get_meta("minion19").materials:checks.all_other_actors_faded=checks.all_other_actors_faded and mat.albedo_color.a<.001
	checks.ground_loot_retained=effects.item_nodes.size()==run.items.size()
	hud.reset();run.mode="playing";hud.sync(run,0)
	checks.starting_inventory_seeded_silently=hud.discovery20_history.is_empty() and hud._discovery20_queue.is_empty()
	hud.reset()
	var unique: Dictionary={}
	for item in run.inventory:
		hud._queue_discovery20(item)
		if item.quality=="unique":unique=item
	checks.queue_bounded=hud._discovery20_queue.size()<=4
	var queued: int=hud._discovery20_queue.size()
	for item in run.inventory:hud._queue_discovery20(item)
	checks.queue_deduped=queued==hud._discovery20_queue.size()
	checks.unique_prioritized=not unique.is_empty() and hud._discovery20_queue[0].uid==unique.uid
	hud._present_discovery20(unique)
	var left: float=hud._discovery_left;var gap: float=hud._discovery20_gap
	for modal in ["paused","inventory","equipment"]:
		run.mode=modal;hud.sync(run,.25)
		checks[modal+"_discovery_held"]=hud._discovery_left==left and hud._discovery20_gap==gap and not hud._discovery.visible
	run.mode=original_mode
	actors.reset();effects.reset();hud.reset()
	checks.reset_clears_ending=not actors._victory20_active and actors._victory20_age==0 and not effects._ending20_active and effects._ending20_age==0
	checks.reset_clears_discovery=hud._discovery20_queue.is_empty() and hud.discovery20_history.is_empty() and not hud._discovery20_seeded
	checks.all_core_restored=snapshot==run.snapshot()
	for value in checks.values():assert(value)
	return checks
