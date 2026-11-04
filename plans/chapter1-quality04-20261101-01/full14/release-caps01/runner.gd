extends SceneTree
func _initialize() -> void:call_deferred("execute")
func execute() -> void:
	var script=load("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full14/release-caps01/caps.gd")
	root.add_child(script.new())
