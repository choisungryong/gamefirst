extends "res://chapter1/view/chapter_actors_quality12.gd"
## Presentation only: cold-killed ordinary bodies yield to the .48s ice shards.
const COLD_CORPSE_SECONDS := .22
var _cold_corpses: Dictionary={}
var _cold_event := -1

func consume(events: Array) -> void:
	for event in events:
		if int(event.get("seq",-1))<=_cold_event:continue
		_cold_event=int(event.seq)
		if event.type!="death" or event.get("skill_id","")!="chapter1.skill.frost":continue
		var entity: Dictionary=view.run.enemies.get(event.target_id,{})
		if entity.is_empty() or entity.hp_raw>0 or entity.elite or entity.kind=="elite":continue
		var key := "%d:%d"%[entity.generation,entity.id]
		_cold_corpses[key]={"age":0.0,"tick":int(entity.dead_tick)}
	super.consume(events)

func sync(run: RefCounted,delta: float) -> void:
	# Parent recomputes sprite tint/owner fade from source every sync. Apply once
	# afterwards, never multiply the preceding frame's cold tint.
	super.sync(run,delta)
	for key in _cold_corpses.keys():
		if not actors.has(key):_cold_corpses.erase(key);continue
		var actor: Node3D=actors[key]
		if not actor.has_meta("sprite"):continue
		var record: Dictionary=_cold_corpses[key]
		if run.mode not in ["paused","choice","inventory","equipment"]:
			record.age=maxf(float(record.age)+maxf(0,delta),float(run.tick-int(record.tick))/60.0)
		var sprite: AnimatedSprite3D=actor.get_meta("sprite")
		var tint := Color(.48,.86,1.16)
		tint.a=sprite.modulate.a*(1.0-smoothstep(.025,COLD_CORPSE_SECONDS,float(record.age)))
		sprite.modulate=tint

func reset() -> void:
	super.reset();_cold_corpses.clear();_cold_event=-1
