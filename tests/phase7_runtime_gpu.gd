extends SceneTree
## External candidate-only runtime evidence. Pilot is automated input, never OS
## input. Stress has explicit synthetic HP/mana and is not normal gameplay.
const Run=preload("res://run/expedition_controller.gd")
class IsolatedSim:
	extends "res://baseline_sim.gd"
	var isolated_path := ""
	func save_progress(_path: String="") -> bool: return super.save_progress(isolated_path)
	func load_progress(_path: String="") -> bool: return super.load_progress(isolated_path)
var output := ""
var expected := ""
var mode := "features"
var dimensions := Vector2i(1920,1080)
var duration := 310.0
var warmup := 0.0
var view: Node
var rows: Array=[]
var failures: Array[String]=[]
var checks := 0
var captures: Array=[]
var guards := {}
var started := 0
var previous := 0
var prior_tick := -1
var run_results: Array=[]
var run_index := 0
var collected_events: Array=[]
var recorder: AudioEffectRecord
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--qa-output="): output=arg.trim_prefix("--qa-output=")
		elif arg.begins_with("--expected-metadata="): expected=arg.trim_prefix("--expected-metadata=")
		elif arg.begins_with("--qa-mode="): mode=arg.trim_prefix("--qa-mode=")
		elif arg.begins_with("--qa-seconds="): duration=float(arg.trim_prefix("--qa-seconds="))
		elif arg.begins_with("--qa-warmup="): warmup=float(arg.trim_prefix("--qa-warmup="))
		elif arg.begins_with("--qa-width="): dimensions.x=int(arg.trim_prefix("--qa-width="))
		elif arg.begins_with("--qa-height="): dimensions.y=int(arg.trim_prefix("--qa-height="))
	call_deferred("run")
func signature(path: String) -> String:
	return FileAccess.get_sha256(path) if FileAccess.file_exists(path) else "absent"
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:
		failures.append(message)
		printerr("PHASE7 RUNTIME FAILED: "+message)
func settled() -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
func capture(name_: String) -> void:
	await settled()
	var image_: Image=root.get_texture().get_image()
	var path:=output.path_join(name_+".png")
	check(image_.save_png(path)==OK and image_.get_size()==dimensions,"actual framebuffer "+name_)
	captures.append({"path":path,"size":[image_.get_width(),image_.get_height()],"sha256":signature(path)})
