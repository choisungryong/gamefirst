extends SceneTree
## Exported PCK with isolated profile storage; all gameplay/UI inputs are OS inputs.
class IsolatedSim extends "res://baseline_sim.gd":
	func save_progress(_path: String = "") -> bool:
		return super.save_progress("res://evidence/phase6/native-qa-20261030-01/progress.json")
	func load_progress(_path: String = "") -> bool:
		return super.load_progress("res://evidence/phase6/native-qa-20261030-01/progress.json")
var view: Node
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	view = load("res://Baseline.tscn").instantiate()
	view.sim = IsolatedSim.new()
	root.add_child(view)
