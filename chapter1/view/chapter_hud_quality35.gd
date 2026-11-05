extends "res://chapter1/view/chapter_hud_quality27.gd"
const PaintedSigil35=preload("res://chapter1/view/equipment_sigil_quality35.gd")
func _sigil(item: Dictionary) -> Control:
 var icon := PaintedSigil35.new()
 icon.slot=item.get("slot","charm")
 icon.tint=QUALITY_COLORS.get(item.get("quality","common"),Color.WHITE)
 return icon
