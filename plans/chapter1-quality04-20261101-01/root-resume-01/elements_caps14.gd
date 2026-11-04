extends "res://chapter1/chapter_one_view.gd"
var checks := 0
var failures: Array[String]=[]
func _physics_process(_delta: float) -> void:pass
func _process(_delta: float) -> void:pass
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);push_error("ELEMENTS_CAP_FAILED "+message)
func _ready() -> void:
	super._ready();call_deferred("probe")
func probe() -> void:
	run.enemies.clear();effects.reset()
	for i in 120:
		run._spawn("walker",Vector2(float(i%12)-6,float(i/12)-5));var e: Dictionary=run.enemies[run._enemy_sequence];e.frozen_until=600
	run._spawn("elite",Vector2(10,10));var elite: Dictionary=run.enemies[run._enemy_sequence];elite.frozen_until=600
	var baseline := JSON.stringify(run.snapshot())
	var events: Array=[]
	for i in 100:events.append({"seq":i+1,"tick":0,"type":"cast","skill_id":"chapter1.skill.arc","position":Vector2.ZERO,"targets":[Vector2(2,0),Vector2(4,1),Vector2(5,2)],"evolved":true})
	for i in 30:events.append({"seq":i+101,"tick":0,"type":"shatter","skill_id":"chapter1.skill.frost","position":Vector2(2,0),"radius_cm":350,"count":5,"evolved":true})
	effects.consume(events)
	check(effects.arc_links.size()==64,"burst link capacity64")
	check(effects.ice_fragments.size()==48,"consume budget8 shatters times6")
	var first := [effects.arc_links.size(),effects.ice_fragments.size(),effects.debris.size(),effects.strokes.size()]
	effects.consume(events)
	check(first==[effects.arc_links.size(),effects.ice_fragments.size(),effects.debris.size(),effects.strokes.size()],"same event batch cannot replay new or inherited effects")
	effects.sync(run,.05)
	check(effects.ice_batch.multimesh.visible_instance_count==96,"max24 frozen targets times4 crystals")
	check(effects.ice_targets.has("%d:%d"%[elite.generation,elite.id]),"distant frozen elite retained ahead of normal targets")
	check(effects.ice_targets.size()<=48,"state record capacity")
	check(JSON.stringify(run.snapshot())==baseline,"presenter never mutates combat snapshot")
	var link_age: float=effects.arc_links[0].age;var shard_position: Vector3=effects.ice_fragments[0].position
	run.mode="paused";effects.sync(run,1.0)
	check(effects.arc_links[0].age==link_age,"pause keeps arc age")
	check(effects.ice_fragments[0].position==shard_position,"pause keeps shatter motion")
	run.mode="playing";effects.sync(run,1.0)
	check(effects.arc_links.is_empty()and effects.ice_fragments.is_empty(),"resume expires short arc/shatter effects")
	for e in run.enemies.values():e.frozen_until=0
	effects.sync(run,.2)
	check(effects.ice_targets.is_empty()and effects.ice_batch.multimesh.visible_instance_count==0,"thawed records/geometry disappear")
	effects.reset()
	check(effects.arc_links.is_empty()and effects.ice_targets.is_empty()and effects.ice_fragments.is_empty(),"reset clears element state")
	check(effects.ice_fragment_batch.multimesh.visible_instance_count==0 and effects.arc_surface.mesh==null,"reset clears rendered batches")
	var result := {"checks":checks,"failures":failures,"scope":"Synthetic renderer capacity/dedupe/pause/thaw/reset/core-nonmutation probe, not normal gameplay or art/performance approval"}
	var file := FileAccess.open("res://caps-result.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close();print("ELEMENTS_CAP_RESULT ",JSON.stringify(result))
	audio.reset()
	# Match production shutdown: unpause stopped voices, then allow the actual
	# mixing thread to release playback, independent of simulated timer speed.
	var release_at := Time.get_ticks_usec()+200000
	while Time.get_ticks_usec()<release_at:await get_tree().process_frame
	for voice in audio.voices:voice.stop();voice.stream=null
	audio.voices.clear();audio.streams.clear();audio.ambience=null
	await get_tree().create_timer(.2).timeout
	get_tree().quit(0 if failures.is_empty()else 1)
