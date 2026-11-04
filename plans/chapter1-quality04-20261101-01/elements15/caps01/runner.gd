extends SceneTree
func _initialize() -> void:call_deferred("execute")
func execute() -> void:
	root.add_child(load("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/elements15/caps01/caps.gd").new())
