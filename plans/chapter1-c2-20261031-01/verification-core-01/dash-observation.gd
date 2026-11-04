extends SceneTree
const Run = preload("res://chapter1/core/combat_run.gd")
func _initialize() -> void:
	var r = Run.new()
	r.start(71)
	r.enemies.clear()
	r._next_spawn = 999999
	r._rebuild_grid()
	var accepted: bool = r.request_dash(Vector2.RIGHT)
	var moved: Array[int] = []
	for i in 12:
		var before: Vector2 = r.hero.position
		r.step(Vector2.ZERO)
		if r.hero.position != before: moved.append(r.tick)
	print("DASH_CONTRACT_OBSERVATION ",JSON.stringify({"accepted":accepted,"moving_step_ticks":moved,"distance":r.hero.position.x,"contract":"request_dash promises12 tick movement; measurement is steps after request at tick0","scope":"observational fixture; no automatic defect severity"}))
	quit(0)
