extends SceneTree
## Explicit presentation fixture: native elite definition + four core damage
## calls using the actual rank2 frost effect. Not a normal-play freeze claim.
var output := ""
func _initialize() -> void:call_deferred("_fixture")
func _fixture() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--frost39-output="):output=arg.trim_prefix("--frost39-output=")
	if output.is_empty() or not "--chapter1-profile-off" in OS.get_cmdline_user_args():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var results: Array=[]
	for variant in [36,39]:
		var view: Node3D=load("res://chapter1/ChapterOne.tscn").instantiate()
		if variant==39:view.effects=load("res://chapter1/view/chapter_elements_quality39.gd").new()
		root.add_child(view);view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
		view.start_run("chapter1.skill.frost");view.run.enemies.clear()
		view.run.growth.award_xp(12);view.run._refresh_mode()
		var offer: Dictionary=view.run.get_offer()
		for card in offer.cards:
			if card.id=="rank:chapter1.skill.frost:2":view.run.choose(offer.token,card.id);break
		view.run._spawn("elite",view.run.hero.position+Vector2(2.5,0))
		var victim: int=view.run.enemies.keys()[0]
		var effects: Dictionary=view.run.effective_skill("chapter1.skill.frost").effects
		for i in 4:
			var context := {"uid":39000+i,"skill_id":"chapter1.skill.frost","effects":effects.duplicate(true),"remaining_hits":effects.hit_budget,"hit_ids":[],"evolved":false}
			view.run._damage_enemy(victim,context,0)
		view.effects.consume(view.run.events);view.actors.consume(view.run.events)
		for i in 6:
			view.run.step(Vector2.ZERO)
			view.effects.consume(view.run.events);view.actors.consume(view.run.events)
			view.world.update_camera(view.run.hero.position,1.0/60)
			view.actors.sync(view.run,1.0/60);view.effects.sync(view.run,1.0/60);view.hud.sync(view.run,1.0/60)
			await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(output.path_join("%d-frozen-fixture.png"%variant))
		var e: Dictionary=view.run.enemies[victim]
		var result := {"variant":variant,"core_hash":JSON.stringify(view.run.snapshot()).sha256_text(),"hp_raw":e.hp_raw,"frozen_until":e.frozen_until,"tick":view.run.tick,"ice_instances":view.effects.ice_batch.multimesh.visible_instance_count}
		view.run.mode="paused"
		var paused := JSON.stringify(view.effects.ice_targets)
		for i in 8:view.effects.sync(view.run,1.0/60)
		result.pause_unchanged=paused==JSON.stringify(view.effects.ice_targets)
		view.run.mode="playing"
		for i in 24:
			view.run.step(Vector2.ZERO);view.effects.consume(view.run.events);view.effects.sync(view.run,1.0/60)
		result.expired_ice_instances=view.effects.ice_batch.multimesh.visible_instance_count
		result.expired_at_tick=view.run.tick
		results.append(result)
		view.audio.reset();view.queue_free();await process_frame;await process_frame
	var success: bool=results[0].core_hash==results[1].core_hash
	for result in results:
		if result.hp_raw<=0 or result.frozen_until<=result.tick or result.ice_instances!=4 or not result.pause_unchanged or result.expired_ice_instances!=0:success=false
	var file := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"success":success,"results":results,"scope":"Explicit native elite/four core-damage-call fixture; actual frozen_until, not normal-play coverage"},"\t"));file.close()
	quit(0 if success else 1)
