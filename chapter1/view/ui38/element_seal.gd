extends Control
## Large engraved crest for a real offered element; no gameplay state.
var element := "ember"
var tint := Color("e8a05a")
func _ready() -> void:
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	custom_minimum_size=Vector2(70,70)
func _draw() -> void:
	draw_set_transform(size/2,0,Vector2(.7,.7))
	var c := Vector2.ZERO
	draw_circle(c,43,Color("13191b"))
	draw_arc(c,43,0,TAU,64,Color(tint,.5),1,true)
	draw_arc(c,35,0,TAU,64,Color(tint,.2),1,true)
	for sign_ in [-1,1]:
		draw_line(c+Vector2(sign_*48,-9),c+Vector2(sign_*48,9),tint,2,true)
		draw_line(c+Vector2(-9,sign_*48),c+Vector2(9,sign_*48),tint,2,true)
	match element:
		"frost":
			for i in 6:
				var v := Vector2.from_angle(i*TAU/6.)
				draw_line(c-v*4,c+v*26,tint,2,true)
				for sign_ in [-1,1]:draw_line(c+v*15,c+v.rotated(sign_*.5)*22,tint,1.5,true)
		"arc":
			draw_polyline(PackedVector2Array([c+Vector2(12,-27),c+Vector2(-13,1),c+Vector2(5,1),c+Vector2(-12,28)]),tint,4,true)
		_:
			draw_colored_polygon(PackedVector2Array([c+Vector2(-17,17),c+Vector2(-22,0),c+Vector2(-5,-12),c+Vector2(3,-29),c+Vector2(20,-2),c+Vector2(15,20),c+Vector2(0,27)]),Color(tint,.75))
			draw_polyline(PackedVector2Array([c+Vector2(-7,17),c+Vector2(0,-5),c+Vector2(7,17)]),Color("ffe6aa"),3,true)
