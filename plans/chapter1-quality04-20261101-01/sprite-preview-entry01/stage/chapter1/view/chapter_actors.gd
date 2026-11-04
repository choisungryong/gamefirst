extends "res://chapter1/view/cloister_actors.gd"
## Tiny owner chevron stays above crowds; actor depth/physics remain unchanged.
## Label3D no_depth_test / render_priority: official Godot4.5 class reference.
var owner_mark: Label3D
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	owner_mark=Label3D.new();owner_mark.text="◇";owner_mark.font_size=32;owner_mark.pixel_size=.009
	owner_mark.outline_size=12;owner_mark.outline_modulate=Color(.025,.035,.045,.96)
	owner_mark.modulate=Color("efcd84");owner_mark.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	owner_mark.no_depth_test=true;owner_mark.render_priority=110;owner_mark.outline_render_priority=109
	owner_mark.position=Vector3(0,2.5,0);hero.add_child(owner_mark)
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	owner_mark.visible=not run.hero.is_empty() and run.hero.hp_raw>0
