extends SceneTree
var checks: Array[Dictionary]=[]
func _initialize() -> void:call_deferred("_study")
func _check(label: String,ok: bool) -> void:checks.append({"label":label,"ok":ok})
func _study() -> void:
	var view=load("res://chapter1/ChapterOne.tscn").instantiate()
	view.hud=load("res://chapter1/view/chapter_hud_quality27.gd").new();root.add_child(view)
	view.set_process(false);view.set_physics_process(false)
	while view.run.tick<16000:view.run.step(view.full_pilot.decide())
	view.hud.sync(view.run,3.0)
	_check("ordinary_toast_y80",is_equal_approx(view.hud.toast.position.y,80.0) and not view.hud.boss_bar.visible)
	while view.run.tick<23000:view.run.step(view.full_pilot.decide())
	view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
	view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0)
	var frozen: Dictionary=view.run.snapshot().duplicate(true)
	DirAccess.make_dir_recursive_absolute("res://hud27-shots")
	var records: Array[Dictionary]=[]
	for size_ in [Vector2i(1920,1080),Vector2i(1440,810),Vector2i(1280,720)]:
		DisplayServer.window_set_size(size_)
		await process_frame
		await process_frame
		for message in ["파수왕의 격노 · 재의 낙인을 피하세요","회복약 사용 · 4개 남음","획득: 신속의 불꽃의 연쇄 매듭 · I 비교·장착"]:
			view.hud.notify(message);view.hud.sync(view.run,0)
			await process_frame
			var after: Rect2=view.hud.toast.get_global_rect()
			var boss: Rect2=view.hud.boss_bar.get_global_rect()
			_check("boss_visible_%d"%size_.x,view.hud.boss_bar.visible)
			_check("separate_%d_%s"%[size_.x,message],not after.intersects(boss) and after.position.y>=boss.end.y+9.9)
			_check("core_unchanged",frozen==view.run.snapshot())
			if message.begins_with("파수왕"):
				view.hud.toast.position.y=80
				await RenderingServer.frame_post_draw
				var before: Rect2=view.hud.toast.get_global_rect()
				_check("old_overlap_%d"%size_.x,before.intersects(boss))
				root.get_texture().get_image().save_png("res://hud27-shots/before-%d.png"%size_.x)
				view.hud.sync(view.run,0)
				await RenderingServer.frame_post_draw
				var img := root.get_texture().get_image();img.save_png("res://hud27-shots/after-%d.png"%size_.x)
				records.append({"requested":[size_.x,size_.y],"image":[img.get_width(),img.get_height()],"boss":str(boss),"before":str(before),"after":str(after)})
	view.hud.sync(view.run,3.0)
	_check("toast_expires",not view.hud.toast.visible)
	_check("same_complete_core",frozen==view.run.snapshot())
	view.audio.reset()
	var ok := true
	for check in checks:ok=ok and check.ok
	var f := FileAccess.open("res://hud27-result.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"checks":checks,"records":records,"passed":ok,"scope":"HUD27 source fixture using normal earned frost23000tick, original core/World22/Actor25b/FX26. Explicit production-message fixtures, before old y80 property vs after. Not actual package27/native/manual/live event proof."},"\t"));f.close()
	for i in 4:await process_frame
	quit(0 if ok else 1)
