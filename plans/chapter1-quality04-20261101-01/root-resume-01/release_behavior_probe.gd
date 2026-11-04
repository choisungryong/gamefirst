extends SceneTree
## Deliberate mechanical fixture, not normal gameplay. Never uses assert for calls.
const Chapter=preload("res://chapter1/core/chapter_run.gd")
const Items=preload("res://chapter1/core/chapter_items.gd")
const Policy=preload("res://chapter1/core/chapter_pilot.gd")
var failures: Array[String]=[]
var checks := 0
func check(value: bool,message: String) -> void:
	checks+=1
	if not value:failures.append(message)
func _initialize() -> void:call_deferred("execute")
func execute() -> void:
	var run=Chapter.new()
	check(run.start(90131),"release start executes")
	var gear: Dictionary=Items.unique(0,1);gear.storage_id=11
	check(run.import_starting_gear([gear]),"release starting gear import executes")
	check(run.equipped.has("weapon") and run.effective_skill("chapter1.skill.ember").effects.projectiles==2,"release imported stats applied")
	check(run.growth.award_xp(12),"fixture growth setup")
	run._refresh_mode();check(run.mode=="choice","fixture enters choice")
	var policy=Policy.new();policy.run=run
	policy.decide()
	check(run.mode=="playing" and run.growth.snapshot().ranks["chapter1.skill.ember"]==2,"release policy actually chooses growth")
	var ring: Dictionary=Items.unique(2,2);ring.uid=99;ring.position=Vector2.ZERO;ring.collected=true;ring.drop_tick=0
	run.inventory.append(ring);policy.decide()
	check(run.equipped.get("ring",-1)==99 and run.mode=="playing","release policy actually opens and equips then resumes")
	print("RELEASE_BEHAVIOR_PROBE ",JSON.stringify({"checks":checks,"failures":failures,"scope":"Explicit resource fixture; not normal gameplay, pacing, profile file IO, visuals or performance"}))
	quit(0 if failures.is_empty() else 1)
