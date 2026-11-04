extends SceneTree
var checks: Dictionary={}
func _initialize() -> void:call_deferred("_test")
func _poses(actor: Node3D) -> Array:
	var result: Array=[];var rig: Skeleton3D=actor.get_meta("minion19").skeleton
	for i in rig.get_bone_count():result.append(rig.get_bone_pose(i))
	return result
func _test() -> void:
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view);view.set_process(false);view.set_physics_process(false)
	while view.run.tick<2800:view.run.step(view.full_pilot.decide())
	view.run.events.clear();view.actors.sync(view.run,0)
	var frozen: Dictionary=view.run.snapshot().duplicate(true)
	var examples: Dictionary={}
	for actor in view.actors.actors.values():
		if actor.has_meta("variant30_index"):
			var entity: Dictionary=view.actors._entity(actor)
			if int(entity.hp_raw)>0 and entity.state=="move" and int(entity.frozen_until)<view.run.tick:examples[str(actor.get_meta("kind"))+":"+str(actor.get_meta("variant30_index"))]=actor
	checks["twelve_role_variants_in_normal_crowd"]=examples.size()==12
	var stable := true;var modal := true;var staff := true;var hit := false
	for actor in examples.values():
		var state: Dictionary=actor.get_meta("minion19");var e: Dictionary=view.actors._entity(actor)
		view.actors._update_pose(actor,Vector2.DOWN,true,false,false,view.run.tick,true)
		var initial := _poses(actor)
		for i in 24:view.actors._update_pose(actor,Vector2.DOWN,true,false,false,view.run.tick,true)
		stable=stable and initial==_poses(actor)
		view.actors._update_pose(actor,Vector2.LEFT,false,false,false,view.run.tick,false)
		modal=modal and initial==_poses(actor)
		if state.has("staff21"):staff=staff and state.staff21.position.distance_to(actor.to_local(view.actors._bone_point(state.skeleton,"Hand.R")))<.00001
		view.actors._enemy_hit_until[e.id]=view.run.tick+6
		view.actors._update_pose(actor,Vector2.DOWN,true,false,false,view.run.tick,true,true)
		hit=hit or actor.has_meta("hit28_base")
	checks["repeated_sampling_has_no_scale_accumulation"]=stable
	checks["frozen_modal_holds_complete_pose"]=modal
	checks["staff_matches_hand_after_deformation"]=staff
	checks["existing_hit28_layer_still_applies"]=hit
	checks["complete_core_unchanged"]=view.run.snapshot()==frozen
	var node_ids: Dictionary={}
	for actor in view.actors.actors.values():node_ids[actor.get_instance_id()]=true
	view.actors.reset();checks["pool_restored_224"]=view.actors._pool25_size()==224
	view.actors.sync(view.run,0)
	var ownership := true;var no_leaked_old_layer := true;var aliases: Dictionary={}
	for key in view.actors.actors:
		var actor: Node3D=view.actors.actors[key]
		ownership=ownership and actor.get_meta("entity_key","")==key
		if aliases.has(actor.get_instance_id()):ownership=false
		aliases[actor.get_instance_id()]=true
		if actor.has_meta("shape30_base"):
			for entry in actor.get_meta("shape30_base"):no_leaked_old_layer=no_leaked_old_layer and entry.scale.is_equal_approx(Vector3.ONE)
	checks["recheckout_ownership_no_alias"]=ownership
	checks["recheckout_restores_base_bone_scale"]=no_leaked_old_layer
	checks["no_extra_skin_or_ordinary_nodes"]=view.actors.pool25_created==224 and view.actors.skin24_builds==1
	checks["core_unchanged_after_pool_cycle"]=view.run.snapshot()==frozen
	var ok := true
	for value in checks.values():ok=ok and bool(value)
	var f := FileAccess.open("res://crowd30-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"passed":ok,"scope":"Normal2800tick state, all role variants, repeated pose/freeze/staff/hit-layer and pool reset/recheckout. Source headless regression only; not visual motion/performance/manual approval."},"\t"));f.close()
	view.audio.reset()
	for i in 4:await process_frame
	quit(0 if ok else 1)
