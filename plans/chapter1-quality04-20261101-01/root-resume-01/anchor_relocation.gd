extends SceneTree
const Run=preload("res://chapter1/core/combat_run.gd")
var checks:=0
var failures:Array[String]=[]
func check(ok:bool,label:String)->void:
	checks+=1
	if not ok:failures.append(label)
func _initialize()->void:
	for state in ["windup","dash","recover","frozen","move"]:
		var run=Run.new()
		check(run.start(71),"start "+state)
		run.enemies.clear()
		run._spawn("walker",Vector2(18,18))
		var e:Dictionary=run.enemies.values()[0]
		e.state="move" if state=="frozen" else state
		e.frozen_until=run.tick+90 if state=="frozen" else 0
		e.telegraph={"origin":e.position,"direction":Vector2.LEFT,"shape":"line","length":6.0,"width":1.0}
		var origin:Vector2=e.position
		var uid:int=e.id
		var telegraph:Dictionary=e.telegraph.duplicate(true)
		run._cleanup()
		check(run.enemies.has(uid),"identity retained "+state)
		if state=="move":
			check(e.position!=origin and e.position.distance_to(run.hero.position)<20,"free moving survivor recycled")
		else:
			check(e.position==origin,"paid or frozen anchor retained "+state)
			check(e.telegraph==telegraph,"telegraph retained "+state)
	check(not OS.get_cmdline_user_args().has("--intentional-fail"),"intentional negative")
	print("ANCHOR_RELOCATION_RESULT ",JSON.stringify({"checks":checks,"failures":failures}))
	quit(0 if failures.is_empty() else 1)
