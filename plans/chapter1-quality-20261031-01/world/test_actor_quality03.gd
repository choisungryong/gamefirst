extends SceneTree
var checks := 0
var failures: Array[String]=[]
func check(value: bool, label: String) -> void:
	checks+=1
	if not value:failures.append(label)
func _initialize() -> void:call_deferred("_run")
func _run() -> void:
	var view := Node3D.new();root.add_child(view)
	var world=load("res://chapter1/view/cloister_world.gd").new();world.setup(view)
	var actors=load("res://chapter1/view/cloister_actors.gd").new();actors.setup(view)
	var run=load("res://chapter1/core/combat_run.gd").new();check(run.start(90131),"real core starts")
	run.step(Vector2.ZERO)
	var before := JSON.stringify(run.snapshot())
	actors.consume([{"type":"cast","tick":run.tick,"direction":Vector2.RIGHT}])
	actors.sync(run,1.0/60)
	check(JSON.stringify(run.snapshot())==before,"actor casting presentation never writes core state")
	check(actors.sprite_definitions.hero.get("directional_cast",false),"all four authored directional casts are available")
	var sprite: AnimatedSprite3D=actors.hero.get_meta("sprite")
	check(sprite.animation=="cast_east","moving release follows the paid attack direction")
	check(sprite.frame==2 and sprite.speed_scale==0,"brief moving release holds the authored release pose")
	run.tick+=7
	before=JSON.stringify(run.snapshot());actors.sync(run,1.0/60)
	check(sprite.animation=="cast_east","planted cast retains paid direction after the brief traveling window")
	check(JSON.stringify(run.snapshot())==before,"standing cast presentation never writes core state")
	var chosen: Dictionary={}
	for e in run.enemies.values():
		if e.hp_raw>0:chosen=e;break
	check(not chosen.is_empty(),"fixture has an actual live spawned enemy")
	if not chosen.is_empty():
		# Synthetic presentation boundary fixture, not normal-play evidence.
		chosen.direction=Vector2.RIGHT;chosen.state="move"
		actors.consume([{"type":"hit","tick":run.tick,"position":chosen.position,"target_id":chosen.id}])
		run.tick+=3;before=JSON.stringify(run.snapshot());actors.sync(run,1.0/60)
		var actor: Node3D=actors.actors["%d:%d" % [chosen.generation,chosen.id]]
		var distance: float=actor.position.distance_to(Vector3(chosen.position.x,0,chosen.position.y))
		check(distance>0 and distance<=.07501,"cosmetic recoil is visible and bounded below the .30m minimum core radius")
		check(JSON.stringify(run.snapshot())==before,"visual recoil leaves every core field unchanged")
		var enemy_sprite: AnimatedSprite3D=actor.get_meta("sprite")
		check(enemy_sprite.animation=="move_east","legacy hurt strip does not rotate an east-facing traveler south")
		run.mode="paused";actors.sync(run,1.0/60)
		check(enemy_sprite.speed_scale==0 and sprite.speed_scale==0,"modal pause freezes actor animation playback")
		run.mode="playing";chosen.hp_raw=0;chosen.state="dead";chosen.dead_tick=run.tick
		actors.sync(run,1.0/60)
		check(actor.scale==Vector3.ONE,"dead actor keeps authored scale instead of shrinking")
		run.tick+=55;actors.sync(run,1.0/60)
		check(enemy_sprite.modulate.a>0 and enemy_sprite.modulate.a<1,"collapsed corpse fades before bounded core cleanup")
	actors.reset()
	check(actors._enemy_recoil.is_empty() and actors._cast_moving_until<0,"retry clears presentation state")
	if OS.get_cmdline_user_args().has("--prove-failure"):check(false,"intentional fixture failure")
	print("ACTOR_QUALITY03_TEST ",JSON.stringify({"checks":checks,"failures":failures,"scope":"Headless synthetic presentation boundaries; not normal gameplay or animation quality approval"}))
	actors.view=null;actors=null;world.root=null;world=null;run=null;view.free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