func run() -> void:
	if output.is_empty() or not output.replace("\\","/").contains("/evidence/phase7/") or DirAccess.dir_exists_absolute(output):
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	for path in ["user://equipment-v1.json","user://progress-v1.json"]: guards[path]=signature(path)
	check(DisplayServer.get_name()!="headless","actual GPU backend")
	check(FileAccess.get_sha256("res://game_data/build_info.json")==expected,"candidate metadata pin")
	DisplayServer.window_set_size(dimensions)
	root.size=dimensions
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps=0
	view=load("res://Expedition.tscn").instantiate()
	var isolated=IsolatedSim.new()
	isolated.isolated_path="res://evidence/phase7/runtime/"+str(OS.get_process_id())+"/progress.json"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(isolated.isolated_path.get_base_dir()))
	view.sim=isolated
	view.controller=Run.new(isolated)
	root.add_child(view)
	await settled()
	if mode=="features":
		await features()
	else:
		await timed_runtime()
	for path in guards: check(signature(path)==guards[path],"native file preserved "+path)
	var report={"mode":mode,"success":failures.is_empty(),"checks":checks,"failures":failures,"framebuffer":[dimensions.x,dimensions.y],"captures":captures,"candidate_metadata_sha256":expected,"external_script_sha256":signature(get_script().resource_path),"executable":OS.get_executable_path(),"renderer":RenderingServer.get_current_rendering_method(),"hardware":RenderingServer.get_video_adapter_name(),"native_guards":guards,"run_results":run_results,"isolated_profile":isolated.isolated_path,"scope":"Candidate rendered scene. Automated pilot is not OS input. Stress explicitly uses synthetic high HP/mana and 300 enemies; ordinary runs retain normal combat and resource rules."}
	if not rows.is_empty(): report["timing"]=save_rows()
	var file:=FileAccess.open(output.path_join("summary.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	file.close()
	print(JSON.stringify(report))
	if physics_frame.is_connected(tick): physics_frame.disconnect(tick)
	view.audio.reset()
	await settled()
	view.free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
func features() -> void:
	view.set_process(false)
	view.set_physics_process(false)
	check(view.controller.state=="ready" and view.hud.overlay.visible,"rendered ready menu")
	check(view.hud.overlay_body.text.contains("00:00"),"fresh-run load message visible")
	await capture("ready")
	view.hud.start_button.pressed.emit()
	check(view.controller.state=="active" and view.sim.alive_count()==1,"start intent enters ordinary run")
	for index in range(3):
		view.hud.skill_buttons[index].pressed.emit()
		check(view.sim.selected_skill_id==view.sim.available_skill_ids()[index],"rendered skill selection "+str(index))
		var state: Dictionary=view.sim.nearest_enemy(view.sim.player)
		for t in range(160):
			view.controller.step(t==0,Vector2(state.p) if not state.is_empty() else Vector2(4,0))
			view.effects.consume(view.sim.events,view.sim)
			view.audio.consume(view.sim.events,view.sim.progress_events)
			view.effects.sync(view.sim,1.0/60.0)
		view.sync_actors()
		view.sync_equipment_hud()
		await capture("skill-"+str(index))
	view.restart()
	view.toggle_equipment()
	var before_tick: int=view.controller.elapsed_ticks
	for i in range(30): view._physics_process(1.0/60.0)
	check(view.controller.elapsed_ticks==before_tick and view.controller.paused,"modal freezes run and resources")
	view.sim.life=17
	view.sim.mana_raw=1234
	view.equipment_presenter.perform("equip",2)
	check(view.sim.life==17 and view.sim.life_max_raw==12800 and view.sim.mana_raw==1234,"robe never heals current quantities")
	check(view.audio.played>0,"equipment UI cue is connected")
	view.equipment_presenter.perform("save",null)
	view.equipment_presenter.perform("unequip","body")
	view.equipment_presenter.perform("load",null)
	check(view.sim.life==17 and view.sim.mana_raw==1234 and view.controller.elapsed_ticks==0,"profile load retains current quantities and starts fresh clock")
	check(view.equipment_presenter.notice_label.text.contains("00:00"),"load success explains fresh run")
	await capture("profile-loaded")
	view.toggle_equipment()
	view.toggle_pause()
	view.toggle_equipment()
	view.toggle_equipment()
	check(view.controller.paused,"closing modal restores earlier pause")
	view.toggle_pause()
	view.focus_lost()
	check(view.controller.paused and not view.input_controller.auto_cast,"focus loss freezes and clears input")
	view.restart()
	check(view.sim.life==50 and view.sim.mana_raw==view.sim.mana_max_raw,"R explicitly recovers current quantities")
	view.hud.volume_slider.value=.2
	check(is_equal_approx(view.audio.master_volume,.2),"volume slider reaches audio")
	view.toggle_mute()
	check(view.audio.muted,"mute intent reaches audio")
	view.toggle_mute()
	check(view.audio.voices.size()==16,"audio voice cap")
	# Synthetic bounded-ground fixture. Death flags/claims are explicit fixture
	# setup, not normal-combat or probability evidence. Timed pilot uses none.
	for state in view.sim.enemies.values().duplicate(): view.sim.despawn_enemy(view.sim.handle(state))
	for index in range(220):
		if view.sim.ground_loot_snapshot().size()==32: break
		var state: Dictionary=view.sim.entity(view.sim.spawn_enemy(view.sim.player+Vector2(5+index%6,4+int(index/6)%3)))
		state.state="dead"
		state.life_raw=0
		view.sim.claim_death_reward(view.sim.handle(state))
		view.sim.despawn_enemy(view.sim.handle(state))
	view.sync_actors()
	check(view.sim.ground_loot_snapshot().size()==32 and view.loot.markers.size()==32,"synthetic GPU ground and marker cap32")
	await capture("ground32-synthetic")
	for t in range(1801): view.sim.step()
	view.sync_actors()
	await settled()
	check(view.sim.ground_loot_snapshot().is_empty() and view.loot.markers.is_empty() and view.loot.labels.is_empty(),"synthetic1800tick TTL retires all ground markers and labels")
	view.restart()
	# Explicit synthetic elite lifetime and failure outcome, separate from pilot.
	var enemy: Dictionary=view.sim.enemies.values()[0]
	var actor: Node3D=view.actor_registry.actors[view.actor_registry.key(enemy)]
	var old_scale: Vector3=actor.scale
	view.controller.elite_identity=view.sim.handle(enemy)
	view.sync_actors()
	await capture("elite-synthetic")
	view.restart()
	check(actor.scale==old_scale,"elite scale restored on pool reuse")
	view.sim.life=0
	view.controller.step()
	view.sync_equipment_hud()
	check(view.controller.state=="defeat" and view.hud.retry_button.visible,"death exposes retry outcome")
	await capture("defeat-synthetic")
	view.hud.retry_button.pressed.emit()
	check(view.controller.state=="active" and view.controller.elapsed_ticks==0,"retry intent creates a new run")
	view.controller.elapsed_ticks=18000-1
	view.controller.elite_spawned=true
	view.controller.elite_defeated=false
	view.controller.step()
	view.sync_equipment_hud()
	check(view.controller.state=="timeout" and view.hud.retry_button.visible,"synthetic deadline exposes timeout outcome")
	await capture("timeout-synthetic")
	view.start_menu()
	check(view.controller.state=="ready" and view.hud.start_button.visible,"return to ready menu")
	await capture("menu-returned")
func start_pilot() -> void:
	view.start_run()
	# Ordinary initial inventory actions; no generated stats or current healing.
	view.sim.equip_item(1)
	view.sim.equip_item(2)
	view.input_controller.auto_cast=true
	prior_tick=-1
func timed_runtime() -> void:
	if mode=="stress":
		view.start_run()
		var profile: Dictionary=view.sim.progress_document()
		profile.xp=6
		check(view.controller.replace_profile_document(profile),"explicit level2 stress equipment fixture")
		for uid in [1,2,3]: check(view.sim.equip_item(uid),"stress fixture equip "+str(uid))
		view.sim.reset(300)
		view.sim.life=1000000.0
		for state in view.sim.enemies.values(): state.life_raw=1000000000
		view.set_physics_process(false)
		view.hud.notice.text="합성 300적 · 고생명/마나 · 일반 원정과 별도"
	else:
		start_pilot()
	if mode=="pilot":
		recorder=AudioEffectRecord.new()
		AudioServer.add_bus_effect(0,recorder)
		recorder.set_recording_active(true)
	physics_frame.connect(tick)
	started=Time.get_ticks_usec()
	previous=started
	var next_capture := 15.0
	while float(Time.get_ticks_usec()-started)/1000000.0 < duration+warmup:
		await process_frame
		var now:=Time.get_ticks_usec()
		var elapsed:=float(now-started)/1000000.0
		if elapsed>=warmup and (mode!="soak" or rows.is_empty() or int(elapsed)>int(rows[-1][0])):
			rows.append([elapsed,float(now-previous)/1000.0,view.controller.elapsed_ticks,view.sim.tick,view.sim.life,view.sim.mana_raw,view.sim.kills,view.sim.alive_count(),view.actor_registry.actors.size(),view.actor_registry.created_count,get_node_count(),view.effects.active.size(),view.effects.projectiles.size(),view.loot.markers.size(),view.audio.played,view.controller.state])
		if recorder!=null and elapsed>=75.0: finish_recording()
		previous=now
		if elapsed>=next_capture:
			await capture("frame-"+str(int(next_capture)))
			next_capture+=60.0
		if mode=="pilot" and view.controller.state in ["victory","defeat","timeout"]:
			run_results.append(view.controller.snapshot())
			await capture("outcome-"+view.controller.state)
			break
		if mode=="soak" and view.controller.state in ["victory","defeat","timeout"]:
			run_results.append(view.controller.snapshot())
			run_index+=1
			start_pilot()
	if recorder!=null: finish_recording()
	await capture("final")
	if mode=="pilot": check(not run_results.is_empty(),"normal-condition pilot reached a terminal outcome")
	if mode=="stress": check(view.sim.alive_count()==300,"300 enemies retained during stress")
	check(view.effects.created<=160 and view.effects.projectile_created<=128 and view.loot.markers.size()<=32 and view.audio.voices.size()==16,"bounded effects/projectiles/loot/audio")
func finish_recording() -> void:
	recorder.set_recording_active(false)
	var recording: AudioStreamWAV=recorder.get_recording()
	if recording!=null: check(recording.save_to_wav(output.path_join("mixed-audio.wav"))==OK,"first75s mixed audio saved (not listening approval)")
	AudioServer.remove_bus_effect(0,AudioServer.get_bus_effect_count(0)-1)
	recorder=null
func tick() -> void:
	if mode=="stress":
		view.sim.mana_raw=100000000
		view.sim.life=1000000.0
		var ids: Array=view.sim.available_skill_ids()
		view.sim.select_skill(ids[int(view.sim.tick/120)%3])
		var target: Dictionary=view.sim.nearest_enemy(view.sim.player)
		view.sim.step(not target.is_empty(),Vector2(target.p) if not target.is_empty() else Vector2.ZERO)
		view.effects.consume(view.sim.events,view.sim)
		view.audio.consume(view.sim.events,view.sim.progress_events)
		view.sync_actors()
		return
	if view.controller.state!="active" or view.sim.paused: return
	var t: int=view.controller.elapsed_ticks
	if t==prior_tick: return
	prior_tick=t
	var target: Dictionary=view.sim.nearest_enemy(view.sim.player)
	# Ordinary movement input policy: orbit inside arena; evade nearest enemies.
	var destination:=Vector2(cos(float(t)/380.0),sin(float(t)/380.0))*6.0
	if not target.is_empty() and view.sim.player.distance_to(target.p)<2.5:
		var away: Vector2=(view.sim.player-Vector2(target.p)).normalized()
		destination=view.sim.player+away*3.0
	view.sim.set_destination(destination.clamp(Vector2(-12,-9),Vector2(12,9)))
	if t%120==0:
		var nearby: int=0
		for state in view.sim.enemies.values():
			if state.state!="dead" and view.sim.player.distance_to(state.p)<6: nearby+=1
		view.select_skill_index(2 if nearby>=3 else 0)
	if int(view.sim.progression_snapshot().level)>=2 and t%120==0: view.sim.equip_item(3)
	view.input_controller.auto_cast=true
func save_rows() -> Dictionary:
	var file:=FileAccess.open(output.path_join("frames.csv"),FileAccess.WRITE)
	file.store_line("elapsed_seconds,frame_ms,run_tick,sim_tick,life,mana_raw,kills,alive,actors,created_actors,nodes,transients,projectiles,loot,audio_played,state")
	var values: Array[float]=[]
	for row in rows:
		file.store_line(",".join(row.map(func(value):return str(value))))
		values.append(float(row[1]))
	file.close()
	values.sort()
	return {"count":rows.size(),"sample_seconds":float(rows[-1][0])-float(rows[0][0]),"p50":values[clampi(ceili(values.size()*.50)-1,0,values.size()-1)],"p95":values[clampi(ceili(values.size()*.95)-1,0,values.size()-1)],"p99":values[clampi(ceili(values.size()*.99)-1,0,values.size()-1)],"worst":values[-1],"frames_over_50ms":values.filter(func(value):return value>50).size(),"wall_seconds":float(Time.get_ticks_usec()-started)/1000000.0,"scope":"Soak uses one selected preceding frame per second, not the full frame distribution; bounded observer array of about600 rows." if mode=="soak" else "All sampled wall-clock rendered frames. Synthetic stress is separate from normal controller runs."}
