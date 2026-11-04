extends SceneTree
const Chapter=preload("res://chapter1/core/chapter_run.gd")
const Items=preload("res://chapter1/core/chapter_items.gd")
var failures: Array[String]=[]
var checks := 0
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);push_error(message)
func _initialize() -> void:
	call_deferred("execute")
func context(run: RefCounted,amount: int) -> Dictionary:
	var effects: Dictionary=run.effective_skill("chapter1.skill.ember").effects.duplicate(true)
	effects.damage_raw=amount;effects.death_burst=0;effects.shatter_count=0
	return {"uid":123,"skill_id":"chapter1.skill.ember","effects":effects,"remaining_hits":128,"hit_ids":[],"evolved":false}
func execute() -> void:
	var rng := RandomNumberGenerator.new();rng.seed=672384
	var seen := {};var groups_ok := true;var valid := true
	for i in 12000:
		var level := 1+i%12
		var quality: String=["common","magic","rare"][i%3]
		var item: Dictionary=Items.roll(rng,level,quality)
		seen[item.base_id]=true;valid=valid and Items.validate(item).is_empty()
		var groups: Array=[]
		for a in item.affixes:
			groups_ok=groups_ok and not a.group in groups;groups.append(a.group)
	check(valid,"12000 bounded/eligible item rolls")
	check(groups_ok,"Affix group exclusion")
	check(seen.size()==12,"All12 bases reachable")
	for i in 3:check(Items.validate(Items.unique(i,12)).is_empty(),"Unique validates "+str(i))
	var forged := Items.unique(0,5);forged.stats.projectiles=200
	check(not Items.validate(forged).is_empty(),"Forged stat bound rejected")
	var first := Chapter.new();check(first.start(71),"Chapter config")
	check(first._clamp_point(Vector2(30,0)).x==19,"Next zone locked")
	check(first._clamp_point(Vector2(-25,0)).x==-19,"First western bound")
	first.tick=70*60;first.step()
	check(first.mode=="playing" and first._champion_id==-1,"Old70seconds is not full chapter win/spawn")
	check(not first.drink_potion() and first.potions==3,"No potion wasted at full HP")
	first.hero.hp_raw=60*256
	check(first.drink_potion() and first.potions==2 and first.hero.hp_raw==102*256,"Manual35percent potion")
	check(not first.drink_potion() and first.potions==2,"Potion cooldown")
	first.set_paused(true);first.tick+=4*60
	check(not first.drink_potion(),"Potion forbidden while paused")
	first.set_paused(false)
	check(not first.activate_ritual("vigil"),"Ritual proximity required")
	first.hero.position=Vector2(8,-7)
	check(first.activate_ritual("vigil") and not first.activate_ritual("vigil"),"Ritual one start")
	first.rituals.vigil.progress=25*60-1;first._step_rituals()
	check(first.rituals.vigil.state=="completed","Hold ritual completes actual last hold step")
	var reward_count := first.inventory.size();first._step_rituals()
	check(first.inventory.size()==reward_count,"Trial reward one time")
	# Fixture accelerates objectives, not a normal-run duration/skill proof.
	var run := Chapter.new();check(run.start(90131),"Fresh objective fixture")
	for z in 3:
		run.hero.position=Chapter.ZONES[z];run._zone_entered=true;run.zone_kills=Chapter.SEAL_KILLS[z]
		run._spawn_wave()
		var champion: int=run._champion_id
		check(champion>0 and run.enemies.has(champion),"Champion exists zone "+str(z))
		check(run.mode=="playing","Spawn never wins zone "+str(z))
		if z==2:
			var boss: Dictionary=run.enemies[champion]
			run._damage_enemy(champion,context(run,int(boss.max_hp_raw)/2),0)
			run._step_chapter_hazards()
			check(run._boss_phase==2,"Boss phase changes from actual damage")
			run._next_ward=run.tick;run._step_chapter_hazards()
			check(run.chapter_hazards.size()==3,"Phase2 three paid warning circles")
			var h: Dictionary=run.chapter_hazards[0];run.hero.position=h.position
			var hp_before: int=run.hero.hp_raw
			run.tick=h.expires-1;run._step_chapter_hazards()
			check(run.hero.hp_raw==hp_before,"Ward no early damage")
			run._next_ward=run.tick+999;run.tick+=1;run._step_chapter_hazards()
			check(run.hero.hp_raw==hp_before-20*256,"Ward damage matches1.8m circle at warning expiry")
			check(run.mode=="playing","Nonlethal ward continues")
			run._next_ward=run.tick;run._step_chapter_hazards();run.hero.position=Vector2(100,10)
			hp_before=run.hero.hp_raw;run.tick+=72;run._next_ward=run.tick+999;run._step_chapter_hazards()
			check(run.hero.hp_raw==hp_before,"Outside paid circles receives no ward damage")
		run._damage_enemy(champion,context(run,100000000),0)
		if z<2:
			check(run.zone==z+1 and run.mode=="playing","Actual champion kill opens next zone "+str(z))
			check(run._clamp_point(Chapter.ZONES[z+1])==Chapter.ZONES[z+1],"Unlocked next courtyard")
			check(run._clamp_point(Vector2(24+48*z,8)).y==3.6,"Corridor restricts width")
			check(not run._zone_entered,"Next objective requires actual visit")
		else:
			check(run.mode=="victory" and run.seals[2].cleared,"Only actual final boss kill wins")
			check(run.chapter_hazards.is_empty(),"No paid hazards after boss victory")
			check(run.inventory[-1].quality=="unique" and run._elite_reward_uid>0,"Owned final unique reward")
			var owned := run.inventory.size();run._damage_enemy(champion,context(run,1000000),0)
			check(run.inventory.size()==owned,"No duplicate boss reward")
	check(run.start(72) and run.zone==0 and run.potions==3 and run.history.size()==1 and run.pending_rewards.is_empty(),"Retry clears chapter state")
	if "--negative" in OS.get_cmdline_user_args():check(false,"Intentional checker failure")
	print("CHAPTER_FULL_TEST ",JSON.stringify({"checks":checks,"failures":failures,"scope":"Fixtures and12000 item rolls; not normal-run pacing or visual approval"}))
	quit(0 if failures.is_empty() else 1)
