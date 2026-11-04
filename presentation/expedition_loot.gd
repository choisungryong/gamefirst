extends RefCounted
## UID+epoch keyed markers. Screen labels separate stacked drops into columns.
const MAX_MARKERS:=32
var view: Node3D
var markers: Dictionary={}
var labels: Dictionary={}
var overlay: Control
var mesh: PrismMesh
var common: Material
var crafted: Material

func setup(owner_view: Node3D) -> void:
	view=owner_view
	var canvas:=CanvasLayer.new()
	canvas.layer=1
	view.add_child(canvas)
	overlay=Control.new()
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.mouse_filter=Control.MOUSE_FILTER_IGNORE
	canvas.add_child(overlay)
	mesh=PrismMesh.new()
	mesh.size=Vector3(.19,.27,.19)
	common=view.material(Color("d5ddd2"),.4)
	crafted=view.material(Color("dfbb70"),.65)

func sync(sim: RefCounted,camera: Camera3D) -> void:
	var wanted: Dictionary={}
	var occupied: Array[Rect2]=[]
	var viewport_size: Vector2=view.get_viewport().get_visible_rect().size
	for entry in sim.ground_loot_snapshot().slice(0,MAX_MARKERS):
		var key: String="%d:%d" % [entry.epoch,entry.uid]
		wanted[key]=true
		if not markers.has(key):
			markers[key]=view.add_mesh(mesh,Vector3.ZERO,crafted if entry.item.quality=="crafted" else common)
			markers[key].cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var label:=Label.new()
			label.add_theme_font_size_override("font_size",16)
			label.add_theme_color_override("font_color",Color("e8c985") if entry.item.quality=="crafted" else Color("d4dfdc"))
			label.add_theme_color_override("font_shadow_color",Color("0c141b"))
			label.add_theme_constant_override("shadow_offset_x",2)
			label.add_theme_constant_override("shadow_offset_y",2)
			label.mouse_filter=Control.MOUSE_FILTER_IGNORE
			var definition: Dictionary=sim.equipment_catalog.definition("items",entry.item.base_id)
			label.text=("◆ " if entry.item.quality=="crafted" else "◇ ")+String(definition.get("display_name","장비"))
			overlay.add_child(label)
			labels[key]=label
		var at:=Vector3(float(entry.p[0]),.18,float(entry.p[1]))
		markers[key].position=at
		var label: Label=labels[key]
		label.visible=not camera.is_position_behind(at)
		if not label.visible: continue
		var screen: Vector2=camera.unproject_position(at+Vector3.UP*.35)
		var wanted_rect:=Rect2(screen+Vector2(16,-26),Vector2(185,25))
		wanted_rect.position.x=clampf(wanted_rect.position.x,12,maxf(12,viewport_size.x-200))
		wanted_rect.position.y=clampf(wanted_rect.position.y,140,maxf(140,viewport_size.y-185))
		for attempt in range(MAX_MARKERS):
			var overlap:=false
			for rect in occupied:
				if wanted_rect.intersects(rect): overlap=true; break
			if not overlap: break
			wanted_rect.position.y+=26
			if wanted_rect.position.y>viewport_size.y-185:
				wanted_rect.position.y=140
				wanted_rect.position.x=clampf(wanted_rect.position.x+190,12,maxf(12,viewport_size.x-200))
		occupied.append(wanted_rect)
		label.position=wanted_rect.position
	for key in markers.keys():
		if not wanted.has(key):
			markers[key].queue_free()
			labels[key].queue_free()
			markers.erase(key)
			labels.erase(key)

func reset() -> void:
	for marker in markers.values(): marker.queue_free()
	for label in labels.values(): label.queue_free()
	markers.clear()
	labels.clear()
