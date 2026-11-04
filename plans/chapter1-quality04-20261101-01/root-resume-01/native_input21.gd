extends SceneTree
var view: Node
var probe: Node
var phase := 0
var records: Array[Dictionary]=[]
class InputProbe extends Node:
	var owner21: SceneTree
	var pending := false
	var at := Vector2.ZERO
	func _input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT and event.pressed:
			at=event.position;pending=true
		if event is InputEventKey and event.pressed and not event.echo and event.keycode==KEY_F8:owner21.call_deferred("_next_phase21")
	func _physics_process(_delta: float) -> void:
		if not pending:return
		pending=false;owner21._record_click21(at)
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view);view.set_physics_process(false)
	probe=InputProbe.new();probe.owner21=self;probe.process_physics_priority=100;root.add_child(probe)
	view.tree_exiting.connect(_save21);_next_phase21()
func _next_phase21() -> void:
	if phase>=2:return
	phase+=1
	if phase>1:view.start_run("chapter1.skill.frost")
	var target := 9000 if phase==1 else 16000
	while view.run.tick<target:view.run.step(view.full_pilot.decide())
	view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view._has_move_target=false
	view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.hud.sync(view.run,0)
	DisplayServer.window_set_title("후보21 실제 클릭 검수 · 구역%d · F8 다음"%(view.run.zone+1))
	print("NATIVE21_INPUT_READY ",JSON.stringify({"phase":phase,"zone":view.run.zone,"tick":view.run.tick,"hero":view.run.hero.position,"physics_stopped_fixture":true,"instruction":"Click visible ground. After verified movement pressF8 for next zone."}))
	_capture21("zone%d-before.png"%view.run.zone)
func _record_click21(at: Vector2) -> void:
	if view.run.mode!="playing":return
	var camera: Camera3D=view.world.camera
	var ground: Variant=Plane(Vector3.UP,0).intersects_ray(camera.project_ray_origin(at),camera.project_ray_normal(at))
	if not ground is Vector3:return
	var requested := Vector2(ground.x,ground.z)
	var expected: Vector2=view.run._clamp_point(requested)
	var selected: Vector2=view._move_target
	var before: Vector2=view.run.hero.position
	var correct: bool=view._has_move_target and selected.distance_to(expected)<.05
	if correct:
		for i in 30:
			view.run.step(view._move_input());view._consume_events()
	var after: Vector2=view.run.hero.position
	var toward: Vector2=(expected-before).normalized()
	var row := {"phase":phase,"zone":view.run.zone,"event_position":at,"requested":requested,"expected":expected,"selected":selected,"before":before,"after":after,"correct_target":correct,"moved_toward":(after-before).dot(toward)>.2,"legacy_target":requested.clamp(Vector2.ONE*-18.8,Vector2.ONE*18.8),"scope":"Actual native click then30normal core/controller steps in stopped-physics QA fixture; no automated pilot/manual-fullrun claim."}
	records.append(row);print("NATIVE21_CLICK ",JSON.stringify(row));_capture21("zone%d-click%d.png"%[view.run.zone,records.size()])
func _capture21(name_: String) -> void:
	await process_frame;await RenderingServer.frame_post_draw
	view._capture_file(name_)
func _save21() -> void:print("NATIVE21_INPUT_FINAL ",JSON.stringify({"records":records,"scope":"Actual package21/native clicks in normal earned checkpoint fixtures, no default save/manual-fullrun/performance claim."}))
