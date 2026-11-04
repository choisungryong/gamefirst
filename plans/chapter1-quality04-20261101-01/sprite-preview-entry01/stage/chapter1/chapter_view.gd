extends Node3D
## C2 scene glue. Fixed-tick core owns all gameplay; UI/actors/VFX only present it.
const CombatRun=preload("res://chapter1/core/combat_run.gd")
const World=preload("res://chapter1/view/cloister_world.gd")
const Actors=preload("res://chapter1/view/cloister_actors.gd")
const Effects=preload("res://chapter1/view/cloister_effects.gd")
const HUD=preload("res://chapter1/view/cloister_hud.gd")
const Audio=preload("res://chapter1/presentation/combat_audio.gd")
const FrameProbe=preload("res://chapter1/presentation/frame_probe.gd")
var run=CombatRun.new()
var world=World.new()
var actors=Actors.new()
var effects=Effects.new()
var hud=HUD.new()
var audio=Audio.new()
var _frame_probe=FrameProbe.new()
var _probe_quit_after_complete := false
var primary := "chapter1.skill.ember"
var seed_ := 90131
var _wall_age := 0.0
var _quit_after := -1.0
var _pilot := false
var _capture_dir := ""
var _captured: Dictionary={}
var _last_audio_event := -1
var _last_result := ""
var _frame_ms: Array[float]=[]
var _qa_quit_sent := false
var _qa_ignore_focus := false
var _has_move_target := false
var _move_target := Vector2.ZERO
var _qa_input_file: FileAccess
var _qa_run_sequence := 0
var _qa_state_sequence := 0
var _qa_last_capture_mode := ""
var _qa_pending_capture_mode := ""
var _audio_previous := Vector2.ZERO
var _audio_step_distance := 0.0

func _exit_tree() -> void:
	_frame_probe.finish("scene_exit")
	# RefCounted presenters must release their scene owner before shutdown.
	if _qa_input_file:_qa_input_file.close();_qa_input_file=null
	actors.view=null;effects.view=null;world.root=null
	for voice in audio.voices:
		if is_instance_valid(voice):voice.stop();voice.stream=null
	audio.voices.clear();audio.streams.clear();audio.ambience=null

