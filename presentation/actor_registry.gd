extends RefCounted
## Stable id:generation keys prevent recycled simulation slots inheriting poses.
## Node ownership/freeing: https://docs.godotengine.org/en/4.5/classes/class_node.html
var actors: Dictionary = {}
var states: Dictionary = {}
var pool: Array[Node3D] = []
var primary: Node3D
var primary_used := false
var paused := false
var loader: Callable
var animator: Callable
var tinter: Callable
const POOL_CAPACITY := 512
const MAX_CORPSE_ACTORS := 64
var culled_corpses := 0
var created_count := 0
var reused_count := 0
var released_count := 0
var animation_lod_enabled := true
var pose_elapsed: Dictionary = {}
var pose_updates := 0
var pose_updates_near := 0
var pose_updates_far := 0
var animation_ms := 0.0
const NEAR_ANIMATION_BUDGET := 64
var near_members: Dictionary = {}
var near_refresh := 0.0
var animation_clock_progress := 0
var animation_playing := 0
var animation_time := 0.0
var pose_buckets: Dictionary = {}

func setup(first: Node3D, load_callback: Callable, animation_callback: Callable, tint_callback: Callable) -> void:
	primary = first
	created_count = 1
	primary.hide()
	loader = load_callback
	animator = animation_callback
	tinter = tint_callback

func key(state: Dictionary) -> String:
	return "%d:%d" % [int(state.id),int(state.generation)]

