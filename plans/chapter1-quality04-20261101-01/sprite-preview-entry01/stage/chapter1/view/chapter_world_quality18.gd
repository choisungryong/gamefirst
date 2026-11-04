extends "res://chapter1/view/chapter_world_quality17.gd"
## Cover every legal camera target and the current viewport's ground footprint.
## Reuses the existing single plane and world-space terrain shader. No collision.
const GROUND_MARGIN := 3.0
var ground_coverage: Dictionary={}
var _coverage_viewport := Vector2.ZERO
var _coverage_camera_size := -1.0
var _coverage_floor: MeshInstance3D
func setup(view: Node3D) -> void:
	super.setup(view)
	_coverage_floor=root.get_child(0) as MeshInstance3D
	_ensure_ground_coverage()
func update_camera(hero: Vector2,delta: float) -> void:
	super.update_camera(hero,delta)
	_ensure_ground_coverage()
func _ensure_ground_coverage() -> void:
	if not is_instance_valid(_coverage_floor) or camera==null:return
	var viewport_size := camera.get_viewport().get_visible_rect().size
	if viewport_size.x<=0 or viewport_size.y<=0:return
	if viewport_size==_coverage_viewport and is_equal_approx(camera.size,_coverage_camera_size):return
	var center := camera.position-CAMERA_OFFSET
	var minimum := Vector2(INF,INF);var maximum := Vector2(-INF,-INF)
	var plane := Plane(Vector3.UP,_coverage_floor.position.y)
	for x in [0.0,viewport_size.x]:
		for y in [0.0,viewport_size.y]:
			var hit: Variant=plane.intersects_ray(camera.project_ray_origin(Vector2(x,y)),camera.project_ray_normal(Vector2(x,y)))
			if not hit is Vector3:return
			var offset := Vector2(hit.x-center.x,hit.z-center.z)
			minimum=minimum.min(offset);maximum=maximum.max(offset)
	# Core bounds: three zone squares of half-size19, centers0/48/96.
	# Camera smoothing stays inside their outer convex rectangle. Margin also
	# covers the bounded camera shake without regenerating a mesh every frame.
	var lower := Vector2(-19,-19)+minimum-Vector2.ONE*GROUND_MARGIN
	var upper := Vector2(115,19)+maximum+Vector2.ONE*GROUND_MARGIN
	var mesh := _coverage_floor.mesh as PlaneMesh
	mesh.size=upper-lower
	_coverage_floor.position.x=(lower.x+upper.x)*.5;_coverage_floor.position.z=(lower.y+upper.y)*.5
	_coverage_viewport=viewport_size;_coverage_camera_size=camera.size
	ground_coverage={"viewport":viewport_size,"minimum":lower,"maximum":upper,"plane_size":mesh.size,"margin":GROUND_MARGIN,"draw_surfaces":mesh.get_surface_count()}
