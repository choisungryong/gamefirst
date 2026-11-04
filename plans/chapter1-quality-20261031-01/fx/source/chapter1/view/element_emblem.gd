extends Control
## Small code-native skill sigils, not a replacement for world art assets.
var element := "ember"
var tint := Color("e4813d")
func _ready() -> void:
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	custom_minimum_size=Vector2(30,30)
func _draw() -> void:
	var c := size*.5
	draw_arc(c,12,0,TAU,32,Color(tint,.20),1,true)
	match element:
		"frost":
			for i in 6:
				var v := Vector2.from_angle(i*TAU/6.)
				draw_line(c-v*2,c+v*10,tint,1.7,true)
				for sign_ in [-1,1]:draw_line(c+v*6,c+v.rotated(sign_*.50)*8,tint,1.2,true)
		"arc":
			draw_polyline(PackedVector2Array([c+Vector2(5,-10),c+Vector2(-5,0),c+Vector2(2,0),c+Vector2(-5,11)]),tint,2.3,true)
		_:
			draw_colored_polygon(PackedVector2Array([c+Vector2(-7,7),c+Vector2(-9,0),c+Vector2(-2,-5),c+Vector2(1,-12),c+Vector2(8,-1),c+Vector2(6,8),c+Vector2(0,11)]),Color(tint,.75))
			draw_polyline(PackedVector2Array([c+Vector2(-3,7),c+Vector2(0,-2),c+Vector2(3,7)]),Color("ffe6aa"),1.8,true)
