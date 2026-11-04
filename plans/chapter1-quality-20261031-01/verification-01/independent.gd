extends SceneTree
## Independent synthetic actual-scene fixture. No normal-play/GPU/OS-input claim.
var checks := 0
var failures: Array[String] = []
var observations: Dictionary = {}
var view: Node3D

func _initialize() -> void:
	call_deferred("exercise")

func check(value: bool, label: String) -> void:
	checks += 1
	if not value: failures.append(label)

func labels(node: Node) -> Array[String]:
	var result: Array[String] = []
	if node is Label: result.append(node.text)
	for child in node.get_children():result.append_array(labels(child))
	return result

func buttons(node: Node) -> Array[Button]:
	var result: Array[Button] = []
	if node is Button:result.append(node)
	for child in node.get_children():result.append_array(buttons(child))
	return result

func press_button(text: String) -> bool:
	for button in buttons(view.hud.modal):
		if button.text==text:
			button.pressed.emit()
			return true
	return false

func key(logical: int, physical: int, pressed: bool=true, echo: bool=false) -> InputEventKey:
	var event := InputEventKey.new()
	event.keycode=logical
	event.physical_keycode=physical
	event.pressed=pressed
	event.echo=echo
	return event

func hotkey(logical: int, physical: int, pressed: bool=true, echo: bool=false) -> void:
	view._unhandled_key_input(key(logical,physical,pressed,echo))
	view.hud.sync(view.run,0)

