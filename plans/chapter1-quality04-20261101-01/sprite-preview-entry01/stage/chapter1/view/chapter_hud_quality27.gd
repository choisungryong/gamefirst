extends "res://chapter1/view/chapter_hud_quality23.gd"
## Keep temporary combat messages below the champion/boss health bar.
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	if boss_bar==null or toast==null:return
	toast.position.y= maxf(80.0,boss_bar.get_rect().end.y+10.0) if boss_bar.visible else 80.0
