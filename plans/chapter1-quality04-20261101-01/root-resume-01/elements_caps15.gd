extends "res://chapter1/chapter_one_view.gd"
var checks := 0
var failures: Array[String]=[]
func _physics_process(_delta: float) -> void:pass
func _process(_delta: float) -> void:pass
func _ready() -> void:
	super._ready();call_deferred("probe")
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);push_error("COLD_DEATH15_FAILED "+message)
func pair(seq: int,evolved: bool=true,shatter: bool=false,hit_skill: String="chapter1.skill.frost",death_skill: String="chapter1.skill.frost",target: int=1,gap: int=1) -> Array:
	return [{"seq":seq,"tick":0,"type":"hit","target_id":1,"position":Vector2(3,0),"skill_id":hit_skill,"damage_raw":1,"evolved":evolved,"frozen":false,"shatter":shatter},{"seq":seq+gap,"tick":0,"type":"death","target_id":target,"position":Vector2(3,0),"skill_id":death_skill,"kind":"walker","elite":false}]
func probe() -> void:
	var baseline := JSON.stringify(run.snapshot())
	var paid := pair(1);effects.consume(paid)
	check(effects.cold_death_accents==1 and effects.ice_fragments.size()==6,"paid evolved-cold kill emits one cosmetic accent")
	effects.consume(paid);check(effects.cold_death_accents==1 and effects.ice_fragments.size()==6,"replay cannot duplicate death debris")
	effects.reset();check(effects.cold_death_accents==0 and effects.ice_fragments.is_empty(),"retry reset clears counter/debris")
	effects.consume(pair(3,false));check(effects.cold_death_accents==0 and effects.ice_fragments.is_empty(),"un-evolved hit does not borrow current evolved rank")
	effects.consume(pair(5,true,true));check(effects.cold_death_accents==0 and effects.ice_fragments.is_empty(),"actual frozen-shatter hit does not duplicate cold death accent")
	effects.consume([{"seq":7,"tick":0,"type":"shatter","position":Vector2(3,0),"skill_id":"chapter1.skill.frost","radius_cm":350,"count":5,"evolved":true}]);check(effects.ice_fragments.size()==6,"real shatter keeps inherited14 chunks")
	effects.reset();effects.consume(pair(8,true,false,"chapter1.skill.frost","chapter1.skill.frost",2));check(effects.cold_death_accents==0,"wrong target rejected")
	effects.consume(pair(10,true,false,"chapter1.skill.frost","chapter1.skill.frost",1,2));check(effects.cold_death_accents==0,"unpaired sequence rejected")
	effects.consume(pair(13,true,false,"chapter1.skill.arc","chapter1.skill.arc"));check(effects.cold_death_accents==0,"arc kill is not cold debris")
	effects.consume(pair(15,true,false,"chapter1.skill.arc","chapter1.skill.frost"));check(effects.cold_death_accents==0,"wrong paid skill rejected")
	effects.reset();var rows: Array=[]
	for i in 80:rows.append_array(pair(100+i*2))
	effects.consume(rows);check(effects.cold_death_accents==4 and effects.ice_fragments.size()==24,"dense cold deaths obey consume4 and shared fragment cap")
	check(JSON.stringify(run.snapshot())==baseline,"cosmetic death accents change no combat state")
	var result := {"checks":checks,"failures":failures,"scope":"Synthetic source15 paid-hit/death snapshot/identity/dedupe/budget/reset/core-nonmutation probe; no damage or freeze granted, not normal gameplay/art/performance approval"}
	print("COLD_DEATH15_PROBE ",JSON.stringify(result))
	var file := FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/elements15/caps01/result.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close()
	audio.reset();var release_at := Time.get_ticks_usec()+200000
	while Time.get_ticks_usec()<release_at:await get_tree().process_frame
	for voice in audio.voices:voice.stop();voice.stream=null
	audio.voices.clear();audio.streams.clear();audio.ambience=null
	get_tree().quit(0 if failures.is_empty()else 1)
