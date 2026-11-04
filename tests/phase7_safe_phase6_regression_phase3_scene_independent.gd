extends SceneTree
## Actual imported meshes/rigs and pooled nodes. Headless correctness only.
const Sim = preload("res://baseline_sim.gd")
const Effects = preload("res://presentation/effect_presenter.gd")
const MeshBatch = preload("res://presentation/skinned_mesh_batch.gd")
var checks := 0
var failures: Array[String] = []
var view: Node3D
var max_normal_roundtrip_delta := 0.0
var max_normal_roundtrip_angle_degrees := 0.0
var max_tangent_roundtrip_delta := 0.0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("PHASE3 SCENE FAILED: "+message)

func skeleton(node: Node) -> Skeleton3D:
	if node is Skeleton3D: return node
	for child in node.get_children():
		var found: Skeleton3D = skeleton(child)
		if found: return found
	return null

func skeleton_pose(actor: Node3D) -> Array:
	var bones: Skeleton3D = skeleton(actor)
	var pose: Array = []
	for bone in range(bones.get_bone_count()): pose.append(bones.get_bone_pose(bone))
	return pose

func mesh_children(actor: Node3D) -> Array:
	var result: Array = []
	for child in skeleton(actor).get_children():
		if child is MeshInstance3D: result.append(child)
	return result

func raw_mesh_groups(actor: Node3D) -> Dictionary:
	var groups: Dictionary = {}
	for node in mesh_children(actor):
		for surface in range(node.mesh.get_surface_count()):
			var material_: Material = node.get_active_material(surface)
			var key_: int = material_.get_instance_id()
			if not groups.has(key_): groups[key_] = {"material":material_,"arrays":[]}
			groups[key_].arrays.append(node.mesh.surface_get_arrays(surface))
	return groups

# Independent oracle copied from the exact engine version's storage contract:
# https://github.com/godotengine/godot/blob/4.5.1-stable/servers/rendering_server.cpp#L557
# https://github.com/godotengine/godot/blob/4.5.1-stable/core/math/vector3.cpp#L97
# Even uncompressed normal/tangent arrays are encoded as two uint16 values.
func encode_oct16(value: Vector2) -> Vector2:
	# C++ multiplies in float32 before truncating to uint16.
	var products := PackedFloat32Array([value.x*65535.0,value.y*65535.0])
	return Vector2(clampi(int(products[0]),0,65535),clampi(int(products[1]),0,65535))

func stored_normal(value: Vector3) -> Vector3:
	var encoded: Vector2 = encode_oct16(value.octahedron_encode())
	return Vector3.octahedron_decode(encoded/65535.0)

func stored_tangent(values: Variant, index: int) -> Vector4:
	var direction := Vector3(values[index],values[index+1],values[index+2])
	var encoded: Vector2 = direction.octahedron_encode()
	encoded.y = maxf(encoded.y,1.0/32767.0)
	encoded.y = encoded.y*.5+.5
	encoded.y = encoded.y if values[index+3] >= 0 else 1.0-encoded.y
	encoded = encode_oct16(encoded)
	if encoded.x == 0 and encoded.y == 65535: encoded.x = 65535
	encoded /= 65535.0
	encoded.y = encoded.y*2.0-1.0
	var sign_: float = 1.0 if encoded.y >= 0 else -1.0
	encoded.y = absf(encoded.y)
	var decoded: Vector3 = Vector3.octahedron_decode(encoded)
	return Vector4(decoded.x,decoded.y,decoded.z,sign_)

