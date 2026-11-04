extends "res://chapter1/view/chapter_elements_quality22.gd"
## Nearby ground names retain their drop beams and original 8m visibility rule.
## Size and separation are presentation only; collection stays in the core.
const LOOT26_FONT := 36
const LOOT26_NOMINAL_PIXELS := 15.0
var _loot26_font: SystemFont
var _loot26_mesh := ImmediateMesh.new()
var _loot26_leaders: MeshInstance3D
var layout26_records: Array[Dictionary]=[]
func setup(owner_view: Node3D) -> void:
 super.setup(owner_view)
 _loot26_font=SystemFont.new();_loot26_font.font_names=PackedStringArray(["Malgun Gothic","맑은 고딕","sans-serif"])
 _loot26_leaders=MeshInstance3D.new();_loot26_leaders.name="GroundNameLeaders26";_loot26_leaders.mesh=_loot26_mesh
 var material := _glow(Color(.72,.69,.59,.65),0)
 material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;material.no_depth_test=true
 _loot26_leaders.material_override=material;_loot26_leaders.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 view.add_child(_loot26_leaders)
func sync(run: RefCounted,delta: float) -> void:
 super.sync(run,delta);layout26_records.clear();_loot26_mesh.clear_surfaces();_loot26_leaders.visible=false
 var camera := view.get_viewport().get_camera_3d()
 if camera==null:return
 var viewport_size: Vector2=view.get_viewport().get_visible_rect().size
 var candidates: Array=[]
 for item in run.items:
  if item.position.distance_squared_to(run.hero.position)>=64.0:continue
  candidates.append(item)
 candidates.sort_custom(func(a,b):
  var priority := {"unique":0,"rare":1,"magic":2,"common":3}
  var ap: int=priority.get(a.quality,3);var bp: int=priority.get(b.quality,3)
  return ap<bp if ap!=bp else int(a.uid)<int(b.uid))
 var occupied: Array[Rect2]=[]
 var line_count := 0
 var grid_origin := INF
 _loot26_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
 for item in candidates:
  if not item_nodes.has(item.uid):continue
  var node: Node3D=item_nodes[item.uid];var label: Label3D=node.get_child(1)
  if not label.has_meta("loot26_ready"):
   label.font=_loot26_font;label.font_size=LOOT26_FONT;label.outline_size=6;label.outline_modulate=Color(.025,.022,.018,1);label.no_depth_test=true
   label.render_priority=110;label.outline_render_priority=109
   label.set_meta("loot26_metrics",_loot26_font.get_string_size(label.text,HORIZONTAL_ALIGNMENT_LEFT,-1,LOOT26_FONT))
   label.set_meta("loot26_ready",true)
  var anchor: Vector3=node.to_global(Vector3(0,1.5,0))
  if camera.is_position_behind(anchor):label.visible=false;continue
  var screen := camera.unproject_position(anchor)
  var pixels_per_world := screen.distance_to(camera.unproject_position(anchor+camera.global_basis.y))
  if pixels_per_world<.001:continue
  var pixel_size_ := LOOT26_NOMINAL_PIXELS/(float(LOOT26_FONT)*pixels_per_world)
  if absf(label.pixel_size-pixel_size_)>.000001:label.pixel_size=pixel_size_
  var scale_ := LOOT26_NOMINAL_PIXELS/float(LOOT26_FONT)
  var text_size: Vector2=label.get_meta("loot26_metrics")*scale_
  var size_ := Vector2(text_size.x+8,_loot26_font.get_height(LOOT26_FONT)*scale_+6)
  var center := Vector2(clampf(screen.x,size_.x*.5+8,viewport_size.x-size_.x*.5-8),clampf(screen.y,92+size_.y*.5,viewport_size.y-112-size_.y*.5))
  if is_inf(grid_origin):grid_origin=center.y
  var chosen := center;var rect := Rect2(center-size_*.5,size_)
  var placed := false
  for step in 41:
   var row := (step+1)/2
   var offset := 0.0 if step==0 else float(row)*(size_.y+5)*( -1.0 if step%2==1 else 1.0)
   var test_center := center+Vector2(0,offset)
   if step>0:test_center.y=grid_origin+roundf((center.y-grid_origin)/(size_.y+5))*(size_.y+5)+offset
   if test_center.y-size_.y*.5<92 or test_center.y+size_.y*.5>viewport_size.y-112:continue
   var test_rect := Rect2(test_center-size_*.5,size_)
   var clear := true
   for used in occupied:
    if test_rect.intersects(used.grow(2)):clear=false;break
   if clear:chosen=test_center;rect=test_rect;placed=true;break
  occupied.append(rect)
  var depth := (anchor-camera.global_position).dot(-camera.global_basis.z)
  var target := camera.project_position(chosen,depth)
  label.position=node.to_local(target);label.visible=true
  var shifted: bool=chosen.distance_to(screen)>3
  if shifted:
   _loot26_mesh.surface_add_vertex(node.to_global(Vector3(0,1.3,0)))
   _loot26_mesh.surface_add_vertex(target-camera.global_basis.y*(size_.y*.45/pixels_per_world));line_count+=2
  layout26_records.append({"uid":item.uid,"name":item.name,"rect":rect,"anchor":screen,"center":chosen,"placed":placed,"shifted":shifted,"font_nominal_logical":float(label.font_size)*label.pixel_size*pixels_per_world})
 if line_count==0:
  _loot26_mesh.surface_add_vertex(Vector3(0,-20,0));_loot26_mesh.surface_add_vertex(Vector3(0,-20,0))
 _loot26_mesh.surface_end();_loot26_leaders.visible=line_count>0
func reset() -> void:
 super.reset();layout26_records.clear();_loot26_mesh.clear_surfaces()
 if is_instance_valid(_loot26_leaders):_loot26_leaders.visible=false
