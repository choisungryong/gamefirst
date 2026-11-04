extends "res://chapter1/view/chapter_world_quality22.gd"
## Unconnected volumetric column study. No core/colliders/lighting additions.
var columns31: Array[Dictionary]=[]
var _old_columns31: Array[Node3D]=[]
var _solid_columns31: Array[Node3D]=[]
var clearance31: Array[Dictionary]=[]
func _prop(id_: String,at: Vector3,height: float=0.0,tint: Color=Color.WHITE,mirror: bool=false) -> void:
	if id_ in ["pillar_whole","pillar_broken"]:columns31.append({"id":id_,"at":at,"height":height,"tint":tint})
	super._prop(id_,at,height,tint,mirror)
func _bake_prop_surface(entries: Array[Dictionary],texture: Texture2D,label: String) -> void:
	var pillars: Array[Dictionary]=[];var others: Array[Dictionary]=[]
	for entry in entries:
		if entry.id in ["pillar_whole","pillar_broken"]:pillars.append(entry)
		else:others.append(entry)
	if not others.is_empty():super._bake_prop_surface(others,texture,label)
	if not pillars.is_empty():
		super._bake_prop_surface(pillars,texture,"OriginalColumnImpostors31")
		_old_columns31.append(root.get_child(root.get_child_count()-1))
func _bake_contact_shadows() -> void:
	var all: Array[Dictionary]=_prop_entries
	var pillars: Array[Dictionary]=[];var others: Array[Dictionary]=[]
	for entry in all:
		if entry.id in ["pillar_whole","pillar_broken"]:pillars.append(entry)
		else:others.append(entry)
	_prop_entries=others
	if not others.is_empty():super._bake_contact_shadows()
	_prop_entries=pillars
	if not pillars.is_empty():
		super._bake_contact_shadows();_old_columns31.append(root.get_child(root.get_child_count()-1))
	_prop_entries=all;art_status.contact_shadows=all.size()
func setup(owner: Node3D) -> void:
	super.setup(owner)
	var whole: Array[Dictionary]=[];var broken: Array[Dictionary]=[]
	for i in columns31.size():
		var column: Dictionary=columns31[i];var definition: Dictionary=_prop_defs[column.id]
		var width: float=float(definition.region[2])/float(definition.region[3])*float(column.height)
		var radius := width*.5
		var at: Vector3=column.at
		var safe := _safe31(Vector2(at.x,at.z),radius)
		var adjusted := Vector3(safe.x,at.y,safe.y)
		clearance31.append({"original":Vector2(at.x,at.z),"at":safe,"radius":radius,"clearance":safe.distance_to(_nearest_legal31(safe)),"moved":safe.distance_to(Vector2(at.x,at.z))>.0001})
		var record := {"transform":Transform3D(Basis(Vector3.UP,float(i)*1.71).scaled(Vector3(radius,float(column.height)*1.30,radius)),adjusted),"tint":column.tint*Color(.86,.86,.80),"zone":roundi(at.x/48)}
		if column.id=="pillar_whole":whole.append(record)
		else:broken.append(record)
	for pair in [[whole,false,"SolidWholeColumns31"],[broken,true,"SolidBrokenColumns31"]]:
		if pair[0].is_empty():continue
		_batch22(pair[0],_column_mesh31(pair[1]),pair[2]);_solid_columns31.append(root.get_child(root.get_child_count()-1))
	art_status.solid_columns31=columns31.size();art_status.column_batches31=_solid_columns31.size()
	set_columns31(false)
func _nearest_legal31(point: Vector2) -> Vector2:
	var best := Vector2.ZERO;var distance := INF
	for zone in 3:
		var center := Vector2(zone*48,0)
		var candidate := point.clamp(center-Vector2.ONE*19,center+Vector2.ONE*19)
		var d := point.distance_squared_to(candidate)
		if d<distance:best=candidate;distance=d
		if zone>0:
			candidate=point.clamp(Vector2(center.x-29,-3.6),Vector2(center.x-19,3.6));d=point.distance_squared_to(candidate)
			if d<distance:best=candidate;distance=d
	return best
func _safe31(point: Vector2,radius: float) -> Vector2:
	for attempt in 24:
		var legal := _nearest_legal31(point);var delta := point-legal
		if delta.length()>=radius+.25:return point
		if delta.length_squared()>.0001:point+=delta.normalized()*(radius+.26-delta.length())
		else:
			var center := Vector2(clampi(roundi(point.x/48),0,2)*48,0)
			var direction := (point-center).normalized()
			if direction.length_squared()<.0001:direction=Vector2.UP
			point=center+direction*((19+radius+.35)/maxf(absf(direction.x),absf(direction.y)))
	return point
func set_columns31(enabled: bool) -> void:
	for node in _old_columns31:node.visible=not enabled
	for node in _solid_columns31:node.visible=enabled
func _column_mesh31(broken: bool) -> ArrayMesh:
	var profile := [Vector2(0,1),Vector2(.035,1),Vector2(.055,.85),Vector2(.08,.85),Vector2(.105,.57),Vector2(.85,.51),Vector2(.88,.73),Vector2(.91,.73),Vector2(.935,1),Vector2(1,.92)]
	if broken:profile=[Vector2(0,1),Vector2(.06,1),Vector2(.10,.85),Vector2(.15,.57),Vector2(.92,.53),Vector2(1,.53)]
	var st := SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES);st.set_smooth_group(0)
	var segments := 32
	for ring in profile.size()-1:
		for segment in segments:
			var points: Array[Vector3]=[]
			for corner in [[ring,segment],[ring,segment+1],[ring+1,segment+1],[ring+1,segment]]:
				var p: Vector2=profile[corner[0]];var angle: float=TAU*float(corner[1])/segments
				var radius: float=p.y*(1+.025*cos(angle*8)) if p.y<.7 else p.y
				var y: float=p.x
				if broken and corner[0]==profile.size()-1:y=.94+.055*sin(angle*3)+.018*cos(angle*7)
				points.append(Vector3(cos(angle)*radius,y,sin(angle)*radius))
			var normal := (points[2]-points[0]).cross(points[1]-points[0]).normalized()
			for index in [0,1,2,0,2,3]:
				st.set_normal(normal)
				st.set_color(Color.WHITE*(.94+.05*cos(float(segment)*.7+float(ring))))
				st.add_vertex(points[index])
	# Darker broken fracture cap, closed with upward-facing triangles.
	var top: float=profile[-1].x
	for segment in segments:
		var a := TAU*float(segment)/segments;var b := TAU*float(segment+1)/segments
		var ya := .94+.055*sin(a*3)+.018*cos(a*7) if broken else top
		var yb := .94+.055*sin(b*3)+.018*cos(b*7) if broken else top
		for point in [Vector3(0,.92 if broken else top,0),Vector3(cos(a)*profile[-1].y,ya,sin(a)*profile[-1].y),Vector3(cos(b)*profile[-1].y,yb,sin(b)*profile[-1].y)]:
			st.set_normal(Vector3.UP);st.set_color(Color.WHITE*(.72 if broken else 1.05));st.add_vertex(point)
	return st.commit()
