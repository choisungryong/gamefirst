extends "res://chapter1/chapter_one_view.gd"
const SharedActor24=preload("res://chapter1/view/chapter_actors_quality24.gd")
var checks: Dictionary={}
func _init() -> void:
	super._init();actors=SharedActor24.new()
func _ready() -> void:
	super._ready();set_process(false);set_physics_process(false)
	var baseline: Dictionary=run.snapshot().duplicate(true)
	_mesh24_checks()
	var originals: Dictionary=run.enemies
	var source: Dictionary=originals.values()[0].duplicate(true)
	var seq := 100000
	for role in ["ranged","charger"]:
		var e: Dictionary=source.duplicate(true);e.kind=role;e.elite=false;e.position=run.hero.position+Vector2(2,-2);e.state="move";e.frozen_until=0;e.direction=Vector2.RIGHT;e.attack_direction=Vector2.RIGHT;e.attack_kind="fan" if role=="ranged" else "line"
		run.enemies={e.id:e};actors.reset();actors.sync(run,.016)
		var actor: Node3D=actors.actors.values()[0];var state: Dictionary=actor.get_meta("minion19")
		checks[role+"_rig"]=actor.get_meta("role21")==role
		var definition: Dictionary=run._enemy_definition(e)
		e.state="windup";e.state_until=run.tick+int(definition.windup);actors.sync(run,.016)
		checks[role+"_windup"]=actor.get_meta("minion19_pose").clip==("windup_fan" if role=="ranged" else "windup_slam")
		e.state="recover" if role=="ranged" else "dash";e.state_until=run.tick+(int(definition.recover) if role=="ranged" else 32)
		actors.consume([{"seq":seq,"type":"enemy_attack","target_id":e.id,"tick":run.tick,"position":e.position,"attack_kind":e.attack_kind,"kind":role}]);seq+=1;actors.sync(run,.1)
		checks[role+"_paid_pose"]=actor.get_meta("minion19_pose").clip==("fan" if role=="ranged" else "walk")
		var pose: Dictionary=actor.get_meta("minion19_pose").duplicate(true);var lean: float=state.model.rotation.x
		var hand: Vector3=state.staff21.global_position if role=="ranged" else Vector3.ZERO
		e.frozen_until=run.tick+60;actors.sync(run,.25)
		checks[role+"_freeze"]=pose==actor.get_meta("minion19_pose") and lean==state.model.rotation.x
		if role=="ranged":checks.staff_frozen_position=hand.is_equal_approx(state.staff21.global_position)
		e.frozen_until=0
		for modal in ["paused","choice","inventory","equipment"]:
			run.mode=modal;actors.sync(run,.25)
			checks[role+"_"+modal]=pose==actor.get_meta("minion19_pose") and lean==state.model.rotation.x
		run.mode="playing"
		if role=="charger":
			e.state="recover";e.state_until=run.tick+int(definition.recover);actors.sync(run,.1)
			checks.charger_no_second_attack=actor.get_meta("minion19_pose").clip=="idle"
		e.hp_raw=0;e.dead_tick=run.tick
		actors.consume([{"seq":seq,"type":"death","target_id":e.id,"tick":run.tick,"position":e.position,"skill_id":"chapter1.skill.frost","kind":role,"elite":false}]);seq+=1;actors.sync(run,.25)
		var hidden := true
		for mat in state.materials:hidden=hidden and mat.albedo_color.a<.001
		checks[role+"_cold_all_materials_hidden"]=hidden
		actors.reset();checks[role+"_reset"]=actors.actors.is_empty() and actors._cold_corpses.is_empty() and actors._demon19_attacks.is_empty()
	run.enemies=originals;checks.complete_core_restored=baseline==run.snapshot()
	var f := FileAccess.open("res://skin24-fixture.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"scope":"Shared mesh equality/material/skeleton independence and copied-role entities for actual presenter invariants; complete original core restored, not normal/manual/performance."},"\t"));f.close()
	var failed := false
	for value in checks.values():if not value:failed=true
	audio.reset()
	for i in 4:await get_tree().process_frame
	get_tree().quit(1 if failed else 0)

func _mesh24_checks() -> void:
	var old=ChapterActors.new();old.view=self
	for kind in ["walker","ranged","charger","elite"]:
		var a: Node3D=old._create(kind);var b: Node3D=actors._create(kind);var c: Node3D=actors._create(kind)
		for actor in [a,b,c]:add_child(actor)
		var sa: Dictionary=a.get_meta("minion19");var sb: Dictionary=b.get_meta("minion19");var sc: Dictionary=c.get_meta("minion19")
		var ma: MeshInstance3D=sa.model.find_child("ChainedDemon",true,false)
		var mb: MeshInstance3D=sb.model.find_child("ChainedDemon",true,false)
		var mc: MeshInstance3D=sc.model.find_child("ChainedDemon",true,false)
		checks[kind+"_geometry_equal"]=ma.mesh.surface_get_arrays(0)==mb.mesh.surface_get_arrays(0)
		checks[kind+"_mesh_shared"]=mb.mesh==mc.mesh
		checks[kind+"_material_equal"]=sa.materials[0].albedo_color==sb.materials[0].albedo_color and sa.materials[0].albedo_texture.resource_path==sb.materials[0].albedo_texture.resource_path and sa.materials[0].rim==sb.materials[0].rim
		checks[kind+"_independent_material"]=sb.materials[0]!=sc.materials[0]
		checks[kind+"_independent_rig"]=sb.skeleton!=sc.skeleton and sb.player!=sc.player
		for actor in [a,b,c]:actor.queue_free()
	checks.two_immutable_skins=actors._shared_skin24.size()==2 and actors.skin24_builds==2
	checks.no_transient_mesh_aliases=actors._batch19_cache.is_empty()
