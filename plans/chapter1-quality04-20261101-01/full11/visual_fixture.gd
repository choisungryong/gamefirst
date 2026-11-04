extends "res://chapter1/chapter_one_view.gd"
## Explicit visual placement/pose fixture, not normal combat or performance.
var shots := {}
var checks := 0
var capture_root := "res://plans/chapter1-quality04-20261101-01/full11/visual-fixture/captures"
func check(ok: bool,label_: String) -> void:
	checks+=1
	if not ok:push_error("VISUAL_FIXTURE_FAILED "+label_);get_tree().quit(1)

func _ready() -> void:
	super._ready();world.camera.size=8
	actors._phase=.3;actors._render_playing=false;actors._render_delta=0
	actors._update_pose(actors.hero,Vector2.DOWN,true,false,false,500,false)
	var locomotion: Array[Transform3D]=[]
	for i in actors.rig_skeleton.get_bone_count():locomotion.append(actors.rig_skeleton.get_bone_pose(i))
	actors._cast_tick=500
	actors._update_pose(actors.hero,Vector2.DOWN,true,true,false,500,false)
	var lower: Array[String]=[];var changed_upper := 0
	for i in locomotion.size():
		var same: bool=locomotion[i].is_equal_approx(actors.rig_skeleton.get_bone_pose(i))
		if not actors._upper.has(i):
			check(same,"cast preserves lower "+actors.rig_skeleton.get_bone_name(i));lower.append(actors.rig_skeleton.get_bone_name(i))
		elif not same:changed_upper+=1
	check(changed_upper>0,"cast actually changes upper body")
	actors._render_delta=.1
	for i in 10:actors._update_pose(actors.hero,Vector2.DOWN,true,true,false,500,false)
	check(is_equal_approx(actors._phase,.3),"pause freezes gait phase")
	var seq_ := 0
	for batch in 20:
		var synthetic: Array=[]
		for i in 12:
			seq_+=1;synthetic.append({"seq":seq_,"type":"hit","position":Vector2.ZERO,"target_id":i,"tick":1,"skill_id":"chapter1.skill.ember"})
		effects.consume(synthetic)
		if batch==0:
			check(effects.contacts.size()==8,"eight contact accents per consume")
			effects.consume(synthetic);check(effects.contacts.size()==8,"replayed seq does not add accents")
	check(effects.contacts.size()==96,"bounded contact pool")
	effects.reset();check(effects.contacts.is_empty(),"retry clears contact pool")
	actors.reset();check(is_zero_approx(actors._phase),"retry resets phase")
	print("RIG_VISUAL_CHECKS ",JSON.stringify({"checks":checks,"lower_bones":lower,"changed_upper":changed_upper,"scope":"Actual skeleton pose and presentation bounds; not art approval"}))
	run.enemies.clear();run.projectiles.clear();run.orbs.clear();run.items.clear()
	run.hero.position=Vector2.ZERO;run.hero.direction=Vector2.DOWN
	run._spawn("walker",Vector2(1,1));run.events.clear()

func _physics_process(_delta: float) -> void:
	run.tick+=1
	var nearer := Vector2(world.camera.global_basis.z.x,world.camera.global_basis.z.z).normalized()
	var right := Vector2(world.camera.global_basis.x.x,world.camera.global_basis.x.z).normalized()
	var phase := mini(4,int(_wall_age/1.5))
	var e: Dictionary=run.enemies.values()[0]
	e.position=-nearer*.9 if phase==0 else nearer*.8+(right*2.3 if phase==2 else Vector2.ZERO)
	e.state="recover";e.direction=Vector2.DOWN
	if phase==4:e.hp_raw=0;e.dead_tick=run.tick-60
	actors.consume([])

func _process(delta: float) -> void:
	super._process(delta)
	var phase := mini(4,int(_wall_age/1.5))
	if actors.actors.is_empty():return
	var sprite: AnimatedSprite3D=actors.actors.values()[0].get_meta("sprite")
	if phase==3:sprite.modulate.a=1
	if not shots.has(phase) and fmod(_wall_age,1.5)>.65:
		shots[phase]=true
		if phase in [0,2,3]:check(sprite.modulate.a>.99,"uncovered/control remains opaque")
		elif phase==1:check(sprite.modulate.a>.30 and sprite.modulate.a<.36,"foreground enemy fades")
		elif phase==4:check(sprite.modulate.a>.35 and sprite.modulate.a<.45,"corpse fade is preserved")
		DirAccess.make_dir_recursive_absolute(capture_root)
		await RenderingServer.frame_post_draw
		var path := capture_root.path_join("phase-%d.png"%phase)
		if not FileAccess.file_exists(path):get_viewport().get_texture().get_image().save_png(path)
		print("RIG_FOREGROUND_FIXTURE ",JSON.stringify({"phase":phase,"overlap":actors._hero_overlapped,"enemy_alpha":sprite.modulate.a,"checks":checks,"scope":"Zoom8 placement fixture; no normal combat or performance claim"}))