func exercise() -> void:
	view=load("res://chapter1/Chapter1.tscn").instantiate()
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	await process_frame
	var run: RefCounted=view.run
	check(run.mode=="menu","actual scene starts in menu")
	check(view.hud.overlay.visible,"menu overlay shown")
	check(buttons(view.hud.modal).filter(func(b):return b.text.ends_with("으로 시작")).size()==3,"three actual menu start buttons plus separate motion control")
	check(not view._pilot and not view._qa_ignore_focus,"fixture does not enable pilot or ignore-focus")
	exercise_motion(run)
	var initial_seed: int=view.seed_
	view.start_run("chapter1.skill.ember")
	view.hud.sync(run,0)
	check(run.mode=="playing" and not view.hud.overlay.visible,"start enters playing and hides overlay")
	check(view.hud.hp.value==120*256,"initial actual HUD HP120")
	check(view.hud.status.text.contains("120 / 120"),"initial HP label")
	# Synthesize only the boundary condition: last HUD update and terminal damage at one tick.
	run.tick=100
	run.hero.hp_raw=5*256
	view.hud.sync(run,0)
	check(view.hud.hp.value==5*256,"prime last HUD update with HP5 at tick100")
	run._hero_damage(5*256,Vector2.ZERO)
	var terminal_snapshot: Dictionary=run.snapshot()
	view.hud.sync(run,0)
	check(run.mode=="defeat" and run.hero.hp_raw==0,"real damage transition reaches defeat HP0")
	check(view.hud.hp.value==0,"same-tick defeat immediately refreshes HP bar to0")
	check(view.hud.status.text.contains("0 / 120"),"same-tick defeat label shows0")
	check(labels(view.hud.modal).has("회랑에 쓰러졌습니다"),"defeat modal shown")
	check(run.snapshot()==terminal_snapshot,"HUD sync does not mutate terminal core")
	observations.terminal={"tick":run.tick,"hp_raw":run.hero.hp_raw,"bar":view.hud.hp.value,"status":view.hud.status.text}
	# Reproduce the native diagnostic: logical R but physical Pause.
	hotkey(KEY_R,KEY_PAUSE)
	check(run.mode=="playing" and run.tick==0,"logical R with physicalPause retries")
	check(view.seed_==initial_seed+1,"retry advances seed exactly once")
	check(run.hero.hp_raw==120*256 and view.hud.hp.value==120*256,"retry resets core and HUD to HP120")
	check(view.hud.status.text.contains("120 / 120"),"retry HP label immediately refreshed")
	check(run.inventory.is_empty(),"retry does not retain previous run gear")
	# Unknown keys and observer-only logging cannot change the core.
	var before_observer: Dictionary=run.snapshot()
	view._qa_log_key(key(KEY_F12,KEY_PAUSE),"fixture_observer")
	check(run.snapshot()==before_observer,"optional key observer does not mutate core")
	hotkey(KEY_F12,KEY_PAUSE)
	check(run.snapshot()==before_observer,"unknown logical key is not treated as physicalPause command")
	# Echo and releases must not toggle any command.
	hotkey(KEY_ESCAPE,KEY_PAUSE,false)
	check(run.mode=="playing","key release does not pause")
	hotkey(KEY_ESCAPE,KEY_PAUSE,true,true)
	check(run.mode=="playing","key echo does not pause")
	hotkey(KEY_ESCAPE,KEY_PAUSE)
	check(run.mode=="paused" and view.hud.overlay.visible,"logicalEscape with physicalPause pauses")
	check(labels(view.hud.modal).has("잠시 멈춤"),"actual pause modal label")
	var paused: Dictionary=run.snapshot()
	for i in 20:run.step(Vector2.RIGHT)
	check(run.snapshot()==paused,"paused input cannot advance combat")
	hotkey(0,KEY_ESCAPE)
	check(run.mode=="playing","physical fallback works only when logical key is0")
	# Pending growth survives nested inventory and pause. These are explicit fixture awards/items.
	run.hero.hp_raw=111*256
	run.growth.award_xp(6)
	run._refresh_mode()
	view.hud.sync(run,0)
	check(run.mode=="choice","legal XP creates choice")
	check(view.hud.hp.value==111*256,"same-tick choice transition forces HUD update")
	var offered: Dictionary=run.get_offer()
	check(offered.cards.size()==3,"actual offer contains3 cards")
	check(buttons(view.hud.modal).size()==3,"three actual choice buttons")
	var item: Dictionary=run.ITEM_TEMPLATES[1].duplicate(true)
	item.uid=41
	item.quality="common"
	item.collected=true
	item.position=Vector2.ZERO
	item.drop_tick=0
	run.inventory.append(item)
	hotkey(KEY_I,KEY_PAUSE)
	check(run.mode=="inventory","logical I opens inventory from choice")
	check(labels(view.hud.modal).has("장비와 전투 선택"),"actual inventory modal")
	check(labels(view.hud.modal).has("수호의 재옷"),"actual item comparison displayed")
	var target_before: bool=view._has_move_target
	check(press_button("장착"),"actual equip button signal connected")
	view.hud.sync(run,0)
	check(run.equipped.get("body",-1)==41,"equip button applies actual owned UID")
	check(run.hero.max_hp_raw==150*256 and run.hero.hp_raw==111*256,"body raises max HP without healing")
	check(view.hud.status.text.contains("111 / 150"),"same-tick equip HUD values match core")
	check(view._has_move_target==target_before,"equip signal does not introduce world move target")
	hotkey(KEY_ESCAPE,KEY_PAUSE)
	check(run.mode=="choice","Escape closes inventory and restores pending choice")
	check(run.get_offer().token==offered.token,"inventory preserved actual offer token")
	hotkey(KEY_ESCAPE,KEY_PAUSE)
	check(run.mode=="paused","Escape pauses pending choice")
	hotkey(KEY_ESCAPE,KEY_PAUSE)
	check(run.mode=="choice" and run.get_offer().token==offered.token,"resume restores same growth offer")
	target_before=view._has_move_target
	check(press_button("선택"),"actual growth button signal connected")
	view.hud.sync(run,0)
	check(run.mode=="playing","actual growth button consumes pending offer")
	check(run.growth.snapshot().ranks["chapter1.skill.ember"]==2,"actual selected rank applied")
	check(view._has_move_target==target_before,"growth signal does not introduce world move target")
	hotkey(KEY_I,KEY_PAUSE)
	check(run.mode=="inventory","logicalI opens inventory during play")
	target_before=view._has_move_target
	check(press_button("전투로 돌아가기 [I]"),"actual close inventory signal connected")
	view.hud.sync(run,0)
	check(run.mode=="playing" and not view.hud.overlay.visible,"close inventory returns to playing")
	check(view._has_move_target==target_before,"inventory close signal does not introduce world move target")
	# Dash/mute handlers must also use the observed logical code.
	hotkey(KEY_SPACE,KEY_PAUSE)
	check(run.get_next_dash_tick()==180,"logicalSpace with physicalPause starts dash cooldown")
	var mute_before: bool=view.audio.muted
	hotkey(KEY_M,KEY_PAUSE)
	check(view.audio.muted!=mute_before,"logicalM toggles audio mute state")
	hotkey(KEY_M,KEY_PAUSE)
	check(view.audio.muted==mute_before,"second logicalM restores mute state")
	exercise_quality()
	if "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional verifier failure")
	print("CHAPTER1_INDEPENDENT_VIEW ",JSON.stringify({"checks":checks,"failures":failures,"observations":observations,"scope":"Synthetic headless actual-scene/HUD and command handler fixture; not OS/GPU/normal-play proof"}))
	view.audio.reset()
	await create_timer(.2).timeout
	view.free();view=null;run=null
	await process_frame
	quit(0 if failures.is_empty() else 1)

