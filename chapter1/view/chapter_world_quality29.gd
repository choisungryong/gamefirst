extends "res://chapter1/view/chapter_world_quality22.gd"
## Unconnected lighting study. Geometry, lighting energy and gameplay unchanged.
## Godot4.5 Forward+ SSAO: docs.godotengine.org/en/4.5/classes/class_environment.html
var environment29: Environment
func setup(view: Node3D) -> void:
	super.setup(view)
	for child in view.get_children():
		if child is WorldEnvironment:environment29=child.environment
	configure29(true)
func configure29(enabled: bool,strong: bool=false) -> void:
	if environment29==null:return
	environment29.ssao_enabled=enabled
	environment29.ssao_radius=.9 if strong else .65
	environment29.ssao_intensity=1.8 if strong else 1.2
	environment29.ssao_power=1.25
	environment29.ssao_detail=.25
	environment29.ssao_light_affect=.28 if strong else .12
