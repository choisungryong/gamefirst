extends "res://chapter1/core/chapter_run_quality36.gd"
## Unadopted successor: no combat duplication or post-start growth reconfiguration.
const SuccessorGrowth = preload("res://chapter1/core/run_growth_quality37.gd")

func _init() -> void:
	growth = SuccessorGrowth.new()
