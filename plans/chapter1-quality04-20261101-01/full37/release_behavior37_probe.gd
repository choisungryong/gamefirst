extends SceneTree
## Explicit mechanical fixture, no profile reads/writes or native visual approval.
const Chapter = preload("res://chapter1/core/chapter_run_quality37.gd")
const World = preload("res://chapter1/view/chapter_world_quality37c.gd")
const Items = preload("res://chapter1/core/chapter_items.gd")
const Policy = preload("res://chapter1/core/chapter_pilot.gd")
var failures: Array[String] = []
var checks := 0
func check(value: bool,message: String) -> void:
	checks += 1
	if not value:failures.append(message)
func _initialize() -> void:call_deferred("execute")
func execute() -> void:
	check(ProjectSettings.get_setting("application/config/custom_user_dir_name","") == "AshenCloisterChapterOneQuality37","release37 explicit continuity destination")
	var run = Chapter.new()
	check(run.start(90131),"release start executes")
	var gear: Dictionary = Items.unique(0,1)
	gear.storage_id = 11
	check(run.import_starting_gear([gear]),"release starting gear import executes")
	check(run.equipped.has("weapon") and run.effective_skill("chapter1.skill.ember").effects.projectiles == 2,"release imported stats applied")
	check(run.growth.award_xp(12),"fixture growth setup")
	run._refresh_mode()
	check(run.mode == "choice","fixture enters choice")
	var policy = Policy.new()
	policy.run = run
	policy.decide()
	check(run.mode == "playing" and run.growth.snapshot().ranks["chapter1.skill.ember"] == 2,"release policy actually chooses growth")
	var ring: Dictionary = Items.unique(2,2)
	ring.uid=99;ring.position=Vector2.ZERO;ring.collected=true;ring.drop_tick=0
	run.inventory.append(ring)
	policy.decide()
	check(run.equipped.get("ring",-1) == 99 and run.mode == "playing","release policy actually opens equips and resumes")
	check(run._spawn("walker",Vector2(4,0)),"release stun target spawned")
	var enemy: Dictionary = run.enemies[run._enemy_sequence]
	enemy.hp_raw = 100000
	var effect: Dictionary = run._catalog.snapshot().skills[2].ranks[0].duplicate(true)
	effect.damage_raw = 1
	var context: Dictionary = {"uid":900,"skill_id":"chapter1.skill.arc","effects":effect,"remaining_hits":8,"hit_ids":[],"evolved":false}
	run._damage_enemy(enemy.id,context,0)
	check(enemy.get("stunned_until",0) == run.tick+18 and enemy.frozen_until == 0,"release shock applies separately from cold")
	var arc = Chapter.new()
	check(arc.start(90131,"chapter1.skill.arc") and arc.growth.award_xp(1640),"pure growth evolution fixture starts")
	for index in 11:
		var offer: Dictionary = arc.growth.next_offer()
		if offer.is_empty():break
		var card: Dictionary = offer.cards[0]
		check(arc.growth.choose(offer.token,card.id),"fixture legal growth choice")
		if card.kind == "evolve":break
	var evolved: Dictionary = arc.growth.effective_skill("chapter1.skill.arc")
	check(evolved.evolved and evolved.name == "세 갈래 폭풍" and evolved.effects.branches == 3,"release actual successor name and three branches")
	var owner = Node3D.new()
	root.add_child(owner)
	var world = World.new()
	world.setup(owner)
	for label in ["RearMasonry22","RearArches22"]:
		var node: MultiMeshInstance3D = world.root.get_node(NodePath(label))
		check(node.material_override is ShaderMaterial and node.material_override.shader.resource_path == "res://chapter1/view/chapter_masonry_quality37c.gdshader",label+" actual successor shader dependency")
		check(node.material_override.get_shader_parameter("flagstone") is Texture2D and node.material_override.get_shader_parameter("soil") is Texture2D,label+" imported existing textures")
	policy.run=null
	world.root=null
	owner.queue_free()
	for index in 4:await process_frame
	owner=null;world=null;run=null;arc=null;policy=null
	print("RELEASE_BEHAVIOR_PROBE ",JSON.stringify({"checks":checks,"failures":failures,"scope":"Packaged37 explicit resource/evolution/world material fixture; no profiles/GPU/manual/normal victory/audio/performance approval"}))
	quit(0 if failures.is_empty() else 1)
