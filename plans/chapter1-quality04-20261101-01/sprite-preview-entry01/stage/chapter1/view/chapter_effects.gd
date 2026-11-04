extends "res://chapter1/view/cloister_effects.gd"
## Full chapter hazards use the same paid positions/radii as damage checks.
var ward_rings: MeshInstance3D
var ward_fill: MeshInstance3D
var potions: Dictionary={}
var _ward_lines := ImmediateMesh.new()
var _ward_area := ImmediateMesh.new()
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	ward_rings=MeshInstance3D.new();ward_fill=MeshInstance3D.new()
	ward_rings.material_override=_glow(Color("e5a363"),.25)
	var fill := _glow(Color(1,.34,.12,.13),0);fill.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	ward_fill.material_override=fill;view.add_child(ward_rings);view.add_child(ward_fill)
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	_ward_lines.clear_surfaces();_ward_lines.surface_begin(Mesh.PRIMITIVE_LINES)
	_ward_area.clear_surfaces();_ward_area.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for h in run.chapter_hazards:
		var center := Vector3(h.position.x,.075,h.position.y)
		var radius: float=h.radius
		var progress := clampf(float(run.tick-h.started)/float(h.expires-h.started),0,1)
		_circle(_ward_lines,center,radius,48);_circle(_ward_lines,center,radius*progress,48)
		for i in 48:
			_ward_area.surface_add_vertex(center)
			_ward_area.surface_add_vertex(center+Vector3(cos(TAU*i/48),0,sin(TAU*i/48))*radius)
			_ward_area.surface_add_vertex(center+Vector3(cos(TAU*(i+1)/48),0,sin(TAU*(i+1)/48))*radius)
	if run.chapter_hazards.is_empty():
		for i in 2:_ward_lines.surface_add_vertex(Vector3(0,-20,0))
		for i in 3:_ward_area.surface_add_vertex(Vector3(0,-20,0))
	_ward_lines.surface_end();_ward_area.surface_end();ward_rings.mesh=_ward_lines;ward_fill.mesh=_ward_area
	var wanted := {}
	for pickup in run.potion_pickups:
		wanted[pickup.uid]=true
		if not potions.has(pickup.uid):
			var node := Node3D.new();var vial := MeshInstance3D.new();var mesh := CapsuleMesh.new();mesh.radius=.10;mesh.height=.32
			vial.mesh=mesh;vial.position.y=.28;vial.material_override=_glow(Color("c1494e"),.25);node.add_child(vial)
			var label := Label3D.new();label.text="+";label.font_size=28;label.pixel_size=.007;label.position.y=.62;label.modulate=Color("e8bdbc");label.billboard=BaseMaterial3D.BILLBOARD_ENABLED;node.add_child(label)
			view.add_child(node);potions[pickup.uid]=node
		potions[pickup.uid].position=Vector3(pickup.position.x,0,pickup.position.y)
	for uid in potions.keys():
		if not wanted.has(uid):potions[uid].queue_free();potions.erase(uid)
func reset() -> void:
	super.reset()
	for node in potions.values():node.queue_free()
	potions.clear()
