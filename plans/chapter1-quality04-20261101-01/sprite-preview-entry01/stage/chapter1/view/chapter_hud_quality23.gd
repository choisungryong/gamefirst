extends "res://chapter1/view/chapter_hud_quality20.gd"
## Stable two-line action status: never split a Korean word to fill spare width.
func setup(view: Node3D) -> void:
	super.setup(view)
	dash.autowrap_mode=TextServer.AUTOWRAP_OFF
	dash.custom_minimum_size=Vector2(150,46)
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	if run.hero.is_empty():return
	var remaining := maxf(0,float(run.get_next_dash_tick()-run.tick)/60.0)
	var evade := "Space 회피 준비" if remaining<=0 else "Space 회피 %.1f초"%remaining
	dash.text=evade+"\nQ 회복약 %d / 5"%run.potions
