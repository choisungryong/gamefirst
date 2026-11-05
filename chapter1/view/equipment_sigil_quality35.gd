extends "res://chapter1/view/equipment_sigil_quality17.gd"
## Project-authored slot paintings; rarity remains in the frame.
const PAINTINGS = {
 "weapon":preload("res://chapter1/art/equipment_icons35/weapon.svg"),
 "body":preload("res://chapter1/art/equipment_icons35/body.svg"),
 "ring":preload("res://chapter1/art/equipment_icons35/ring.svg"),
 "charm":preload("res://chapter1/art/equipment_icons35/charm.svg")
}
func _init() -> void:
 super._init()
 custom_minimum_size=Vector2(56,56)
func _draw() -> void:
 draw_style_box(_frame(),Rect2(Vector2.ZERO,size))
 var painting: Texture2D=PAINTINGS.get(slot,PAINTINGS["charm"])
 var edge: float=minf(size.x,size.y)-8.0
 draw_texture_rect(painting,Rect2((size-Vector2.ONE*edge)*0.5,Vector2.ONE*edge),false)
