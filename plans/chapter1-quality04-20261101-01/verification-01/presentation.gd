extends SceneTree
## Synthetic headless actual Chapter1 scene. No GPU/OS/normal-play quality claim.
var checks := 0
var failures: Array[String]=[]
var observations: Dictionary={}
var view: Node3D

func _initialize() -> void:call_deferred("exercise")

func check(value: bool, label: String) -> void:
	checks+=1
	if not value:failures.append(label)

func all_core(value: Variant) -> Variant:
	# Include every script variable, nested growth/catalog state and private RNG
	# states. The public snapshot alone omits cooldown/context/event/RNG state.
	if value is RandomNumberGenerator:return {"rng_seed":value.seed,"rng_state":value.state}
	if value is Script:return value.resource_path
	if value is Object:
		var result: Dictionary={}
		for property in value.get_property_list():
			if int(property.usage)&PROPERTY_USAGE_SCRIPT_VARIABLE:result[property.name]=all_core(value.get(property.name))
		return result
	if value is Dictionary:
		var result: Dictionary={}
		for key in value:result[key]=all_core(value[key])
		return result
	if value is Array:
		var result: Array=[]
		for item in value:result.append(all_core(item))
		return result
	return value

func exercise() -> void:
	view=load("res://chapter1/Chapter1.tscn").instantiate()
	root.add_child(view);view.set_process(false);view.set_physics_process(false)
	await process_frame
	view.start_run("chapter1.skill.ember")
	var run: RefCounted=view.run
	check(run.mode=="playing","actual scene starts representative run")
	check(view.actors.raw_texture_fallbacks.is_empty(),"actor textures imported; no raw fallback")
	check(view.audio.raw_fallbacks.is_empty(),"audio resources imported; no raw fallback")
	exercise_interpolation(run)
	exercise_poses(run)
	exercise_overlap(run)
	exercise_effects(run)
	exercise_audio(run)
	# Exercise real core steps and the real scene consume callback with presentation
	# calls at different render/physics ratios. Every private core variable included.
	view.start_run("chapter1.skill.ember")
	var real_samples: Array=[]
	for tick in 90:
		run.step(Vector2.RIGHT if tick<45 else Vector2.UP)
		var before: Variant=all_core(run)
		view._consume_events()
		if tick%2==0:
			view.actors.sync(run,1.0/30.0);view.effects.sync(run,1.0/30.0)
			view.actors.sync(run,0);view.effects.sync(run,0)
		check(all_core(run)==before,"all core variables unchanged after actual consume/presentation at tick%d" % tick)
		if tick in [15,45,89]:real_samples.append({"tick":run.tick,"phase":view.actors.hero.get_meta("motion_sample").phase,"shown":str(view.actors.hero.position),"core":str(run.hero.position)})
	observations.real_samples=real_samples
	observations.shadow_limit="headless dummy MultiMesh getter returned zero transforms; visual contact alignment requires allocated GPU review (positive-03 actual1 preserved)"
	view.toggle_pause()
	check(run.mode=="paused","actual scene pause command enters paused mode")
	var paused_core: Variant=all_core(run)
	view.actors.sync(run,0)
	var paused_at: Vector3=view.actors.hero.position
	var paused_phase: float=view.actors.hero.get_meta("motion_sample").phase
	var paused_cast: int=view.actors._cast_until
	for i in 10:
		run.step(Vector2.DOWN);view._consume_events()
		view.actors.sync(run,.02);view.effects.sync(run,.02)
	check(all_core(run)==paused_core,"pause presentation and attempted core steps leave all private core state unchanged")
	check(view.actors.hero.position==paused_at,"paused scene actor transform remains fixed")
	check(view.actors.hero.get_meta("motion_sample").phase==paused_phase,"paused scene gait phase remains fixed")
	check(view.actors._cast_until==paused_cast,"retained events during pause cannot restart release")
	view.toggle_pause();view.actors.sync(run,0)
	check(run.mode=="playing" and view.actors.hero.position==paused_at,"actual resume command cannot rewind displayed transform")
	view.retry()
	check(view.actors.actors.is_empty(),"retry removes previous actor map before next sync")
	view.actors.sync(run,0)
	check(run.tick==0 and run.hero.hp_raw==120*256,"actual scene retry resets core")
	check(view.actors.actors.size()==24,"next sync presents the actual24 initial enemies")
	check(view.actors._last_event==-1 and view.actors._enemy_recoil.is_empty(),"retry clears event and recoil presentation state")
	check(view.actors.hero.get_meta("motion_sample").phase==0.0,"retry clears gait phase")
	check(not view.actors._hero_rim.visible,"retry hides overlap rim")
	if "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional verifier failure")
	print("QUALITY04_PRESENTATION_CONTRACT ",JSON.stringify({"checks":checks,"failures":failures,"observations":observations,"scope":"synthetic actual-scene headless boundary fixture; not image quality, GPU performance, normal play or listening proof"}))
	# Let scheduled AudioStreamPlayer play commands reach the audio server before
	# stopping/freeing the scene. A fixture that queues and stops everything in a
	# single script turn can otherwise leave unprocessed playback refs at exit.
	await create_timer(.2).timeout
	view.audio.reset();await create_timer(.3).timeout
	view.free();view=null;run=null
	await process_frame
	quit(0 if failures.is_empty() else 1)

