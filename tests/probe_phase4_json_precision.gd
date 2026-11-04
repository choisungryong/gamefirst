extends SceneTree
func _initialize() -> void:
	var value: float = Vector2(3.4,-2.5).x
	var short_: String = JSON.stringify(value)
	var precise: String = JSON.stringify(value,"",true,true)
	print(JSON.stringify({"normal":short_,"precise":precise,"normal_exact":JSON.parse_string(short_) == value,"precise_exact":JSON.parse_string(precise) == value}))
	quit(0 if JSON.parse_string(precise) == value else 1)