func ensure(state: Dictionary) -> Node3D:
	var identity: String = key(state)
	if actors.has(identity): return actors[identity]
	var node: Node3D
	if not primary_used:
		node = primary
		primary_used = true
	elif not pool.is_empty():
		node = pool.pop_back()
		reused_count += 1
	else:
		node = loader.call("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
		created_count += 1
		node.scale = Vector3.ONE*1.12
		tinter.call(node,Color(.74,.86,.68))
	actors[identity] = node
	states[identity] = ""
	# Rebinding a pool slot starts from rest, never the previous generation's pose.
	# https://docs.godotengine.org/en/4.5/classes/class_skeleton3d.html#class-skeleton3d-method-reset-bone-poses
	node.rotation = Vector3.ZERO
	reset_skeletons(node)
	node.show()
	var ap: AnimationPlayer = node.get_meta("player")
	# Manual animation uses accumulated elapsed time, never a gameplay timer.
	# https://docs.godotengine.org/en/4.5/classes/class_animationmixer.html
	ap.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	pose_elapsed[identity] = 0.0
	ap.speed_scale = 0.0 if paused else 1.0
	return node

func reset_skeletons(node: Node) -> void:
	if node is Skeleton3D: node.reset_bone_poses()
	for child in node.get_children(): reset_skeletons(child)

func sync(sim: RefCounted) -> void:
	var wanted: Dictionary = {}
	var corpse_count := 0
	culled_corpses = 0
	for state in sim.enemies.values():
		if state.state == "dead":
			if corpse_count >= MAX_CORPSE_ACTORS:
				culled_corpses += 1
				continue
			corpse_count += 1
		wanted[key(state)] = true
	# Release stale generations before allocating replacements, so an all-entity
	# reset/rebind can immediately reuse retired nodes without doubling the pool.
	for identity in actors.keys():
		if not wanted.has(identity): release(identity)
	for state in sim.enemies.values():
		var identity: String = key(state)
		if not wanted.has(identity): continue
		wanted[identity] = true
		var node: Node3D = ensure(state)
		var desired_position := Vector3(state.p.x,0,state.p.y)
		if node.position != desired_position: node.position = desired_position
		var toward: Vector2 = sim.player-Vector2(state.p)
		if state.state != "dead" and toward.length_squared() > .01:
			var desired_yaw: float = atan2(toward.x,toward.y)
			if node.rotation.y != desired_yaw: node.rotation.y = desired_yaw
		if states[identity] != state.state:
			pose_elapsed[identity] = 0.0
			var first_pose: bool = states[identity] == ""
			var blend: float = 0.0 if first_pose else .06
			match String(state.state):
				"approach": animator.call(node,"Walking_A" if sim.enemy_ai else "Idle",.75,first_pose,blend)
				"windup": animator.call(node,"Unarmed_Melee_Attack_Punch_A",1.5,first_pose,blend)
				"recover": animator.call(node,"Idle",1.0,first_pose,blend)
				"hurt": animator.call(node,"Hit_A",1.8,first_pose,blend)
				"dead": animator.call(node,"Death_A",1.0,first_pose,blend)
			states[identity] = state.state
	for identity in actors.keys():
		if not wanted.has(identity): release(identity)

func release(identity: String) -> void:
	var node: Node3D = actors[identity]
	node.hide()
	var ap: AnimationPlayer = node.get_meta("player")
	ap.stop()
	ap.speed_scale = 1
	released_count += 1
	if node == primary: primary_used = false
	elif pool.size() < POOL_CAPACITY: pool.append(node)
	else: node.queue_free()
	actors.erase(identity)
	states.erase(identity)
	pose_elapsed.erase(identity)
	pose_buckets.erase(identity)
	near_members.erase(identity)

func advance(delta: float, camera: Camera3D, player_position: Vector2) -> void:
	pose_updates = 0
	pose_updates_near = 0
	pose_updates_far = 0
	animation_ms = 0.0
	animation_clock_progress = 0
	animation_playing = 0
	if paused: return
	animation_time += delta
	var began: int = Time.get_ticks_usec()
	near_refresh -= delta
	if near_refresh <= 0.0:
		near_refresh = .2
		var ranked: Array = []
		for identity in actors:
			var node: Node3D = actors[identity]
			var distance_sq: float = Vector2(node.position.x,node.position.z).distance_squared_to(player_position)
			if distance_sq <= 25.0: ranked.append([distance_sq,identity])
		ranked.sort_custom(func(a,b): return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1]))
		near_members.clear()
		for index in range(mini(NEAR_ANIMATION_BUDGET,ranked.size())): near_members[ranked[index][1]] = true
	for identity in actors:
		var node: Node3D = actors[identity]
		var visible_: bool = camera.is_position_in_frustum(node.global_position+Vector3.UP)
		var near_: bool = near_members.has(identity)
		var interval: float = 1.0/60.0 if near_ else 1.0/15.0
		if not visible_: interval = .5
		if not animation_lod_enabled: interval = 0.0
		pose_elapsed[identity] = float(pose_elapsed.get(identity,0.0))+delta
		var ap: AnimationPlayer = node.get_meta("player")
		if ap.is_playing(): animation_playing += 1
		# Fixed absolute ID phases stay spread after clip changes; resetting a
		# newly hurt actor's elapsed time must not synchronize the far cohort.
		var phase: float = float(int(identity.get_slice(":",0))%8)/8.0
		var bucket: int = floori(animation_time/interval+phase) if interval > 0 else 0
		var due: bool = interval == 0 or int(pose_buckets.get(identity,bucket-1)) != bucket
		if due:
			var before: float = ap.current_animation_position
			ap.advance(pose_elapsed[identity])
			if ap.current_animation_position != before: animation_clock_progress += 1
			pose_elapsed[identity] = 0.0
			pose_buckets[identity] = bucket
			pose_updates += 1
			if near_: pose_updates_near += 1
			else: pose_updates_far += 1
	animation_ms = float(Time.get_ticks_usec()-began)/1000.0

func set_paused(value: bool) -> void:
	paused = value
	for node in actors.values():
		var ap: AnimationPlayer = node.get_meta("player")
		ap.speed_scale = 0.0 if value else 1.0

func reset() -> void:
	for identity in actors.keys(): release(identity)
	paused = false
	primary_used = false
	near_members.clear()
	near_refresh = 0.0
	animation_time = 0.0
	pose_buckets.clear()
	var ap: AnimationPlayer = primary.get_meta("player")
	ap.stop()
	ap.speed_scale = 1

func actor_for(state: Dictionary) -> Node3D:
	return actors.get(key(state)) if not state.is_empty() else null