func _ready() -> void:
	DisplayServer.window_set_title("잿빛 회랑 · Chapter 1")
	world.setup(self)
	actors.setup(self)
	effects.setup(self)
	hud.temporary_art=actors.temporary_art
	hud.setup(self)
	hud.start.connect(start_run)
	hud.choice.connect(choose)
	hud.equipment.connect(open_equipment)
	hud.close_equipment.connect(close_equipment)
	hud.equip_item.connect(equip_item)
	hud.pause_toggle.connect(toggle_pause)
	hud.retry.connect(retry)
	hud.mute_toggle.connect(toggle_mute)
	hud.motion_toggle.connect(func(enabled: bool):world.set_reduced_motion(not enabled))
	audio.setup(self)
	audio.set_master_volume(.80)
	audio.set_paused(true)
	get_window().focus_exited.connect(func():
		if not _qa_ignore_focus and run.mode not in ["menu","victory","defeat"]:run.set_paused(true))
	var autostart := false
	var input_log_path := ""
	var frame_probe_dir := ""
	var probe_arg_count := 0
	for arg in OS.get_cmdline_user_args():
		if arg=="--chapter1-start":autostart=true
		elif arg=="--chapter1-pilot":_pilot=true
		elif arg=="--chapter1-qa-ignore-focus":_qa_ignore_focus=true
		elif arg.begins_with("--chapter1-frame-probe-dir="):
			probe_arg_count+=1;frame_probe_dir=arg.trim_prefix("--chapter1-frame-probe-dir=")
		elif arg=="--chapter1-frame-probe-quit":_probe_quit_after_complete=true
		elif arg.begins_with("--chapter1-qa-input-log="):input_log_path=arg.trim_prefix("--chapter1-qa-input-log=")
		elif arg.begins_with("--chapter1-primary="):primary=arg.trim_prefix("--chapter1-primary=")
		elif arg.begins_with("--chapter1-quit-after="):_quit_after=float(arg.trim_prefix("--chapter1-quit-after="))
		elif arg.begins_with("--chapter1-capture-dir="):_capture_dir=arg.trim_prefix("--chapter1-capture-dir=")
		elif arg.begins_with("--chapter1-seed="):seed_=int(arg.trim_prefix("--chapter1-seed="))
	if not input_log_path.is_empty():
		var allowed := ProjectSettings.globalize_path("res://plans/chapter1-c2-20261031-01/").replace("\\","/")
		var quality_allowed := ProjectSettings.globalize_path("res://plans/chapter1-quality-20261031-01/").replace("\\","/")
		var path := input_log_path.replace("\\","/").simplify_path()
		if (path.begins_with(allowed) or path.begins_with(quality_allowed)) and not FileAccess.file_exists(path):
			DirAccess.make_dir_recursive_absolute(path.get_base_dir())
			_qa_input_file=FileAccess.open(path,FileAccess.WRITE)
		else:push_error("QA input log must be a new file inside the new C2 evidence directory")
	if probe_arg_count>1 or (probe_arg_count==1 and frame_probe_dir.is_empty()) or (_probe_quit_after_complete and probe_arg_count!=1):
		push_error("Frame probe requires exactly one nonempty output flag");get_tree().quit(1);return
	if not frame_probe_dir.is_empty():
		if not _frame_probe.configure(frame_probe_dir,self,{"pilot":_pilot,"qa_ignore_focus":_qa_ignore_focus,"captures_enabled":not _capture_dir.is_empty(),"input_log_enabled":not input_log_path.is_empty(),"wall_quit_enabled":_quit_after>0,"seed":seed_,"primary":primary}):
			get_tree().quit(1);return
	if autostart:start_run(primary)
	hud.sync(run,0)
	var actor_states: Dictionary={}
	for kind in actors.sprite_definitions:actor_states[kind]=Array(actors.sprite_definitions[kind].frames.get_animation_names())
	print("CHAPTER1_READY ",JSON.stringify({"scene":"chapter1/Chapter1.tscn","temporary_actor_art":actors.temporary_art,"actor_states":actor_states,"raw_texture_fallbacks":actors.raw_texture_fallbacks,"scope":"representative encounter, not completed chapter","pilot":_pilot,"qa_ignore_focus":_qa_ignore_focus}))

func start_run(id_: String) -> void:
	primary=id_
	if not run.start(seed_,primary):
		push_error(str(run.errors));get_tree().quit(1);return
	_qa_run_sequence+=1
	actors.reset();effects.reset();hud.reset();audio.reset()
	_last_audio_event=-1;_last_result="";_captured.clear();_frame_ms.clear()
	_has_move_target=false
	_audio_previous=run.hero.position;_audio_step_distance=0
	audio.set_paused(false)
	hud.notify("경험치와 장비를 회수하며 회랑 수호자를 준비하세요")

func retry() -> void:
	seed_+=1
	start_run(primary)

func choose(token: String, card_id: String) -> void:
	if run.choose(token,card_id):
		hud.invalidate();audio.play_ui("equip",run.tick)
	_consume_events()

func open_equipment() -> void:
	if run.open_inventory():hud.invalidate()

func close_equipment() -> void:
	run.close_inventory();hud.invalidate()

func equip_item(uid: int) -> void:
	if run.equip(uid):
		hud.notify("장비 효과를 적용했습니다");hud.invalidate();audio.play_ui("equip",run.tick)
	_consume_events()

func toggle_pause() -> void:
	if run.mode=="menu" or run.mode in ["victory","defeat"]:return
	run.set_paused(run.mode!="paused")
	hud.invalidate()

func toggle_mute() -> void:
	audio.set_muted(not audio.muted)
	hud.notify("소리 꺼짐" if audio.muted else "소리 켜짐")

func _input(event: InputEvent) -> void:
	_qa_log_key(event,"input")

func _qa_log_key(event: InputEvent, phase: String) -> void:
	if _qa_input_file==null or not event is InputEventKey:return
	_qa_input_file.store_string(JSON.stringify({"phase":phase,"mode":run.mode,"tick":run.tick,"keycode":event.keycode,"physical_keycode":event.physical_keycode,"pressed":event.pressed,"echo":event.echo})+"\n")
	_qa_input_file.flush()

