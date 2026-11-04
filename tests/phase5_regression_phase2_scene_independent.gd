extends SceneTree
## Actual Baseline scene + real imported proxy rigs; headless functional checks only.
const Sim = preload("res://baseline_sim.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("PHASE2 SCENE FAILED: "+message)

func clip(node: Node3D) -> String:
	var ap: AnimationPlayer = node.get_meta("player")
	return String(ap.current_animation).get_file()

func pointer(pressed: bool) -> InputEventMouseButton:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_RIGHT
	event.pressed = pressed
	return event

func bones(node: Node) -> Skeleton3D:
	if node is Skeleton3D: return node
	for child in node.get_children():
		var found: Skeleton3D = bones(child)
		if found: return found
	return null

func skeleton_pose(node: Node3D) -> Array:
	var skeleton: Skeleton3D = bones(node)
	var result: Array = []
	if skeleton:
		for index in range(skeleton.get_bone_count()): result.append(skeleton.get_bone_pose(index))
	return result

func run() -> void:
	var scene: PackedScene = load("res://Baseline.tscn")
	var view = scene.instantiate()
	view.sim.reset(0)
	view.initial_enemies = 0
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	check(view.actor_registry.actors.is_empty(),"initial zero has no registered actors")
	check(not view.actor_registry.primary.visible,"initial zero hides the unused primary proxy")
	check(not view.enemy_label.visible and not view.enemy_bar.visible,"initial zero hides target HUD")

	for count in [2,10,100]:
		view.sim.enemy_ai = false
		view.set_enemy_count(count)
		view.sim.enemy_ai = false
		view.sync_actors()
		check(view.sim.enemies.size() == count and view.actor_registry.actors.size() == count,"real scene registers requested count "+str(count))
		var node_ids: Dictionary = {}
		var accurate := true
		var animation_ok := true
		for state in view.sim.enemies.values():
			var node: Node3D = view.actor_registry.actor_for(state)
			node_ids[node.get_instance_id()] = true
			accurate = accurate and node.visible and node.position == Vector3(state.p.x,0,state.p.y)
			animation_ok = animation_ok and clip(node) == "Idle" and view.actor_registry.states[view.actor_registry.key(state)] == state.state
		check(node_ids.size() == count and accurate,"unique actual nodes track entity positions/visibility "+str(count))
		check(animation_ok,"registered states choose real proxy animations "+str(count))
		view.held = true
		view.queued_cast = true
		view.toggle_pause()
		var all_paused := true
		for node in view.actor_registry.actors.values():
			var ap: AnimationPlayer = node.get_meta("player")
			all_paused = all_paused and ap.speed_scale == 0
		check(all_paused and not view.held and not view.queued_cast,"pause freezes every actor and clears queued pointer "+str(count))
		view.toggle_pause()
		var all_resumed := true
		for node in view.actor_registry.actors.values():
			var ap: AnimationPlayer = node.get_meta("player")
			all_resumed = all_resumed and ap.speed_scale == 1
		check(all_resumed,"resume restores every actor "+str(count))

	# Same-clip reuse must start again, even if AnimationPlayer.stop kept its name.
	view.set_enemy_count(2)
	view.sim.enemy_ai = false
	view.sync_actors()
	var states: Array = view.sim.enemies.values()
	var victim: Dictionary = states[1]
	var old_handle: Dictionary = view.sim.handle(victim)
	var old_node: Node3D = view.actor_registry.actor_for(victim)
	var old_ap: AnimationPlayer = old_node.get_meta("player")
	old_ap.advance(.45)
	view.sim.despawn_enemy(old_handle)
	view.sync_actors()
	check(not old_node.visible and not old_ap.is_playing(),"despawn hides actual actor and stops its animation")
	check(view.actor_registry.actor_for(victim) == null,"despawn removes stale generation lookup")
	var replacement: Dictionary = view.sim.spawn_enemy(Vector2(4,4))
	view.sync_actors()
	var replacement_state: Dictionary = view.sim.entity(replacement)
	var replacement_node: Node3D = view.actor_registry.actor_for(replacement_state)
	var replacement_ap: AnimationPlayer = replacement_node.get_meta("player")
	check(replacement.id == old_handle.id and replacement.generation > old_handle.generation,"scene exercises same ID with newer generation")
	check(replacement_node == old_node and replacement_node.visible,"pool reuses actual retired node")
	check(replacement_ap.is_playing() and clip(replacement_node) == "Idle" and is_zero_approx(replacement_ap.current_animation_position),"same-clip reuse restarts playback at zero")
	check(view.actor_registry.actor_for(victim) == null,"old dictionary cannot retrieve replacement actor")

	# A dead pose cannot leak through reused primary/pooled rigs.
	replacement_state.state = "dead"
	replacement_state.life_raw = 0
	replacement_state.corpse_until = view.sim.tick+2
	view.sync_actors()
	check(clip(replacement_node) == "Death_A","actual death clip is selected for the reused skeleton")
	replacement_ap.advance(.3)
	var death_pose: Array = skeleton_pose(replacement_node)
	check(not death_pose.is_empty(),"actual death clip is applied to a real skeleton")
	view.sim.step()
	view.sync_actors()
	check(view.actor_registry.actor_for(replacement_state) == replacement_node,"corpse actor persists before exact TTL")
	view.sim.step()
	view.sync_actors()
	check(view.actor_registry.actor_for(replacement_state) == null and not replacement_node.visible,"TTL removes and hides corpse actor")
	var next_handle: Dictionary = view.sim.spawn_enemy(Vector2(-3,-3))
	view.sync_actors()
	var next_node: Node3D = view.actor_registry.actor_for(view.sim.entity(next_handle))
	check(next_node == replacement_node and clip(next_node) == "Idle","dead rig is reused in live idle state")
	var clean_scene: Node3D = view.load_model("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
	view.animate(clean_scene,"Idle",.75,true)
	check(skeleton_pose(next_node) == skeleton_pose(clean_scene),"reused rig pose equals freshly initialized idle pose")
	check(death_pose != skeleton_pose(clean_scene),"death pose fixture differs from clean idle pose")
	clean_scene.free()
	# Acquiring at the player must not retain an old heading when toward==zero.
	next_node.rotation = Vector3(.2,2.3,.4)
	view.sim.despawn_enemy(next_handle)
	view.sync_actors()
	var coincident: Dictionary = view.sim.spawn_enemy(view.sim.player)
	view.sync_actors()
	var coincident_node: Node3D = view.actor_registry.actor_for(view.sim.entity(coincident))
	check(coincident_node == next_node and coincident_node.rotation.is_zero_approx(),"pooled actor at player resets stale rotation even without a facing vector")
	var stale_handles: Array = view.sim.enemies.values().map(func(state): return view.sim.handle(state))
	var old_primary: Node3D = view.actor_registry.primary
	view.restart()
	var stale_hidden := true
	for identity in stale_handles: stale_hidden = stale_hidden and view.actor_registry.actor_for(identity) == null
	check(stale_hidden and view.actor_registry.primary == old_primary,"reset invalidates all actor generations and retains primary ownership")

	# Kill all actual simulation entities with overlapping real bolts, then expire all.
	view.set_enemy_count(10)
	view.sim.enemy_ai = false
	view.sim.corpse_ticks = 2
	var projectiles: Array = []
	var shot := 1
	for state in view.sim.enemies.values():
		state.life_raw = 1
		projectiles.append({"p":state.p,"direction":Vector2.RIGHT,"age":0,"life":132,"id":shot})
		shot += 1
	view.sim.bolts = projectiles
	view.sim.step_bolts()
	view.sync_actors()
	check(view.sim.alive_count() == 0 and view.sim.kills == 10 and view.actor_registry.actors.size() == 10,"all-killed scene retains exactly ten corpse actors")
	check(not view.enemy_bar.visible and not view.enemy_label.visible,"all-killed hides target HUD")
	var all_death := true
	for node in view.actor_registry.actors.values(): all_death = all_death and clip(node) == "Death_A"
	check(all_death,"every killed entity receives its death animation")
	view.sim.step()
	view.sim.step()
	view.sync_actors()
	check(view.actor_registry.actors.is_empty() and view.actor_registry.states.is_empty(),"all corpse TTLs clear registry states and actor bindings")
	var all_hidden: bool = not view.actor_registry.primary.visible
	for node in view.actor_registry.pool: all_hidden = all_hidden and not node.visible
	check(all_hidden,"all released primary/pool nodes are hidden")

	# Exercise view handlers directly; no OS input injection.
	view.set_enemy_count(2)
	view._unhandled_input(pointer(true))
	view._input(pointer(false))
	check(not view.held and view.queued_cast,"global release clears hold while preserving one quick click")
	view._physics_process(Sim.STEP)
	check(not view.queued_cast and not view.sim.pending.is_empty(),"quick press-release becomes one actual pending cast")
	view.held = true
	view.queued_cast = true
	view.get_window().focus_exited.emit()
	check(not view.held and not view.queued_cast,"connected focus-exited signal clears both input flags")
	var desired_ground := Vector3(2,0,2)
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = view.camera.unproject_position(desired_ground)
	var projected: Variant = view.input_controller.destination_request(click,view.camera)
	check(projected is Vector3 and projected.distance_to(desired_ground) < .001,"extracted input projection resolves the real scene camera ground point")
	check(view.input_controller.world_movement(Vector2.ZERO,view.camera) == Vector2.ZERO and is_equal_approx(view.input_controller.world_movement(Vector2(1,1),view.camera).length(),1),"extracted camera-relative movement preserves zero and normalizes diagonals")
	view.toggle_pause()
	var paused_destination: Vector2 = view.sim.move_target
	view._unhandled_input(click)
	check(view.sim.move_target == paused_destination,"paused left click cannot change simulation destination")
	view.toggle_pause()

	view.sim.bolts = [{"p":Vector2.ZERO,"direction":Vector2.RIGHT,"age":1,"life":132,"id":999}]
	view.sync_actors()
	view.burst(Vector3.ZERO,Color.ORANGE,4,.3)
	check(view.projectile_nodes.size() == 1 and view.particles.size() == 4,"actual scene owns projectile sprite and burst nodes")
	var particle_life: float = view.particles[0].life
	var particle_position: Vector3 = view.particles[0].node.position
	var paused_tick: int = view.sim.tick
	view.toggle_pause()
	view._physics_process(.2)
	view._process(.2)
	check(view.sim.tick == paused_tick and view.particles[0].life == particle_life and view.particles[0].node.position == particle_position,"paused view freezes particle lifetime/position and simulation")
	var transient_nodes: Array = view.projectile_nodes.values()
	for particle in view.particles: transient_nodes.append(particle.node)
	view.restart()
	check(view.projectile_nodes.is_empty() and view.particles.is_empty() and view.sim.pending.is_empty() and view.sim.history.is_empty(),"restart clears visuals, pending work and events")
	var all_retired := true
	for node in transient_nodes: all_retired = all_retired and not node.visible and not node.is_queued_for_deletion()
	check(all_retired,"restart retires every transient visual into a hidden reusable pool")
	await process_frame
	var all_retained := true
	for node in transient_nodes: all_retained = all_retained and is_instance_valid(node) and not node.visible
	check(all_retained,"deferred frame retains hidden pool nodes without reviving effects")
	view.set_enemy_count(0)
	check(view.actor_registry.actors.is_empty() and not view.actor_registry.primary.visible and view.sim.enemies.is_empty(),"zero reset leaves no bound or visible primary actor")
	# Continued phase3 regression output has its own location; accepted phase2
	# runtime evidence remains under evidence/phase2.
	view.report_dir = "res://evidence/phase5/verification/legacy-scene-regression-report"
	var before_report: Array = [view.sim.tick,view.sim.history.duplicate(true),view.sim.enemies.duplicate(true),view.sim.mana_raw]
	check(view.write_report(),"extracted QA boundary writes a real scene report")
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(view.report_dir+"/scene-run.json"))
	check(report.actor_count == 0 and report.entities == 0 and report.requested_enemies == 0 and not report.capture_saved,"QA report preserves actual empty population and uncaptured status")
	check(before_report == [view.sim.tick,view.sim.history,view.sim.enemies,view.sim.mana_raw],"QA report does not mutate combat state")
	view.free()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional scene harness failure proof")
	print(JSON.stringify({"scope":"phase2 real-scene headless functional validation; not GPU performance or D2R equivalence","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
