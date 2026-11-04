extends "res://chapter1/view/chapter_elements_quality14.gd"
## Actual cold kills have an ice debris beat even when weak enemies die before
## reaching freeze stacks. This is cosmetic death debris, not a freeze/shatter
## damage proc. Only the immediately preceding paid hit's evolved snapshot is
## used, never current gear/rank. Real frozen shatters retain the14 path.
var cold_death_accents := 0
var _cold_death_seq := -1
var _previous_paid_hit: Dictionary={}

func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	print("CHAPTER1_ELEMENTS15 ",JSON.stringify({"cold_death_budget":4,"damage":0,"freeze_added":false,"rank_owner":"immediately preceding actual hit.evolved snapshot","scope":"Own cosmetic evolved-cold death debris, not a gameplay shatter proc"}))

func consume(events: Array) -> void:
	var accents: Array[Dictionary]=[]
	for event in events:
		if int(event.seq)<=_cold_death_seq:continue
		_cold_death_seq=int(event.seq)
		if event.type=="hit":_previous_paid_hit=event
		elif event.type=="death" and event.skill_id=="chapter1.skill.frost" and not _previous_paid_hit.is_empty():
			if int(event.seq)==int(_previous_paid_hit.seq)+1 and int(event.target_id)==int(_previous_paid_hit.target_id) and _previous_paid_hit.skill_id==event.skill_id and _previous_paid_hit.get("evolved",false) and not _previous_paid_hit.get("shatter",false):
				if accents.size()<4:accents.append(event)
	super.consume(events)
	for event in accents:
		if ice_fragments.size()>=ICE_SHARD_CAP:continue
		cold_death_accents+=1
		for i in mini(6,ICE_SHARD_CAP-ice_fragments.size()):
			var angle := float((int(event.seq)*19+i*61)%360)*PI/180.0
			var at: Vector2=event.position
			ice_fragments.append({"position":Vector3(at.x,.70,at.y),"velocity":Vector3(cos(angle)*3.2,2.2+float(i%3)*.6,sin(angle)*3.2),"age":0.0,"duration":.42,"angle":angle,"size":.28+float(i%3)*.07})
		burst(event.position,Color(.65,.92,1),8,.85)
		if strokes.size()<MAX_STROKES:strokes.append({"type":"impact","at":event.position,"radius":1.15,"life":.34,"duration":.34,"element":.5,"color":Color("96ddec")})

func reset() -> void:
	super.reset();cold_death_accents=0;_cold_death_seq=-1;_previous_paid_hit={}
