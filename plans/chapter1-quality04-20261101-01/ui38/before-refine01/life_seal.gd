extends Control
## A native vector vessel. Its fill is supplied exclusively by the HUD's real HP.
var fraction := 1.0:
	set(value):
		fraction=clampf(value,0.0,1.0)
		queue_redraw()
func _ready() -> void:
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	custom_minimum_size=Vector2(112,112)
func _draw() -> void:
	var c := size/2.0
	draw_circle(c,49,Color("101315"))
	draw_arc(c,49,0,TAU,80,Color("aa8d58"),2.0,true)
	draw_arc(c,43,-PI/2,TAU*fraction-PI/2,80,Color("b83f51"),9.0,true)
	draw_circle(c,34,Color("241b1d"))
	var diamond := PackedVector2Array([c+Vector2(0,-27),c+Vector2(19,0),c+Vector2(0,27),c+Vector2(-19,0)])
	draw_colored_polygon(diamond,Color("753040"))
	draw_polyline(PackedVector2Array([diamond[0],diamond[1],diamond[2],diamond[3],diamond[0]]),Color("e7dfc9"),1.0,true)
	draw_line(c+Vector2(-12,0),c+Vector2(12,0),Color("e7dfc9"),2,true)
	draw_line(c+Vector2(0,-16),c+Vector2(0,16),Color("e7dfc9"),2,true)
	for i in 8:
		var v := Vector2.from_angle(float(i)*TAU/8)
		draw_line(c+v*51,c+v*55,Color("aa8d58"),2,true)