func exercise_interpolation(run: RefCounted) -> void:
	var actors: RefCounted=view.actors
	var hero: Node3D=actors.hero
	actors._present_position(hero,Vector2.ZERO,0,true,1)
	var positions: Array=[]
	for fraction in [0.0,.25,.5,.75,1.0]:
		var at: Vector3=actors._present_position(hero,Vector2(.10,0),1,true,fraction)
		check(is_equal_approx(at.x,.1*fraction),"actual Node3D interpolation fraction %.2f" % fraction)
		hero.position=at
		check(hero.position==at,"render transform actually accepts interpolated position")
		positions.append(at.x)
	var phase: float=hero.get_meta("motion_sample").phase
	check(is_equal_approx(phase,.1/actors.HERO_STRIDE),"distance-driven phase uses travelled metres")
	actors._present_position(hero,Vector2(.10,0),1,true,.3)
	check(hero.get_meta("motion_sample").phase==phase,"extra render samples cannot advance gait")
	check(is_equal_approx(actors._present_position(hero,Vector2(.10,0),1,false,.2).x,.1),"pause shows authoritative endpoint")
	check(is_equal_approx(actors._present_position(hero,Vector2(.10,0),1,true,0).x,.1),"resume cannot slide backward")
	check(actors._present_position(hero,Vector2(9,0),2,true,.25).x==9.0,"teleport snaps rather than sweeps")
	check(actors._present_position(hero,Vector2.ZERO,0,true,.25)==Vector3.ZERO,"retry tick rewind snaps")
	# The existing consume callback captures each actual fixed tick, even when
	# render sync happens only every second tick (30Hz render / 60Hz core).
	view.start_run("chapter1.skill.ember")
	actors.sync(run,0)
	for i in 8:
		run.step(Vector2.RIGHT);actors.consume(run.events)
	var sample: Dictionary=hero.get_meta("motion_sample")
	check(int(sample.tick)==run.tick,"consume captures last fixed core tick without render")
	check(sample.previous!=sample.current,"last two exact fixed-tick endpoints retained")
	check(float(sample.phase)>0.0,"gait advances when render skips core ticks")
	observations.interpolation={"quarter_samples":positions,"phase_after_8_core_ticks":sample.phase,"last_previous":str(sample.previous),"last_current":str(sample.current)}

