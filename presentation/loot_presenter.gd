extends RefCounted
## Bounded visual projection only; automatic pickup and lifetime stay in Sim.
## Godot 4.5 Label3D and SphereMesh: shared marker assets, no per-frame rolls.
## https://docs.godotengine.org/en/4.5/classes/class_label3d.html
var markers: Dictionary = {}
var marker_mesh: SphereMesh
var common_material: StandardMaterial3D
var crafted_material: StandardMaterial3D

func reset() -> void:
	for marker in markers.values():
		marker.queue_free()
	markers.clear()

func sync(view: Node3D, sim: RefCounted) -> void:
	var wanted: Dictionary = {}
	for entry in sim.ground_loot_snapshot():
		var key := "%d:%d" % [int(entry.epoch),int(entry.uid)]
		wanted[key] = true
		if not markers.has(key):
			markers[key] = create_marker(view,sim,entry)
		var marker: Node3D = markers[key]
		marker.position = Vector3(float(entry.p[0]),.18,float(entry.p[1]))
	for key in markers.keys():
		if not wanted.has(key):
			markers[key].queue_free()
			markers.erase(key)

func create_marker(view: Node3D, sim: RefCounted, entry: Dictionary) -> Node3D:
	if marker_mesh == null:
		marker_mesh = SphereMesh.new()
		marker_mesh.radius = .12
		marker_mesh.height = .24
		marker_mesh.radial_segments = 8
		marker_mesh.rings = 4
		common_material = material(Color("c3d3c4"))
		crafted_material = material(Color("e5ba68"))
	var marker := Node3D.new()
	marker.name = "GroundLoot_%d_%d" % [int(entry.epoch),int(entry.uid)]
	view.add_child(marker)
	var mesh := MeshInstance3D.new()
	mesh.mesh = marker_mesh
	mesh.material_override = crafted_material if entry.item.quality == "crafted" else common_material
	mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	marker.add_child(mesh)
	var text := Label3D.new()
	var definition: Dictionary = sim.equipment_catalog.definition("items",entry.item.base_id)
	text.text = "%s\n가까이 가면 획득" % String(definition.get("display_name","장비"))
	text.font_size = 28
	text.pixel_size = .005
	text.position.y = .45
	text.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	text.modulate = Color("e5ba68") if entry.item.quality == "crafted" else Color("c3d3c4")
	marker.add_child(text)
	return marker

func material(color: Color) -> StandardMaterial3D:
	var result := StandardMaterial3D.new()
	result.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	result.albedo_color = color
	return result
