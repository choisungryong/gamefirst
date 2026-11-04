extends SceneTree
var checks:=0
var failures:Array[String]=[]
func check(value:bool,message:String)->void:
	checks+=1
	if not value:failures.append(message)
func _initialize()->void:call_deferred("execute")
func execute()->void:
	var scene=load("res://chapter1/Chapter1.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	scene.start_run("chapter1.skill.ember")
	var before:Dictionary=scene.run.snapshot()
	var fx=scene.effects
	fx.burst(Vector2.ZERO,Color.ORANGE,5000)
	check(fx.debris.size()==fx.MAX_PARTICLES,"particle cap")
	var events:Array=[]
	for i in 200:events.append({"type":"explosion","seq":100+i,"tick":1,"position":Vector2.ZERO,"skill_id":"chapter1.skill.ember","radius_cm":340,"evolved":true})
	fx.consume(events)
	check(fx.strokes.size()==8,"per-consume impact budget")
	for i in 20:
		for e in events:e.seq+=200
		fx.consume(events)
	check(fx.strokes.size()<=fx.MAX_STROKES,"stroke cap")
	fx.sync(scene.run,0.01)
	check(fx.impacts.multimesh.visible_instance_count<=fx.MAX_IMPACTS,"impact render cap")
	check(fx.plumes.multimesh.visible_instance_count<=fx.MAX_IMPACTS,"plume render cap")
	check(fx.shards.multimesh.visible_instance_count<=fx.MAX_PARTICLES,"shard render cap")
	check(scene.run.snapshot()==before,"presentation leaves whole core snapshot unchanged")
	fx.sync(scene.run,1.0)
	check(fx.strokes.is_empty() and fx.debris.is_empty(),"bounded lifetime cleanup")
	var audio=scene.audio
	check(audio.voices.size()==13,"voice cap13")
	check(audio.streams.size()==11,"eleven distinct cue families")
	var count:=0
	for cue in audio.streams:
		for stream in audio.streams[cue]:
			count+=1;check(stream!=null,"loaded cue "+cue)
	check(count==19,"nineteen variants")
	check(audio.ambience!=null,"ambience loaded")
	audio.set_paused(false)
	audio.play("fire",1)
	var played:int=audio.played
	audio.play("fire",2)
	check(audio.played==played,"cue cooldown")
	audio.set_muted(true);audio.play("cold",50)
	check(audio.played==played,"mute prevents new cues")
	audio.set_muted(false);audio.set_paused(true)
	audio.play("cold",70)
	check(audio.played==played,"pause prevents gameplay cues")
	audio.play_ui("equip",70)
	check(audio.played==played+1,"paused UI acknowledgement")
	scene.run.hero.hp_raw=0;scene.run.mode="defeat"
	scene.hud.sync(scene.run,0)
	check(scene.hud.hp.value==0,"same-tick terminal HUD0")
	scene.retry();scene.toggle_pause();scene.hud.sync(scene.run,0)
	check(scene.hud.hp.value==120*256,"retry fresh HP")
	check(scene.hud.skill_labels.size()==3,"three skill identity slots")
	if "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional negative")
	print("QUALITY_PRESENTATION_TEST ",JSON.stringify({"checks":checks,"failures":failures,"scope":"Synthetic presentation fixture, no visual or actual hearing approval"}))
	scene.audio.reset()
	await create_timer(.2).timeout
	scene.free();scene=null;fx=null;audio=null
	await process_frame
	quit(0 if failures.is_empty() else 1)