func exercise_poses(run: RefCounted) -> void:
	var actors: RefCounted=view.actors
	var hero: Node3D=actors.hero
	var sprite: AnimatedSprite3D=hero.get_meta("sprite")
	var def: Dictionary=actors.sprite_definitions.hero
	var initial_phase: float=hero.get_meta("motion_sample").phase
	var expected_frame := int(initial_phase*4)%4
	for direction in [Vector2.RIGHT,Vector2.LEFT,Vector2.UP,Vector2.DOWN]:
		actors._update_pose(hero,direction,true,false,false,8,true)
		check(sprite.animation.begins_with("move_"),"turn retains directional existing gait")
		check(sprite.sprite_frames.get_frame_count(sprite.animation)==4,"honest original four gait frames")
		check(sprite.frame==expected_frame,"heading change preserves gait phase")
		check(sprite.offset==def.anchors[sprite.animation][sprite.frame],"frame-specific authored foot anchor")
		check(is_equal_approx(sprite.pixel_size,def.scales[sprite.animation][sprite.frame]),"frame-specific authored physical scale")
	actors.consume([{"type":"cast","seq":10000,"tick":8,"direction":Vector2.UP}])
	for moving in [false,true]:
		actors._update_pose(hero,Vector2.UP,moving,true,false,8,true,false,true)
		check(sprite.animation.begins_with("cast_") and sprite.frame==2,"release event immediately displays release frame")
		actors._update_pose(hero,Vector2.UP,moving,true,false,14,true,false,true)
		check(sprite.frame==3,"release proceeds to recovery frame")
		check(hero.get_meta("motion_sample").phase==initial_phase,"short cast preserves locomotion phase")
	actors._update_pose(hero,Vector2.DOWN,true,false,false,20,true)
	check(sprite.frame==expected_frame,"gait resumes phase after cast interruption")
	var until: int=actors._cast_until
	actors.consume([{"type":"cast","seq":10000,"tick":999,"direction":Vector2.DOWN}])
	check(actors._cast_until==until,"duplicate event sequence cannot restart cast")
	actors._update_pose(hero,Vector2.DOWN,true,false,false,20,false)
	check(sprite.speed_scale==0.0,"pause disables automatic gait animation")
	# Check every authored current animation frame uses the JSON foot anchor;
	# this validates registration, not new foot contact or biomechanical quality.
	var registered := 0
	var source_frames: Array=[]
	for path in ["res://chapter1/art/actors/hero.json","res://chapter1/art/quality03/hero_cast_v01.json"]:
		var doc: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))
		source_frames.append_array(doc.frames)
	for animation in def.anchors:
		for frame in def.anchors[animation].size():
			var texture: Texture2D=def.frames.get_frame_texture(animation,frame)
			var anchor: Vector2=def.anchors[animation][frame]
			var feet := Vector2(texture.get_width()*.5-anchor.x,texture.get_height()*.5+anchor.y)
			check(feet.x>=0 and feet.x<=texture.get_width() and feet.y>=0 and feet.y<=texture.get_height(),"registered foot anchor inside authored frame %s/%d" % [animation,frame])
			var atlas := texture as AtlasTexture
			var matched := false
			for record in source_frames:
				var r: Array=record.region
				if atlas.region!=Rect2(r[0],r[1],r[2],r[3]):continue
				var source_foot := Vector2(float(record.feet[0]),float(record.feet[1]))
				var local_foot := Vector2(source_foot.x-float(r[2])*.5,float(r[3])*.5-source_foot.y)+anchor
				matched=local_foot.length()<.00001 and is_equal_approx(def.scales[animation][frame],1.0/float(record.pixels_per_meter))
				break
			check(matched,"source JSON foot projects exactly to actor origin %s/%d" % [animation,frame])
			registered+=1
	observations.authored_hero_frames_checked=registered

func exercise_overlap(run: RefCounted) -> void:
	view.start_run("chapter1.skill.ember")
	run.enemies.clear() # Controlled overlap boundary, not a normal gameplay claim.
	var actors: RefCounted=view.actors
	actors.sync(run,0)
	check(not actors._hero_rim.visible,"no living enemy means no rim")
	var camera: Camera3D=view.get_viewport().get_camera_3d()
	var toward := Vector2(camera.global_basis.z.x,camera.global_basis.z.z).normalized()
	run._spawn("walker",toward*.4)
	actors.sync(run,0)
	var enemy: Dictionary=run.enemies.values()[0]
	var node: Node3D=actors.actors["%d:%d" % [enemy.generation,enemy.id]]
	check(actors._projected_frame(node,camera).intersects(actors._projected_frame(actors.hero,camera)),"actual displayed frame bounds overlap")
	check(actors._hero_rim.visible,"nearer projected live overlap requests rim")
	var hero_sprite: AnimatedSprite3D=actors.hero.get_meta("sprite")
	check(not hero_sprite.no_depth_test and hero_sprite.render_priority==0,"hero base retains normal depth test and default priority")
	check(actors._hero_rim.get_parent()==actors.hero,"exactly one separate hero outline mesh")
	enemy.position=-toward*.4;actors.sync(run,0)
	check(not actors._hero_rim.visible,"enemy behind hero cannot request rim")
	enemy.position=toward*.4+Vector2(camera.global_basis.x.x,camera.global_basis.x.z)*8
	actors.sync(run,0);check(not actors._hero_rim.visible,"nearer but projected non-overlap has no rim")
	enemy.position=toward*.4;enemy.hp_raw=0;enemy.dead_tick=run.tick
	actors.sync(run,0);check(not actors._hero_rim.visible,"projected corpse overlap has no rim")
	var source := FileAccess.get_file_as_string("res://chapter1/view/hero_occlusion_rim.gdshader")
	check(source.contains("edge-body") and source.contains("ALPHA=outline"),"rim shader removes filled silhouette")
	observations.overlap_scope="projected current-frame rectangles (conservative); no per-pixel alpha/depth occlusion proof"

