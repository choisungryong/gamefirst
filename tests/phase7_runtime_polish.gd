extends SceneTree
## Independent integration checks for expedition-only modal acknowledgement.
const Run = preload("res://run/expedition_controller.gd")
class IsolatedSim:
	extends "res://baseline_sim.gd"
	var test_path := ""
	func save_progress(_path: String = "user://progress-v1.json") -> bool: return super.save_progress(test_path)
	func load_progress(_path: String = "user://progress-v1.json") -> bool: return super.load_progress(test_path)
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool,message: String) -> void:
	checks += 1
	if not ok: failures.append(message)
func signature(path: String) -> String:
	return FileAccess.get_sha256(path) if FileAccess.file_exists(path) else "absent"
func materials(node: Node) -> Array:
	var result: Array=[]
	if node is MeshInstance3D:
		for surface in range(node.mesh.get_surface_count()): result.append(node.get_active_material(surface))
	for child in node.get_children(): result.append_array(materials(child))
	return result
func run() -> void:
	var folder := "res://evidence/phase7/runtime-polish/"+str(OS.get_process_id())+"-"+str(Time.get_ticks_usec())
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder))
	var guards := {}
	for path in ["user://equipment-v1.json","user://progress-v1.json"]: guards[path]=signature(path)
	var view = load("res://Expedition.tscn").instantiate()
	var isolated = IsolatedSim.new()
	isolated.test_path=folder+"/progress.json"
	view.sim=isolated
	view.controller=Run.new(isolated)
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	await process_frame
	check(view.hud.load_button.tooltip_text.contains("00:00"),"menu load declares fresh run")
	check(view.hud.overlay_body.text.contains("00:00"),"menu body declares fresh run")
	view.start_run()
	view.sim.life=17
	view.sim.mana_raw=1234
	view.toggle_equipment()
	check(view.equipment_presenter.load_button.tooltip_text.contains("00:00"),"modal load declares fresh run")
	var played: int=view.audio.played
	var damage_state: int=view.sim.rng.state
	view.equipment_presenter.perform("equip",2)
	check(view.audio.played==played+1,"successful equip sounds during paused modal")
	check(view.sim.life==17 and view.sim.mana_raw==1234 and view.sim.rng.state==damage_state,"UI cue neither heals nor draws combat RNG")
	check(view.audio.voices.size()==16 and view.audio.paused,"UI cue preserves bounded pool and gameplay pause")
	played=view.audio.played
	view.audio.play_ui("equip",view.sim.tick)
	check(view.audio.played==played,"same tick UI cue deduplicates")
	view.audio.set_muted(true)
	view.audio.play_ui("equip",view.sim.tick+10)
	check(view.audio.played==played,"UI cue respects mute")
	view.audio.set_muted(false)
	view.equipment_presenter.perform("save",null)
	check(FileAccess.file_exists(isolated.test_path),"isolated profile saved")
	view.sim.life=13
	view.sim.mana_raw=999
	view.equipment_presenter.perform("load",null)
	check(view.controller.elapsed_ticks==0 and view.controller.paused,"modal load restarts clock while retaining pause")
	check(view.sim.life==13 and view.sim.mana_raw==999,"load preserves current quantities")
	check(view.equipment_presenter.notice_label.text.contains("새 원정") and view.equipment_presenter.notice_label.text.contains("00:00"),"successful modal load explains new run")
	# Explicit synthetic elite identities isolate visual pool lifetime, never damage.
	var enemy: Dictionary=view.sim.enemies.values()[0]
	var identity: Dictionary=view.sim.handle(enemy)
	var actor: Node3D=view.actor_registry.actors[view.actor_registry.key(enemy)]
	var original_scale: Vector3=actor.scale
	var original_materials: Array=materials(actor)
	view.controller.elite_identity=identity
	view.sync_actors()
	check(actor.scale.is_equal_approx(Vector3.ONE*1.48),"elite fixture is visibly distinct")
	view.restart()
	var rebound: Node3D=view.actor_registry.actors[view.actor_registry.key(view.sim.enemies.values()[0])]
	check(actor==rebound and actor.scale==original_scale and materials(actor)==original_materials,"R generation rebind restores scale and exact original material references")
	enemy=view.sim.enemies.values()[0]
	identity=view.sim.handle(enemy)
	view.controller.elite_identity=identity
	view.sync_actors()
	view.sim.entity(identity).state="dead"
	view.world_presenter.sync_elite(identity,view.actor_registry)
	check(actor.scale==original_scale and materials(actor)==original_materials and not view.world_presenter.elite_root.visible,"dead elite immediately releases decoration and original actor appearance")
	view.restart()
	enemy=view.sim.enemies.values()[0]
	identity=view.sim.handle(enemy)
	view.controller.elite_identity=identity
	view.sync_actors()
	view.toggle_equipment()
	view.equipment_presenter.perform("load",null)
	check(actor.scale==original_scale and materials(actor)==original_materials,"profile load restores pooled elite appearance")
	check(view.world_presenter.elite_original_materials.is_empty() and view.world_presenter.elite_actor==null,"no retained elite material or actor references after load")
	for path in guards: check(signature(path)==guards[path],"native guard "+path)
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional runtime polish proof")
	view.audio.reset()
	await process_frame
	await process_frame
	view.free()
	view=null
	isolated=null
	await process_frame
	await process_frame
	print(JSON.stringify({"checks":checks,"failures":failures,"success":failures.is_empty(),"scope":"headless modal feedback and fresh-run wording, not audio listening or OS input"}))
	quit(0 if failures.is_empty() else 1)