func _unhandled_key_input(event: InputEvent) -> void:
	_qa_log_key(event,"unhandled_key_input")
	if not event is InputEventKey or not event.pressed or event.echo:return
	# Menu shortcuts use logical keys. Native QA proved injected input carries
	# correct keycode but a constant unrelated physical scan code; WASD stays physical.
	var shortcut: int=event.keycode if event.keycode!=0 else event.physical_keycode
	match shortcut:
		KEY_ESCAPE:
			if run.mode=="inventory":close_equipment()
			else:toggle_pause()
		KEY_I:
			if run.mode=="inventory":close_equipment()
			else:open_equipment()
		KEY_SPACE:
			_has_move_target=false
			run.request_dash(_move_input())
		KEY_M:toggle_mute()
		KEY_F1:hud.debug.visible=not hud.debug.visible
		KEY_R:
			if run.mode in ["victory","defeat"]:retry()

func _unhandled_input(event: InputEvent) -> void:
	if run.mode!="playing" or not event is InputEventMouseButton:return
	if event.button_index!=MOUSE_BUTTON_LEFT or not event.pressed:return
	var origin: Vector3=world.camera.project_ray_origin(event.position)
	var direction: Vector3=world.camera.project_ray_normal(event.position)
	var ground: Variant=Plane(Vector3.UP,0).intersects_ray(origin,direction)
	if ground is Vector3:
		_move_target=Vector2(ground.x,ground.z).clamp(Vector2.ONE*-18.8,Vector2.ONE*18.8)
		_has_move_target=true
		effects.move_marker(_move_target)
		get_viewport().set_input_as_handled()

func _move_input() -> Vector2:
	var x := float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A))
	var y := float(Input.is_physical_key_pressed(KEY_W))-float(Input.is_physical_key_pressed(KEY_S))
	var right := Vector2(world.camera.global_basis.x.x,world.camera.global_basis.x.z).normalized()
	var forward := Vector2(-world.camera.global_basis.z.x,-world.camera.global_basis.z.z).normalized()
	if x!=0 or y!=0:_has_move_target=false
	elif _has_move_target and not run.hero.is_empty():
		var delta: Vector2=_move_target-run.hero.position
		if delta.length()>.12:return delta.normalized()
		_has_move_target=false
	return (right*x+forward*y).limit_length(1.0)

func _physics_process(_delta: float) -> void:
	if _qa_quit_sent or run.mode=="menu":return
	var movement := _pilot_input() if _pilot else _move_input()
	run.step(movement)
	_consume_events()
	if run.mode=="playing":
		_audio_step_distance+=run.hero.position.distance_to(_audio_previous)
		if _audio_step_distance>1.15:
			audio.play("step",run.tick);_audio_step_distance=0
	_audio_previous=run.hero.position

func _pilot_input() -> Vector2:
	# Explicit QA-only normal input/choice/equipment driver. No HP/mana/XP grants.
	if run.mode=="choice":
		var offer: Dictionary=run.get_offer()
		if not offer.is_empty():
			var picked: Dictionary=offer.cards[0]
			for card in offer.cards:
				if card.kind=="evolve":picked=card;break
			run.choose(offer.token,picked.id)
			hud.invalidate()
	if run.mode=="playing":
		for item in run.inventory:
			if run.equipped.get(item.slot,-1)!=item.uid:
				run.open_inventory();run.equip(item.uid);run.close_inventory();hud.invalidate()
		var at: Vector2=run.hero.position
		var destination := Vector2(cos(run.elapsed()*.21),sin(run.elapsed()*.21))*6.5
		var nearest := 16.0
		for orb in run.orbs:
			var d: float=at.distance_squared_to(orb.position)
			if d<nearest:nearest=d;destination=orb.position
		for e in run.enemies.values():
			if e.elite and e.hp_raw>0:
				var delta: Vector2=e.position-at
				if delta.length()<4.5:
					destination=at-delta.normalized()*5.0
					if e.state=="windup":run.request_dash(-delta)
		return (destination-at).normalized()
	return Vector2.ZERO

