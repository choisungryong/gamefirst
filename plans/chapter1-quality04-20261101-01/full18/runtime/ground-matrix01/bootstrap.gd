extends SceneTree
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	var script=load("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full18/runtime/ground-matrix01/matrix.gd")
	root.add_child(script.new())