func mesh_merge_invariants() -> void:
	var raw: Node3D = view.load_model("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
	var merged: Node3D = view.load_model("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
	var source_groups: Dictionary = raw_mesh_groups(raw)
	var raw_nodes: Array = mesh_children(raw)
	var original_skin: Skin = raw_nodes[0].skin
	var batch = MeshBatch.new()
	var result: Dictionary = batch.merge(merged)
	check(result.get("merged",false) and result.source_meshes == 9 and result.surfaces == 2,"actual nine-piece skeleton merges into two material surfaces")
	var merged_nodes: Array = mesh_children(merged)
	check(merged_nodes.size() == 1 and skeleton(merged).get_bone_count() == 41,"merged actor retains a complete 41-bone skeleton and one mesh node")
	var node: MeshInstance3D = merged_nodes[0]
	check(node.skin == original_skin and node.skin.get_bind_count() == 41 and node.skeleton == NodePath(".."),"merged mesh retains original Skin/bindings and Skeleton path")
	check(node.transform == Transform3D.IDENTITY,"merged mesh keeps the original identity transform")
	var all_arrays_match := true
	var all_materials_match := true
	var shading_roundtrips_match := true
	var tangent_handedness_preserved := true
	var total_vertices := 0
	var total_indices := 0
	for surface in range(node.mesh.get_surface_count()):
		var material_: Material = node.get_active_material(surface)
		var key_: int = material_.get_instance_id()
		all_materials_match = all_materials_match and source_groups.has(key_)
		if not source_groups.has(key_): continue
		var actual: Array = node.mesh.surface_get_arrays(surface)
		var offsets: Dictionary = {}
		var vertex_offset := 0
		for source in source_groups[key_].arrays:
			for slot in range(Mesh.ARRAY_MAX):
				if source[slot] == null: continue
				var offset: int = offsets.get(slot,0)
				if slot == Mesh.ARRAY_INDEX:
					for index in range(source[slot].size()):
						all_arrays_match = all_arrays_match and actual[slot][offset+index] == source[slot][index]+vertex_offset
				elif slot == Mesh.ARRAY_NORMAL:
					for index in range(source[slot].size()):
						var before: Vector3 = source[slot][index]
						var after: Vector3 = actual[slot][offset+index]
						shading_roundtrips_match = shading_roundtrips_match and after == stored_normal(before)
						max_normal_roundtrip_delta = maxf(max_normal_roundtrip_delta,before.distance_to(after))
						max_normal_roundtrip_angle_degrees = maxf(max_normal_roundtrip_angle_degrees,rad_to_deg(before.angle_to(after)))
				elif slot == Mesh.ARRAY_TANGENT:
					for index in range(0,source[slot].size(),4):
						var expected: Vector4 = stored_tangent(source[slot],index)
						tangent_handedness_preserved = tangent_handedness_preserved and actual[slot][offset+index+3] == source[slot][index+3]
						for component in range(4):
							shading_roundtrips_match = shading_roundtrips_match and actual[slot][offset+index+component] == expected[component]
							max_tangent_roundtrip_delta = maxf(max_tangent_roundtrip_delta,absf(actual[slot][offset+index+component]-source[slot][index+component]))
				else: all_arrays_match = all_arrays_match and actual[slot].slice(offset,offset+source[slot].size()) == source[slot]
				offsets[slot] = offset+source[slot].size()
			vertex_offset += source[Mesh.ARRAY_VERTEX].size()
			total_vertices += source[Mesh.ARRAY_VERTEX].size()
			total_indices += source[Mesh.ARRAY_INDEX].size()
		for slot in offsets: all_arrays_match = all_arrays_match and actual[slot].size() == offsets[slot]
	check(all_arrays_match,"every source vertex/UV/bone/weight and offset index survives material grouping exactly")
	check(shading_roundtrips_match,"every normal/tangent matches the exact Godot4.5.1 uint16 octahedral storage roundtrip")
	check(tangent_handedness_preserved,"every original tangent handedness sign is retained")
	check(all_materials_match and total_vertices == 4858 and total_indices == 15864,"body/eye materials and known imported geometry totals are preserved")
	var pose_changes := true
	for clip in ["Idle","Walking_A","Unarmed_Melee_Attack_Punch_A","Hit_A","Death_A"]:
		view.animate(raw,clip,1.0,true,0.0)
		view.animate(merged,clip,1.0,true,0.0)
		var start_pose: Array = skeleton_pose(raw)
		var raw_player: AnimationPlayer = raw.get_meta("player")
		var merged_player: AnimationPlayer = merged.get_meta("player")
		raw_player.advance(.17)
		merged_player.advance(.17)
		check(skeleton_pose(raw) == skeleton_pose(merged),"all real bone poses match unmerged actor for "+clip)
		pose_changes = pose_changes and skeleton_pose(raw) != start_pose
	check(pose_changes,"all five animation fixtures actually change real bone poses")
	var another: Node3D = view.load_model("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
	var another_result: Dictionary = batch.merge(another)
	check(another_result.get("merged",false) and mesh_children(another)[0].mesh == node.mesh,"compatible actors share the same immutable merged mesh")
	var untouched: Node3D = view.load_model("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
	check(mesh_children(untouched).size() == 9,"merging instances does not modify the original imported PackedScene")
	untouched.free()
	another.free()
	merged.free()
	raw.free()

func fixture_bolts(count: int, first_id: int = 1) -> Array:
	var bolts: Array = []
	for index in range(count): bolts.append({"p":Vector2(float(index%20)*.1,float(index/20)*.1),"direction":Vector2.RIGHT,"age":index%30,"life":132,"id":first_id+index})
	return bolts

func hidden_unique(nodes: Array) -> bool:
	var ids: Dictionary = {}
	for node in nodes:
		if not is_instance_valid(node) or node.visible or node.is_queued_for_deletion(): return false
		ids[node.get_instance_id()] = true
	return ids.size() == nodes.size()

func effects_pool_invariants() -> void:
	view.set_enemy_count(0)
	var effects: RefCounted = view.effect_presenter
	view.sim.bolts = fixture_bolts(Effects.MAX_PROJECTILES+88)
	var before: String = JSON.stringify({"bolts":view.sim.bolts,"rng":str(view.sim.rng.state),"mana":view.sim.mana_raw,"tick":view.sim.tick})
	effects.sync(view.sim,view.camera,view.atlas)
	check(effects.projectile_nodes.size() == Effects.MAX_PROJECTILES and effects.projectile_created == Effects.MAX_PROJECTILES,"projectile visuals have a hard active/allocation cap")
	check(effects.dropped_projectiles == 88 and view.sim.bolts.size() == Effects.MAX_PROJECTILES+88,"visual overflow is counted without removing authoritative bolts")
	var previous_nodes: Array = effects.projectile_nodes.values()
	effects.reset()
	check(effects.projectile_nodes.is_empty() and effects.projectile_pool.size() == Effects.MAX_PROJECTILES and hidden_unique(effects.projectile_pool),"reset unbinds and retains a unique hidden projectile pool")
	var reset_frames := true
	for node in previous_nodes: reset_frames = reset_frames and node.frame_coords == Vector2i.ZERO
	check(reset_frames,"projectile retirement clears previous atlas frame")
	var created: int = effects.projectile_created
	view.sim.bolts = fixture_bolts(Effects.MAX_PROJECTILES,2001)
	effects.sync(view.sim,view.camera,view.atlas)
	var visible_accurate := true
	for index in range(view.sim.bolts.size()):
		var bolt: Dictionary = view.sim.bolts[index]
		var node: Sprite3D = effects.projectile_nodes[bolt.id]
		visible_accurate = visible_accurate and node.visible and node.scale == Vector3.ONE and node.texture == view.atlas and node.position == Vector3(bolt.p.x,.9,bolt.p.y)
	check(effects.projectile_created == created and effects.projectile_reused == Effects.MAX_PROJECTILES and visible_accurate,"all projectile slots reuse with new identity/position/texture/scale")
	check(not effects.projectile_nodes.has(1),"old projectile identities do not resolve after pool reuse")
	effects.reset()
	for cycle in range(3):
		view.sim.bolts = fixture_bolts(100,10001+cycle*1000)
		effects.sync(view.sim,view.camera,view.atlas)
		effects.reset()
	check(effects.projectile_created == created and effects.projectile_pool.size() == Effects.MAX_PROJECTILES,"repeated projectile cycles retain a bounded pool without creating nodes")

	effects.burst(Vector3(1,2,3),Color.ORANGE,Effects.MAX_PARTICLES+99,.3)
	check(effects.particles.size() == Effects.MAX_PARTICLES and effects.particle_created == Effects.MAX_PARTICLES and effects.dropped_particles == 99,"particle overflow honors the active/allocation cap and reports drops")
	var old_particle: MeshInstance3D = effects.particles[0].node
	var old_position: Vector3 = old_particle.position
	effects.advance(.1)
	check(effects.particles[0].life < .3 and old_particle.position != old_position,"pooled particle fixture actually advances before expiry")
	effects.advance(.3)
	check(effects.particles.is_empty() and effects.particle_pool.size() == Effects.MAX_PARTICLES and hidden_unique(effects.particle_pool),"expired particles enter one hidden bounded pool")
	created = effects.particle_created
	var at := Vector3(-2,1,-3)
	effects.burst(at,Color.CYAN,Effects.MAX_PARTICLES,.5)
	var clean := true
	for particle in effects.particles:
		clean = clean and particle.node.visible and particle.node.position == at and particle.node.scale == Vector3.ONE and particle.life == .5 and particle.max == .5 and particle.node.material_override.albedo_color == Color.CYAN
	check(effects.particle_created == created and effects.particle_reused == Effects.MAX_PARTICLES and clean,"reused particles clear old position/scale/color/lifetime")
	effects.reset()
	for duration in [0.0,-1.0,INF,NAN]: effects.burst(Vector3.ZERO,Color.ORANGE,10,duration)
	effects.burst(Vector3.ZERO,Color.ORANGE,0,.3)
	check(effects.particles.is_empty() and effects.particle_created == created,"invalid/empty bursts cannot allocate or activate effects")
	for cycle in range(4):
		effects.burst(Vector3.ZERO,Color.ORANGE,64,.3)
		effects.reset()
	check(effects.particle_created == created and effects.particle_pool.size() == Effects.MAX_PARTICLES and hidden_unique(effects.particle_pool),"repeated burst/reset cycles retain a bounded unique particle pool")
	# Restore exactly the original authoritative fixture before comparing the
	# complete fields and RNG; FX operations above never called the sim step.
	view.sim.bolts = fixture_bolts(Effects.MAX_PROJECTILES+88)
	check(before == JSON.stringify({"bolts":view.sim.bolts,"rng":str(view.sim.rng.state),"mana":view.sim.mana_raw,"tick":view.sim.tick}),"presentation pooling never changes combat/RNG/mana/time")
	view.sim.bolts.clear()
	effects.reset()

func animation_lod_invariants() -> void:
	view.set_enemy_count(2)
	view.sim.enemy_ai = false
	var states: Array = view.sim.enemies.values()
	states[0].p = view.sim.player+Vector2(1,0)
	states[1].p = view.sim.player+Vector2(6,0)
	view.sync_actors()
	var registry: RefCounted = view.actor_registry
	registry.animation_lod_enabled = true
	var near: Node3D = registry.actor_for(states[0])
	var far: Node3D = registry.actor_for(states[1])
	var near_player: AnimationPlayer = near.get_meta("player")
	var far_player: AnimationPlayer = far.get_meta("player")
	check(near_player.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL and far_player.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL,"registry owns explicit manual animation advancement")
	registry.advance(.01,view.camera,view.sim.player)
	registry.advance(.01,view.camera,view.sim.player)
	check(near_player.current_animation_position > far_player.current_animation_position and far_player.current_animation_position >= 0,"near pose clock updates more frequently after the first binding frame")
	registry.advance(.05,view.camera,view.sim.player)
	check(is_equal_approx(near_player.current_animation_position,far_player.current_animation_position) and registry.pose_updates == 2,"far pose catches up using accumulated elapsed time")
	states[1].p = Vector2(100,100)
	view.sync_actors()
	registry.advance(.05,view.camera,view.sim.player)
	registry.advance(.01,view.camera,view.sim.player)
	check(registry.pose_elapsed[registry.key(states[1])] > 0,"offscreen fixture really accumulates deferred pose time")
	states[1].state = "hurt"
	view.sync_actors()
	check(is_zero_approx(registry.pose_elapsed[registry.key(states[1])]),"state change discards elapsed time belonging to the previous clip")
	registry.animation_lod_enabled = false
	registry.advance(.01,view.camera,view.sim.player)
	check(far_player.current_animation_position <= .02,"new hurt clip advances only the post-transition duration")
	check(registry.pose_updates == 2,"disabling pose LOD advances every registered rig including offscreen")
	var positions := [near_player.current_animation_position,far_player.current_animation_position]
	registry.set_paused(true)
	registry.advance(.3,view.camera,view.sim.player)
	check(positions == [near_player.current_animation_position,far_player.current_animation_position] and registry.pose_updates == 0,"paused manual animation keeps all poses and update counts frozen")
	registry.set_paused(false)
	view.set_enemy_count(0)
	check(registry.pose_elapsed.is_empty(),"reset/release removes every old generation pose accumulator")

func animation_budget_invariants() -> void:
	view.set_enemy_count(100)
	view.sim.enemy_ai = false
	var registry: RefCounted = view.actor_registry
	registry.animation_lod_enabled = true
	var states: Array = view.sim.enemies.values()
	for index in range(states.size()): states[index].p = view.sim.player+Vector2(1.0+index*.001,0)
	view.sync_actors()
	var updates: Dictionary = {}
	var previous: Dictionary = {}
	for state in states:
		var identity: String = registry.key(state)
		updates[identity] = 0
		previous[identity] = 0.0
	var max_near := 0
	var max_far := 0
	var maximum_frame_work := 0
	var near_set: Dictionary = {}
	for frame in range(120):
		registry.advance(1.0/120.0,view.camera,view.sim.player)
		# Initial bindings all establish their first visible pose once. The
		# steady-state scheduler must stagger subsequent updates.
		if frame > 0:
			max_near = maxi(max_near,registry.pose_updates_near)
			max_far = maxi(max_far,registry.pose_updates_far)
			maximum_frame_work = maxi(maximum_frame_work,registry.pose_updates)
		near_set = registry.near_members.duplicate()
		for identity in registry.actors:
			var player: AnimationPlayer = registry.actors[identity].get_meta("player")
			if player.current_animation_position != previous[identity]: updates[identity] += 1
			previous[identity] = player.current_animation_position
	check(near_set.size() == registry.NEAR_ANIMATION_BUDGET and max_near <= registry.NEAR_ANIMATION_BUDGET,"crowded near cohort respects the 64-rig high-rate animation budget")
	var nearest_members := true
	for index in range(states.size()): nearest_members = nearest_members and (near_set.has(registry.key(states[index])) == (index < registry.NEAR_ANIMATION_BUDGET))
	check(nearest_members,"64 high-rate members are the nearest actual actors")
	var near_progress := true
	var far_progress := true
	for identity in updates:
		if near_set.has(identity): near_progress = near_progress and updates[identity] >= 59 and updates[identity] <= 61
		else: far_progress = far_progress and updates[identity] >= 14 and updates[identity] <= 16
	check(near_progress,"every budgeted near actor actually progresses at approximately 60Hz")
	check(far_progress,"every remaining visible actor progresses at approximately 15Hz without starvation")
	check(max_far < states.size()-registry.NEAR_ANIMATION_BUDGET and maximum_frame_work < states.size(),"far update phases spread work across frames instead of one synchronized full crowd")
	# Flush the remaining positive elapsed durations without adding wall time.
	# This catches schedulers which discard an initial phase by negative time.
	registry.animation_lod_enabled = false
	registry.advance(0.0,view.camera,view.sim.player)
	var conserved := true
	for node in registry.actors.values():
		var player: AnimationPlayer = node.get_meta("player")
		conserved = conserved and absf(player.current_animation_position-.75) <= .00002
	check(conserved,"all actor clocks conserve one real second after flushing deferred pose time")
	view.set_enemy_count(0)
	check(registry.near_members.is_empty() and is_zero_approx(registry.near_refresh),"reset clears cached near membership and forces immediate reranking")

func corpse_budget_invariants() -> void:
	view.set_enemy_count(100)
	view.sim.enemy_ai = false
	check(view.actor_registry.actors.size() == 100,"corpse budget never caps a fully alive crowd")
	var states: Array = view.sim.enemies.values()
	for index in range(80):
		states[index].state = "dead"
		states[index].life_raw = 0
		states[index].corpse_until = view.sim.tick+2
	view.sync_actors()
	check(view.sim.enemies.size() == 100 and view.sim.alive_count() == 20,"corpse display culling leaves every authoritative entity unchanged")
	check(view.actor_registry.actors.size() == 20+view.actor_registry.MAX_CORPSE_ACTORS and view.actor_registry.culled_corpses == 16,"mixed live/corpse scene retains all live actors plus exactly64 corpses")
	var all_alive_bound := true
	for index in range(80,100): all_alive_bound = all_alive_bound and view.actor_registry.actor_for(states[index]) != null
	check(all_alive_bound,"no living entity is hidden to satisfy the corpse budget")
	check(view.crowd_label.text.contains("생존 20") and view.crowd_label.text.contains("논리 개체 100") and view.crowd_label.text.contains("배우 84"),"HUD separates live20/logical100/actually bound84 actors")
	view.report_dir = "res://evidence/phase7/verification/legacy-mixed-corpse-report"
	var before: Array = [view.sim.tick,view.sim.enemies.duplicate(true),str(view.sim.rng.state)]
	var wrote: bool = view.write_report()
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(view.report_dir+"/scene-run.json"))
	check(wrote and report.alive == 20 and report.entities == 100 and report.actor_count == 84 and report.logical_corpses == 80 and report.rendered_corpses == 64 and report.culled_corpses == 16,"QA report separately counts logical/rendered/culled corpses")
	check(before == [view.sim.tick,view.sim.enemies,str(view.sim.rng.state)],"expanded corpse QA output does not change simulation or RNG")
	view.sim.step()
	view.sim.step()
	view.sync_actors()
	check(view.sim.enemies.size() == 20 and view.actor_registry.actors.size() == 20 and view.actor_registry.culled_corpses == 0,"TTL still reclaims authoritative shown and culled corpses exactly")
	view.set_enemy_count(0)

func run() -> void:
	view = load("res://Baseline.tscn").instantiate()
	view.sim.reset(0)
	view.initial_enemies = 0
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	mesh_merge_invariants()
	effects_pool_invariants()
	animation_lod_invariants()
	animation_budget_invariants()
	corpse_budget_invariants()
	view.free()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional phase3 scene failure proof")
	print(JSON.stringify({"scope":"phase3 real-mesh/rig/pool headless correctness; not GPU performance or final art quality","checks":checks,"failures":failures,"success":failures.is_empty(),"max_normal_roundtrip_delta":max_normal_roundtrip_delta,"max_normal_roundtrip_angle_degrees":max_normal_roundtrip_angle_degrees,"max_tangent_component_roundtrip_delta":max_tangent_roundtrip_delta}))
	quit(0 if failures.is_empty() else 1)
