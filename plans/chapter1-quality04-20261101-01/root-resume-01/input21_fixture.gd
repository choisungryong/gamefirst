extends "res://chapter1/chapter_one_input21.gd"
var checks: Dictionary={}
var cases: Array[Dictionary]=[]
func _ready() -> void:
	super._ready();set_process(false);set_physics_process(false)
	var baseline: Dictionary=run.snapshot().duplicate(true)
	var original_zone: int=run.zone
	var hero_position: Vector2=run.hero.position
	var failures_before := 0
	for zone_ in 3:
		run.zone=zone_;run.hero.position=run.ZONES[zone_]
		world.update_camera(run.hero.position,10)
		for offset in [Vector2(3,-2),Vector2(-4,3),Vector2(25,8)]:
			var target: Vector2=run.ZONES[zone_]+offset
			var expected: Vector2=run._clamp_point(target)
			var event := InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_LEFT;event.pressed=true;event.position=world.camera.unproject_position(Vector3(target.x,0,target.y))
			_unhandled_input(event)
			var actual: Vector2=_move_target
			checks["zone%d_%s"%[zone_,str(offset)]]=actual.distance_to(expected)<.025
			var before: Vector2=target.clamp(Vector2.ONE*-18.8,Vector2.ONE*18.8)
			if before.distance_to(expected)>.025:failures_before+=1
			cases.append({"zone":zone_,"target":target,"expected":expected,"actual":actual,"legacy_target":before})
		run.mode="inventory";var held: Vector2=_move_target
		var blocked := InputEventMouseButton.new();blocked.button_index=MOUSE_BUTTON_LEFT;blocked.pressed=true;blocked.position=Vector2(100,100)
		_unhandled_input(blocked);checks["zone%d_inventory_ignored"%zone_]=_move_target==held
		run.mode="playing"
	run.zone=original_zone;run.hero.position=hero_position;_has_move_target=false
	checks.full_core_restored=baseline==run.snapshot()
	checks.legacy_failed_later_zones=failures_before>=6
	var f := FileAccess.open("res://input21-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"cases":cases,"legacy_failures":failures_before,"scope":"Synthetic unlocked-zone/camera projection/input-event fixture; original complete core restored. No native/manual/fullrun claim."},"\t"));f.close()
	var failed := false
	for value in checks.values():if not value:failed=true
	audio.reset()
	call_deferred("_finish_input21",1 if failed else 0)
func _finish_input21(code: int) -> void:
	for i in 4:await get_tree().process_frame
	get_tree().quit(code)
