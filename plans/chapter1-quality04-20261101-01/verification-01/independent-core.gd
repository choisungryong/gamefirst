extends SceneTree
const Run=preload("res://chapter1/core/combat_run.gd")
var checks:=0
var failures:Array[String]=[]
var observations:Array=[]
func check(ok:bool,label:String)->void:
	checks+=1
	if not ok:failures.append(label)
func make_run(corner:Vector2, reverse_order:bool)->RefCounted:
	var r=Run.new();r.start(71)
	r.enemies.clear();r._enemy_sequence=0;r.events.clear();r._next_spawn=1000000
	r.hero.position=corner
	for i in 40:
		var p:=corner-Vector2(signf(corner.x),signf(corner.y))*1.2
		p+=Vector2(signf(corner.x)*float(i%5)*.05,signf(corner.y)*float(i/5)*.05)
		r._spawn("walker",p)
	if reverse_order:
		var ids:Array=r.enemies.keys();ids.reverse()
		var reordered:Dictionary={}
		for id_ in ids:reordered[id_]=r.enemies[id_]
		r.enemies=reordered
	return r
func _initialize()->void:
	for corner in [Vector2(19,19),Vector2(-19,19),Vector2(19,-19),Vector2(-19,-19)]:
		var a=make_run(corner,false);var b=make_run(corner,true)
		var rng_before:Array=[a._spawn_rng.state,a._loot_rng.state]
		var max_step:=0.0;var finite_bounds:=true;var equal_states:=true
		var first_damage_tick:=-1
		for tick in 1200:
			var positions:Dictionary={}
			for id_ in a.enemies:positions[id_]=a.enemies[id_].position
			a.tick+=1;b.tick+=1;a._step_enemies();b._step_enemies()
			for id_ in a.enemies:
				var p:Vector2=a.enemies[id_].position
				max_step=maxf(max_step,p.distance_to(positions[id_]))
				finite_bounds=finite_bounds and p.is_finite() and absf(p.x)<=19.000001 and absf(p.y)<=19.000001
				if a.enemies[id_]!=b.enemies[id_]:equal_states=false
			if first_damage_tick<0 and a.hero.hp_raw<120*256:first_damage_tick=a.tick
		check(first_damage_tick>0 and first_damage_tick<=1200,"all rotated compressed queues can deliver actual damage "+str(corner))
		check(a.metrics.enemy_attacks>0,"real telegraphed attacks execute "+str(corner))
		check(finite_bounds,"finite geometry remains bounded "+str(corner))
		check(max_step<=1.6/60.0+.045+.00001,"per-tick displacement bounded "+str(corner))
		check(equal_states and a.hero==b.hero,"whole 20s enemy state independent of insertion order "+str(corner))
		check(a.metrics.crowd_peak_neighbors<=32,"40-body queue respects 32-neighbor ceiling "+str(corner))
		check(rng_before==[a._spawn_rng.state,a._loot_rng.state],"steering and enemy attacks do not consume reward/spawn RNG "+str(corner))
		check(a.kills==0 and a.orbs.is_empty() and a.items.is_empty() and a.inventory.is_empty(),"queue simulation cannot generate player rewards "+str(corner))
		observations.append({"corner":str(corner),"first_damage_tick":first_damage_tick,"enemy_attacks":a.metrics.enemy_attacks,"hp_raw":a.hero.hp_raw,"max_step":max_step,"peak_neighbors":a.metrics.crowd_peak_neighbors})
	if "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional independent verifier failure")
	print("QUALITY04_INDEPENDENT_CORE ",JSON.stringify({"checks":checks,"failures":failures,"observations":observations,"scope":"synthetic rotated compressed queues; no gameplay balance approval"}))
	quit(0 if failures.is_empty() else 1)
