extends "res://chapter1/chapter_view.gd"
const ChapterRun=preload("res://chapter1/core/chapter_run_quality16.gd")
const ChapterWorld=preload("res://chapter1/view/chapter_world_quality31d.gd")
const ChapterHUD=preload("res://chapter1/view/chapter_hud_quality27.gd")
const ChapterEffects=preload("res://chapter1/view/chapter_elements_quality26.gd")
const ChapterPilot=preload("res://chapter1/core/chapter_pilot.gd")
const ChapterProfile=preload("res://chapter1/core/chapter_profile.gd")
const ChapterActors=preload("res://chapter1/view/chapter_actors_quality30c.gd")
var full_pilot=ChapterPilot.new()
var profile=ChapterProfile.new()
var _receipt := ""
var _saved_receipt := ""
var _profile_off := false
var _chapter_last_event := -1
func _init() -> void:
	run=ChapterRun.new();world=ChapterWorld.new();hud=ChapterHUD.new();effects=ChapterEffects.new();actors=ChapterActors.new()
	full_pilot.run=run
func _ready() -> void:
	_profile_off="--chapter1-profile-off" in OS.get_cmdline_user_args()
	if _profile_off:profile.error="검증 실행 · 저장 비활성"
	else:profile.configure()
	_sync_profile("저장 준비" if profile.available else profile.error)
	hud.stash_show.connect(func():hud.stash_open=true;hud.invalidate())
	hud.stash_equip.connect(func(id_: int):_sync_profile("다음 도전 장비 저장 완료" if profile.select_item(id_) else profile.error))
	hud.stash_salvage.connect(func(id_: int):_sync_profile("장비 해체 저장 완료" if profile.salvage(id_) else profile.error))
	hud.save_retry.connect(_save_terminal)
	super._ready()
	DisplayServer.window_set_title("잿빛 회랑 · 제1장")
	print("FULL_CHAPTER_READY ",JSON.stringify({"scene":"chapter1/ChapterOne.tscn","three_connected_zones":true,"scope":"Full chapter implementation candidate; quality/pacing/manual/audio gates open"}))
func start_run(id_: String) -> void:
	if profile.available and profile.state.items.size()>256:
		hud.stash_open=true;_sync_profile("회수 장비를 해체해 256개 이하로 정리하면 출발할 수 있습니다");return
	if not profile.available and not _profile_off and profile.error!="전용 저장 경로가 없는 미리보기입니다":hud.notify(profile.error);return
	_chapter_last_event=-1
	_receipt="%d-%d-%d"%[OS.get_process_id(),Time.get_unix_time_from_system(),Time.get_ticks_usec()];_saved_receipt=""
	hud.stash_open=false
	super.start_run(id_)
	if profile.available:
		if not run.import_starting_gear(profile.starting_gear()):push_error("Starting gear import rejected");get_tree().quit(1);return
		hud.invalidate()
	hud.notify("앞뜰의 봉인을 돌파하세요 · Q 회복약 · E 선택 의식")

func _sync_profile(note: String) -> void:
	hud.profile_state=profile.state.duplicate(true);hud.profile_note=note;hud.invalidate()

func _save_terminal() -> void:
	if run.mode not in ["victory","defeat"]:return
	if _saved_receipt==_receipt:_sync_profile("이번 도전 보상 저장 완료");return
	if not profile.available:_sync_profile(profile.error);return
	if profile.record_run(_receipt,run.inventory,run.pending_rewards,run.mode=="victory",run.tick):
		_saved_receipt=_receipt;_sync_profile("이번 도전 보상 저장 완료 · 장비 %d개"%profile.state.items.size())
	else:_sync_profile(profile.error+" · 현재 보상은 이 화면에 유지됩니다")
func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var key: int=event.keycode if event.keycode!=0 else event.physical_keycode
		if key==KEY_ESCAPE and hud.stash_open:
			hud.stash_open=false;hud.invalidate();get_viewport().set_input_as_handled();return
		if key==KEY_Q:
			if run.drink_potion():_consume_events();hud.invalidate()
			get_viewport().set_input_as_handled();return
		if key==KEY_E:
			for def in run.RITUALS:
				if run.activate_ritual(def.id):_consume_events();hud.invalidate();break
			get_viewport().set_input_as_handled();return
	super._unhandled_key_input(event)
func _pilot_input() -> Vector2:return full_pilot.decide()
func _consume_events() -> void:
	super._consume_events()
	for event in run.events:
		if int(event.seq)<=_chapter_last_event:continue
		_chapter_last_event=event.seq
		match String(event.type):
			"victory","defeat":_save_terminal()
			"item_pickup":hud.notify("획득: "+event.item.name+" · I 비교·장착")
			"gate_opened":hud.notify("봉인 해제 · 동쪽 회랑으로 "+event.name);audio.play_ui("equip",run.tick)
			"zone_entered":hud.notify(run.ZONE_NAMES[run.zone]+" · 새로운 봉인을 돌파하세요")
			"chapter_champion":hud.notify(event.name+" 출현");world.kick_camera(.45)
			"boss_phase":hud.notify("파수왕의 격노 · 재의 낙인을 피하세요");world.kick_camera(.6)
			"chapter_burst":audio.play("explosion",run.tick)
			"potion_used":hud.notify("회복약 사용 · %d개 남음"%run.potions);audio.play("pickup",run.tick)
			"ritual_completed":hud.notify(event.name+" 완료 · 보상 획득");audio.play_ui("equip",run.tick)
			"reward_pending":hud.notify("가방이 가득 찼습니다 · 의식 보상을 보관 대기합니다")
func _process(delta: float) -> void:
	super._process(delta)
	world.sync(run,delta)
	if not _capture_dir.is_empty():
		for at in [150,210,270,330,390,450,510]:
			if run.elapsed()>=at and not _captured.has(at):_captured[at]=true;_capture(at)
func _capture_file(filename: String) -> void:
	var base := ProjectSettings.globalize_path("res://plans/chapter1-quality04-20261101-01/").replace("\\","/")
	var dest := _capture_dir.replace("\\","/").simplify_path()
	if not dest.begins_with(base):super._capture_file(filename);return
	DirAccess.make_dir_recursive_absolute(dest)
	var path := dest.path_join(filename)
	if FileAccess.file_exists(path):push_error("Refusing to overwrite full chapter capture");return
	var image := get_viewport().get_texture().get_image()
	if image:print("FULL_CHAPTER_CAPTURE ",path," ",image.save_png(path))
func _print_result() -> void:
	var summary: Dictionary=run.snapshot();summary.erase("enemies");summary.erase("projectiles");summary.erase("orbs");summary.erase("items")
	summary.scope="Full chapter candidate, normal QA driver when enabled; visual/manual/audio/performance approval separate"
	summary.pilot=_pilot;summary.qa_ignore_focus=_qa_ignore_focus
	summary.profile_available=profile.available;summary.profile_off=_profile_off;summary.profile_note=hud.profile_note
	print("FULL_CHAPTER_RUNTIME_RESULT ",JSON.stringify(summary))
