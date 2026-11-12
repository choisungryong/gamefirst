extends SceneTree
## Offline fixed-input visual comparison, never a real-time performance result.
var output := ""
var width := 1280
var results: Array=[]
var failed := false
func _initialize() -> void:call_deferred("_compare")
func _compare() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--arc44-output="):output=arg.trim_prefix("--arc44-output=")
		if arg.begins_with("--arc44-width="):width=int(arg.trim_prefix("--arc44-width="))
	if output.is_empty() or width not in [1280,1920] or not "--chapter1-profile-off" in OS.get_cmdline_user_args():quit(2);return
	if DirAccess.dir_exists_absolute(output):quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(width,width*9/16)
	root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	for variant in [43,44]:
		var view: Node3D=load("res://chapter1/ChapterOne.tscn").instantiate()
		if variant==44:view.effects=load("res://chapter1/view/chapter_elements_quality44.gd").new()
		root.add_child(view);view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
		view.start_run("chapter1.skill.arc");view.audio.set_muted(true)
		var hashes: Array=[];var presentation_hashes: Array=[];var captures := {}
		var counts := {"cast":0,"hit":0,"death":0,"segments":0,"branch_casts":0,"three_branch_casts":0,"stunned_frames":0}
		var last_seq := -1;var pause_checked := false;var pause_ok := true
		for iteration in 3600:
			var move: Vector2=view.full_pilot.decide()
			if view.run.mode!="playing":break
			view.run.step(move)
			var capture := ""
			for event in view.run.events:
				if int(event.seq)<=last_seq:continue
				last_seq=int(event.seq)
				if event.get("skill_id","")!="chapter1.skill.arc":continue
				if event.type=="cast":
					var origins := {}
					var branched := false
					for segment in event.get("segments",[]):
						counts.segments+=1
						if origins.has(segment.from):branched=true
						origins[segment.from]=int(origins.get(segment.from,0))+1
					if branched:counts.branch_casts+=1
					var three_way := false
					for count in origins.values():
						if int(count)>=3:three_way=true
					if three_way:
						counts.three_branch_casts+=1
						if not captures.has("three_branch"):capture="three_branch"

				if counts.has(event.type):
					counts[event.type]+=1
					if not captures.has(event.type):capture=event.type
			view.effects.consume(view.run.events);view.actors.consume(view.run.events)
			view.world.update_camera(view.run.hero.position,1.0/60)
			view.actors.sync(view.run,1.0/60);view.effects.sync(view.run,1.0/60);view.hud.sync(view.run,1.0/60)
			if view.effects.stun36_visible>0:
				counts.stunned_frames+=1
				if capture.is_empty() and not captures.has("stun") and counts.stunned_frames>5:capture="stun"
			if capture.is_empty() and not captures.has("afterglow"):
				for link in view.effects.arc_links:
					if link.age/link.duration>.40 and link.age/link.duration<.80:capture="afterglow";break
			if not pause_checked and not view.effects.contacts.is_empty():
				pause_checked=true;var old_mode: String=view.run.mode;view.run.mode="paused"
				var before := JSON.stringify(pools(view.effects))
				for repeat in 8:view.effects.sync(view.run,1.0/60)
				pause_ok=before==JSON.stringify(pools(view.effects));view.run.mode=old_mode
			hashes.append(JSON.stringify(view.run.snapshot()).sha256_text())
			presentation_hashes.append(JSON.stringify(pools(view.effects)).sha256_text())
			if not capture.is_empty():
				await process_frame;await RenderingServer.frame_post_draw
				var path := output.path_join("%d-%s-tick%d.png"%[variant,capture,view.run.tick])
				if root.get_texture().get_image().save_png(path)!=OK:failed=true
				captures[capture]={"tick":view.run.tick,"path":path}
			elif iteration%3==0:await process_frame
		var result := {"variant":variant,"tick":view.run.tick,"counts":counts,"captures":captures,"core_hash_chain":JSON.stringify(hashes).sha256_text(),"pool_hash_chain":JSON.stringify(presentation_hashes).sha256_text(),"pause_checked":pause_checked,"pause_unchanged":pause_ok}
		results.append(result);print("ARC44_VARIANT ",JSON.stringify(result))
		view.audio.reset();view.queue_free();await process_frame;await process_frame
	var same_core: bool=results.size()==2 and results[0].core_hash_chain==results[1].core_hash_chain
	var same_pools: bool=results.size()==2 and results[0].pool_hash_chain==results[1].pool_hash_chain
	for result in results:
		if not result.pause_checked or not result.pause_unchanged or result.counts.hit==0:failed=true
	if not same_core or not same_pools:failed=true
	var report := {"same_core_hash_chain":same_core,"same_presentation_pools":same_pools,"variants":results,"success":not failed,"width":width,"scope":"Fixed-step presentation comparison; no performance/full-win/three-branch claim unless observed"}
	var file := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("ARC44_RESULT ",JSON.stringify(report));quit(1 if failed else 0)
func pools(effects: RefCounted) -> Dictionary:
	return {"strokes":effects.strokes,"contacts":effects.contacts,"debris":effects.debris,"arc_links":effects.arc_links,"ice_fragments":effects.ice_fragments,"stun_visible":effects.stun36_visible}
