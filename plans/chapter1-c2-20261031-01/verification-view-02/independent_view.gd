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
	check(buttons(view.hud.modal).size()==3,"three actual menu start buttons")
	check(not view._pilot and not view._qa_ignore_focus,"fixture does not enable pilot or ignore-focus")
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
	if "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional verifier failure")
	print("CHAPTER1_INDEPENDENT_VIEW ",JSON.stringify({"checks":checks,"failures":failures,"observations":observations,"scope":"Synthetic headless actual-scene/HUD and command handler fixture; not OS/GPU/normal-play proof"}))
	view.audio.reset()
	await create_timer(.2).timeout
	view.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