func exercise_effects(run: RefCounted) -> void:
	var fx: RefCounted=view.effects
	fx.reset();run.mode="playing"
	var events: Array=[]
	for i in 1100:events.append({"seq":i+1,"type":"hit","tick":10,"position":Vector2.ZERO,"skill_id":"chapter1.skill.ember"})
	var before: Variant=all_core(run)
	fx.consume(events)
	check(fx.strokes.size()==12,"dense hit batch limits local accents to12")
	check(fx.debris.size()<=960,"dense hit batch caps debris960")
	check(fx._last_camera_tick==-100,"ordinary hits do not kick camera")
	var debris_count: int=fx.debris.size()
	fx.consume(events)
	check(fx.debris.size()==debris_count and fx.strokes.size()==12,"effects sequence replay produces no duplicates")
	fx.sync(run,0)
	check(fx.shards.multimesh.visible_instance_count<=960,"rendered shard capacity bounded")
	check(fx.beams.mesh.get_surface_count()==1,"hit accents produce actual bounded mesh surface")
	var life: float=fx.strokes[0].life
	run.mode="paused";fx.sync(run,1.0)
	check(fx.strokes[0].life==life,"paused hit accent age frozen")
	run.mode="playing"
	for i in 20:fx.consume([{"seq":1200+i,"type":"explosion","tick":20+i,"position":Vector2.ZERO,"skill_id":"chapter1.skill.ember","radius_cm":200,"evolved":true}])
	fx.sync(run,0)
	check(fx.strokes.size()<=96 and fx.impacts.multimesh.visible_instance_count<=48 and fx.plumes.multimesh.visible_instance_count<=48,"stroke/impact/plume capacities bounded")
	check(fx._last_camera_tick==34,"camera impulses rate limited to one per14ticks")
	check(all_core(run)==before,"effects including saturated hits do not mutate any core variable")
	fx.sync(run,.6)
	check(fx.strokes.is_empty() and fx.debris.is_empty(),"short hit effects expire")
	fx.reset();check(fx._last_event==-1 and fx._last_camera_tick==-100,"retry clears FX dedup and camera limiter")

func exercise_audio(run: RefCounted) -> void:
	var audio: RefCounted=view.audio
	var before: Variant=all_core(run)
	audio.reset();audio.set_muted(false);audio.set_master_volume(.8);audio.set_paused(false)
	audio.play("step",100);audio.play("fire",100)
	check(audio.voices.size()==13 and audio.voice_gains.size()==13,"audio fixed13voices and per-voice gain slots")
	check(audio.voices[1].playing and audio.voices[2].playing,"two actual active cues for gain regression")
	check(is_equal_approx(audio.voice_gains[1],.38) and is_equal_approx(audio.voice_gains[2],.8),"step/fire retain independent active gains")
	audio.set_muted(true)
	check(audio.voices[1].volume_db==-80 and audio.voices[2].volume_db==-80,"mute attenuates active cues")
	audio.set_master_volume(.5);audio.set_muted(false)
	check(is_equal_approx(db_to_linear(audio.voices[1].volume_db),.5*.11*.38),"unmute/master preserves active step gain")
	check(is_equal_approx(db_to_linear(audio.voices[2].volume_db),.5*.11*.8),"unmute/master preserves active fire gain")
	check(is_equal_approx(db_to_linear(audio.voices[0].volume_db),.5*.025),"ambience retains separate quiet gain")
	audio.set_paused(true)
	check(audio.voices[1].stream_paused and audio.voices[2].stream_paused,"pause retains active voice pause state")
	audio.set_master_volume(.7)
	check(audio.voices[1].stream_paused and audio.voices[2].stream_paused,"master adjustment does not unpause active cues")
	audio.set_paused(false)
	var played: int=audio.played
	audio.play("fire",100)
	check(audio.played==played,"same-tick cue cooldown prevents repeat")
	audio.reset();audio.set_paused(false)
	for i in 20:audio.play("fire",i*20)
	check(audio.voices.slice(11,13).all(func(v):return not v.playing),"ordinary cues preserve two critical voices")
	audio.play("hurt",1000);audio.play("equip",1000)
	check(audio.voices[11].playing and audio.voices[12].playing,"critical cues can use reserved voices")
	check(audio.dropped>0,"saturated audio pool reports drops")
	check(all_core(run)==before,"audio/mute/master/pool saturation never changes core")
	audio.reset()
	check(audio.voices.all(func(v):return not v.playing),"retry stops every voice")
	check(audio.voice_gains.all(func(g):return g==1.0),"retry clears stale cue gains")
	observations.audio="actual AudioStreamPlayer active gain/mute/master/pause/pool checks under headless dummy audio; listening remains unverified"