func exercise_motion(run: RefCounted) -> void:
	var motion: CheckButton
	for button in buttons(view.hud.modal):
		if button is CheckButton and button.text=="화면 흔들림":motion=button
	check(motion!=null,"actual menu has separate motion checkbutton")
	var before: Dictionary=run.snapshot()
	if motion:
		motion.button_pressed=false
		check(not view.hud.motion_enabled and view.world._reduced_motion,"actual motion toggle disables camera response")
		view.world.kick_camera(1.0)
		check(view.world._camera_trauma==0.0,"reduced motion refuses new trauma")
		motion.button_pressed=true
		check(view.hud.motion_enabled and not view.world._reduced_motion,"actual motion toggle restores camera option")
	check(run.snapshot()==before,"motion preference does not change core")

func exercise_quality() -> void:
	var run: RefCounted=view.run
	var fx: RefCounted=view.effects
	var audio: RefCounted=view.audio
	fx.reset()
	var hit := {"seq":1,"type":"hit","position":Vector2(1,0),"tick":1,"skill_id":"chapter1.skill.ember","target_id":900}
	fx.consume([hit])
	var after_first: Array=fx.debris.duplicate(true)
	fx.consume([hit])
	check(fx.debris==after_first,"FX event sequence replay emits no duplicate particle")
	var explosion := {"seq":2,"type":"explosion","position":Vector2.ZERO,"tick":2,"skill_id":"chapter1.skill.ember","radius_cm":340,"evolved":true}
	fx.consume([explosion])
	check(fx.strokes.size()==1 and is_equal_approx(float(fx.strokes[0].radius),3.4),"impact uses paid event radius3.4")
	run.set_paused(true)
	var paused_core: Dictionary=run.snapshot()
	var frozen_debris: Array=fx.debris.duplicate(true)
	var frozen_strokes: Array=fx.strokes.duplicate(true)
	fx.sync(run,5.0)
	check(fx.debris==frozen_debris and fx.strokes==frozen_strokes,"paused FX does not age or move particles/strokes")
	check(run.snapshot()==paused_core,"paused FX sync leaves full core unchanged")
	run.set_paused(false)
	var render_core: Dictionary=run.snapshot()
	var line_id: int=fx._line_mesh.get_instance_id()
	var fill_id: int=fx._fill_mesh.get_instance_id()
	var beam_id: int=fx._beam_mesh.get_instance_id()
	fx.sync(run,.01)
	fx.sync(run,.01)
	check(fx._line_mesh.get_instance_id()==line_id and fx._fill_mesh.get_instance_id()==fill_id and fx._beam_mesh.get_instance_id()==beam_id,"dynamic mesh objects reused across sync")
	check(run.snapshot()==render_core,"playing FX sync leaves full core unchanged")
	fx.sync(run,2.0)
	check(fx.debris.is_empty() and fx.strokes.is_empty(),"playing FX lifetimes expire")
	fx.burst(Vector2.ZERO,Color.ORANGE,10000)
	check(fx.debris.size()==960,"external burst cannot exceed960 particle slots")
	fx.reset()
	var many: Array=[]
	for i in 120:
		var e: Dictionary=explosion.duplicate(true);e.seq=i+100;e.tick=10
		many.append(e)
	fx.consume(many)
	check(fx.strokes.size()==8,"120 explosion events retain bounded8 new impacts per consume")
	for batch in 14:
		for e in many:e.seq+=200
		fx.consume(many)
	check(fx.strokes.size()==96 and fx.debris.size()<=960,"repeated bursts cap strokes96 and particles960")
	fx.sync(run,0)
	check(fx.impacts.multimesh.visible_instance_count<=48 and fx.plumes.multimesh.visible_instance_count<=48,"48 visible impacts and plumes maximum")
	fx.reset();fx.sync(run,0)
	check(fx.impacts.multimesh.visible_instance_count==0 and fx.plumes.multimesh.visible_instance_count==0 and fx.shards.multimesh.visible_instance_count==0,"reset then sync clears old visible effects")
	# A synthetic immutable projectile retains its form when actual offered rank changes.
	run.projectiles.clear()
	var p := {"uid":900,"position":Vector2.ZERO,"direction":Vector2.RIGHT,"radius":.16,"skill_id":"chapter1.skill.ember","hostile":false}
	run.projectiles.append(p)
	fx.sync(run,0)
	var paid_transform: Transform3D=fx.projectiles.multimesh.get_instance_transform(0)
	var paid_data: Color=fx.projectiles.multimesh.get_instance_custom_data(0)
	run.growth.award_xp(30);run._refresh_mode()
	var offer: Dictionary=run.get_offer()
	for card in offer.get("cards",[]):
		if card.kind=="rank" and card.skill_id=="chapter1.skill.ember":run.choose(offer.token,card.id);break
	var before_draw: Dictionary=run.snapshot()
	fx.sync(run,0)
	check(fx.projectiles.multimesh.get_instance_transform(0)==paid_transform and fx.projectiles.multimesh.get_instance_custom_data(0)==paid_data,"in-flight projectile form ignores later current rank")
	check(run.snapshot()==before_draw,"projectile rendering does not modify core or paid record")
	# These are headless command-handler checks, not sound audition.
	audio.reset();audio.set_muted(false);audio.set_master_volume(1);audio.set_paused(false)
	check(audio.voices.size()==13 and audio.voices[0].stream==audio.ambience,"bounded13 voices reserve loop slot0")
	var before_played: int=audio.played
	for i in 10:audio.play("fire",1000+i*100)
	check(audio.played==before_played+10,"ten noncritical voices can play")
	var before_drop: int=audio.dropped
	audio.play("fire",2100)
	check(audio.played==before_played+10 and audio.dropped==before_drop+1,"noncritical cue cannot consume two reserved voices")
	audio.play("hurt",2200);audio.play_ui("equip",2300)
	check(audio.played==before_played+12,"critical and UI cues use final two reserved voices")
	audio.play("drop",2400)
	check(audio.played==before_played+12 and audio.voices.size()==13,"full voice pool drops without unbounded allocation")
	check(audio.voices[0].stream==audio.ambience,"one-shots never replace ambience")
	audio.set_muted(true)
	var quiet: bool=true
	for voice in audio.voices:quiet=quiet and voice.volume_db<=-79.9
	check(quiet,"mute attenuates every active voice")
	audio.set_muted(false);audio.set_paused(true)
	var stop_count: int=audio.played
	audio.play("cold",2500)
	check(audio.played==stop_count,"paused gameplay cue refused")
	audio.reset()
	check(audio.paused and audio.last_cue_tick.is_empty() and audio.variants.is_empty(),"audio reset clears cue reservation and variant state")
	var all_stopped: bool=true
	for voice in audio.voices:all_stopped=all_stopped and not voice.playing
	check(all_stopped,"audio reset stops all voices")
	audio.set_paused(false)
	audio.play("cold",2600)
	var one_cue: int=audio.played
	audio.play("cold",2601)
	check(audio.played==one_cue,"same cue cooldown prevents replay")
	audio.set_paused(true);audio.play_ui("equip",2700)
	check(audio.played==one_cue+1,"paused UI cue has audible command path")
	audio.reset();audio.set_paused(false)
	var death := {"seq":50000,"type":"death","position":Vector2.ZERO,"tick":0,"skill_id":"chapter1.skill.ember","target_id":900,"kind":"walker"}
	run.events.clear();run.events.append(death)
	view._consume_events()
	var after_death: int=audio.played
	view._consume_events()
	check(audio.played==after_death,"glue sequence guard prevents duplicate death cue")
	audio.reset()
	# Authored casts use four directional clips while legacy walking stays explicit.
	var hero_def: Dictionary=view.actors.sprite_definitions.get("hero",{})
	check(hero_def.get("directional_cast",false),"new hero directional cast metadata adopted")
	for facing in ["north","east","south","west"]:
		check(hero_def.frames.has_animation("cast_"+facing) and hero_def.frames.get_frame_count("cast_"+facing)==4,"four authored cast phases for "+facing)
	var actor_before: Dictionary=run.snapshot()
	view.actors.sync(run,0)
	check(run.snapshot()==actor_before,"actor presentation leaves full core unchanged")
	var initial_trauma: float=view.world._camera_trauma
	view.world.set_reduced_motion(true);view.world.kick_camera(100)
	check(view.world._camera_trauma==0,"reduced camera option clears and blocks trauma")
	view.world.set_reduced_motion(false)
	for i in 30:view.world.kick_camera(100)
	check(view.world._camera_trauma<=.9,"camera trauma remains bounded")
	check(view.world.art_status.get("props",0)<=500,"decorative props count bounded in authored composition")
	observations.quality={"particles":960,"strokes":96,"impacts":48,"voices":audio.voices.size(),"directional_cast":hero_def.get("directional_cast",false),"props":view.world.art_status.get("props",0)}
