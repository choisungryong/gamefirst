extends SceneTree
## Same real Core37/pilot/camera, presentation-only before/after comparison.
var output := ""
var failed := false
var results: Array=[]
func _initialize() -> void:call_deferred("_compare")
func _compare() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--frost39-output="):output=arg.trim_prefix("--frost39-output=")
	if output.is_empty() or not "--chapter1-profile-off" in OS.get_cmdline_user_args():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(1280,720)
	root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	for variant in [36]:
		var view: Node3D=load("res://chapter1/ChapterOne.tscn").instantiate()
		if variant==39:view.effects=load("res://chapter1/view/chapter_elements_quality39.gd").new()
		root.add_child(view);view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
		view.start_run("chapter1.skill.frost");view.audio.set_muted(true)
		var counts := {"cast":0,"hit":0,"shatter":0,"frozen_frames":0}
		var captures := {};var last_seq := -1;var hashes: Array=[]
		var pause_checked := false;var pause_ok := true;var maximum := {"projectiles":0,"contacts":0,"impacts":0,"casts":0}
		for iteration in 3600:
			var move: Vector2=view.full_pilot.decide()
			if view.run.mode!="playing":break
			view.run.step(move)
			var capture := ""
			var capture_at := Vector2.ZERO
			for event in view.run.events:
				if int(event.seq)<=last_seq:continue
				last_seq=int(event.seq)
				if event.get("skill_id","")!="chapter1.skill.frost":continue
				if counts.has(event.type):
					counts[event.type]+=1
					if not captures.has(event.type):capture=event.type;capture_at=event.position
			view.effects.consume(view.run.events);view.actors.consume(view.run.events)
			view.world.update_camera(view.run.hero.position,1.0/60)
			view.actors.sync(view.run,1.0/60);view.effects.sync(view.run,1.0/60);view.hud.sync(view.run,1.0/60)
			var has_frozen := false
			for e in view.run.enemies.values():
				if e.hp_raw>0 and view.run.tick<int(e.frozen_until):has_frozen=true;break
			if has_frozen:
				counts.frozen_frames+=1
				if not captures.has("frozen") and counts.frozen_frames>8:capture="frozen"
			if variant==39:
				maximum.projectiles=maxi(maximum.projectiles,view.effects.frost39_projectile_count)
				maximum.contacts=maxi(maximum.contacts,view.effects.frost39_contact_count)
				maximum.impacts=maxi(maximum.impacts,view.effects.frost39_impact_count)
				maximum.casts=maxi(maximum.casts,view.effects.frost39_cast_count)
			if not pause_checked and not view.effects.contacts.is_empty():
				pause_checked=true
				var old_mode: String=view.run.mode
				view.run.mode="paused"
				var before := JSON.stringify({"strokes":view.effects.strokes,"contacts":view.effects.contacts,"fragments":view.effects.ice_fragments})
				for j in 8:view.effects.sync(view.run,1.0/60)
				pause_ok=before==JSON.stringify({"strokes":view.effects.strokes,"contacts":view.effects.contacts,"fragments":view.effects.ice_fragments})
				view.run.mode=old_mode
			hashes.append(JSON.stringify(view.run.snapshot()).sha256_text())
			if not capture.is_empty():
				var camera: Camera3D=view.get_viewport().get_camera_3d()
				var screen: Vector2=camera.unproject_position(Vector3(capture_at.x,.8,capture_at.y))
				captures[capture]={"tick":view.run.tick,"world":[capture_at.x,capture_at.y],"screen":[screen.x,screen.y]}

		var result := {"variant":variant,"tick":view.run.tick,"mode":view.run.mode,"counts":counts,"captures":captures,"core_hash_chain":JSON.stringify(hashes).sha256_text(),"pause_checked":pause_checked,"pause_unchanged":pause_ok,"maximum_routed":maximum}
		results.append(result);print("FROST39_VARIANT ",JSON.stringify(result))
		view.audio.reset();view.queue_free();await process_frame;await process_frame
	var identical: bool=results.size()==1
	if not identical:failed=true
	for r in results:
		if not r.pause_checked or not r.pause_unchanged:failed=true
	var report := {"same_core_hash_chain":identical,"variants":results,"success":not failed,"scope":"Real60sec seeded Core37 pilot; actual cast/hit/frozen/shatter only; not full win, performance or visual approval"}
	var file := FileAccess.open(output.path_join("EVENT-POSITIONS.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("FROST39_RESULT ",JSON.stringify(report));quit(1 if failed else 0)