func _consume_events() -> void:
	effects.consume(run.events)
	actors.consume(run.events)
	for event in run.events:
		if int(event.seq)<=_last_audio_event:continue
		_last_audio_event=int(event.seq)
		match String(event.type):
			"cast":audio.play({"chapter1.skill.ember":"fire","chapter1.skill.frost":"cold","chapter1.skill.arc":"lightning"}.get(event.skill_id,"fire"),run.tick)
			"hit":audio.play("impact",run.tick)
			"death":audio.play("death",run.tick)
			"explosion":audio.play("explosion",run.tick)
			"shatter":audio.play("cold",run.tick)
			"hero_hit":audio.play("hurt",run.tick)
			"item_drop":audio.play("drop",run.tick)
			"item_pickup":hud.notify("획득: "+event.item.name);audio.play("pickup",run.tick)
			"growth":audio.play_ui("equip",run.tick)

func _process(delta: float) -> void:
	if _qa_quit_sent:return
	_frame_probe.observe(self,run)
	_wall_age+=delta
	if run.mode=="playing" and _frame_ms.size()<15000:_frame_ms.append(delta*1000)
	if not run.hero.is_empty():
		world.update_camera(run.hero.position,delta)
		actors.sync(run,delta)
		effects.sync(run,delta)
	hud.sync(run,delta)
	audio.set_paused(run.mode!="playing" or _qa_quit_sent)
	if not _capture_dir.is_empty():
		# Wait one stable render frame so the saved image contains the new modal.
		if run.mode!=_qa_last_capture_mode:
			_qa_last_capture_mode=run.mode;_qa_pending_capture_mode=run.mode
		elif not _qa_pending_capture_mode.is_empty():
			_qa_state_sequence+=1
			_capture_file("state-%04d-run-%03d-%s.png" % [_qa_state_sequence,_qa_run_sequence,_qa_pending_capture_mode])
			_qa_pending_capture_mode=""
	if run.mode in ["victory","defeat"] and _last_result!=run.mode:
		_last_result=run.mode
		_print_result()
	if not _capture_dir.is_empty():
		for at in [5,20,40,60,75,90]:
			if run.elapsed()>=at and not _captured.has(at):
				_captured[at]=true
				_capture(at)
	if ((_quit_after>0 and _wall_age>=_quit_after) or (_probe_quit_after_complete and _frame_probe.done)) and not _qa_quit_sent:
		_qa_quit_sent=true
		_print_result()
		audio.reset()
		# Fixed-fps offline QA advances simulated timers faster than the audio
		# mixing thread. Stop simulation, then give audio actual wall-clock time.
		var audio_release_at := Time.get_ticks_usec()+150000
		while Time.get_ticks_usec()<audio_release_at:await get_tree().process_frame
		get_tree().quit()

func _capture(at: int) -> void:
	_capture_file("run-%03d-frame-%03d.png" % [_qa_run_sequence,at])

func _capture_file(filename: String) -> void:
	var base := ProjectSettings.globalize_path("res://plans/chapter1-c2-20261031-01/").replace("\\","/")
	var quality_base := ProjectSettings.globalize_path("res://plans/chapter1-quality-20261031-01/").replace("\\","/")
	var export_base := OS.get_executable_path().get_base_dir().replace("\\","/")+"/qa-captures/"
	var dest := _capture_dir.replace("\\","/").simplify_path()
	if not dest.begins_with(base) and not dest.begins_with(quality_base) and not dest.begins_with(export_base):push_error("Capture directory must be inside a C2/quality evidence directory or executable qa-captures directory");return
	DirAccess.make_dir_recursive_absolute(dest)
	var path := dest.path_join(filename)
	if FileAccess.file_exists(path):push_error("Refusing to overwrite capture: "+path);return
	var image := get_viewport().get_texture().get_image()
	if image:print("CHAPTER1_CAPTURE ",path," ",image.save_png(path))

func _print_result() -> void:
	var values := _frame_ms.duplicate();values.sort()
	var p95: float=values[mini(values.size()-1,int(values.size()*.95))] if not values.is_empty() else 0.0
	print("CHAPTER1_RUNTIME_RESULT ",JSON.stringify({"mode":run.mode,"elapsed":run.elapsed(),"kills":run.kills,"hp_raw":run.hero.get("hp_raw",0),"metrics":run.metrics,"growth":run.growth.snapshot(),"equipped":run.equipped,"pilot":_pilot,"qa_ignore_focus":_qa_ignore_focus,"frame_samples":values.size(),"frame_p95_ms":p95,"scope":"representative encounter; captures/driver may perturb frame times; not formal GPU quality pass"}))
