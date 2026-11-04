extends Control
## Own code-native slot emblems; no external artwork.
var slot := "charm"
var tint := Color("d1af6b")
func _init() -> void:
	custom_minimum_size=Vector2(42,42);mouse_filter=Control.MOUSE_FILTER_IGNORE
	size_flags_horizontal=Control.SIZE_SHRINK_BEGIN;size_flags_vertical=Control.SIZE_SHRINK_CENTER
func _draw() -> void:
	var c := size*.5
	draw_style_box(_frame(),Rect2(Vector2.ZERO,size))
	match slot:
		"weapon":
			draw_line(c+Vector2(-9,12),c+Vector2(9,-12),tint,3,true)
			draw_line(c+Vector2(-8,1),c+Vector2(3,9),tint,3,true)
			draw_circle(c+Vector2(-9,12),2,tint)
		"body":
			draw_polyline(PackedVector2Array([c+Vector2(-5,-12),c+Vector2(-13,-7),c+Vector2(-9,0),c+Vector2(-6,-2),c+Vector2(-6,12),c+Vector2(6,12),c+Vector2(6,-2),c+Vector2(9,0),c+Vector2(13,-7),c+Vector2(5,-12)]),tint,2,true)
			draw_arc(c+Vector2(0,-12),5,0,PI,14,tint,2,true)
		"ring":
			draw_arc(c+Vector2(0,3),9,0,TAU,32,tint,2,true)
			draw_colored_polygon(PackedVector2Array([c+Vector2(0,-13),c+Vector2(5,-8),c+Vector2(0,-3),c+Vector2(-5,-8)]),tint)
		_:
			draw_arc(c+Vector2(0,-4),10,PI,TAU,20,tint,1.5,true)
			draw_colored_polygon(PackedVector2Array([c+Vector2(0,-6),c+Vector2(8,3),c+Vector2(0,14),c+Vector2(-8,3)]),tint)
func _frame() -> StyleBoxFlat:
	var s := StyleBoxFlat.new();s.bg_color=Color("181b1b");s.border_color=Color(tint,.45);s.set_border_width_all(1);return s
