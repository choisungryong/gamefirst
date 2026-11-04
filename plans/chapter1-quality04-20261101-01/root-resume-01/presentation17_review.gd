extends "res://chapter1/chapter_one_view.gd"
var scenario := "ending"
var age := 0.0
var saved: Dictionary={}
var checks: Dictionary={}
var armed := false
var scroll_before := 0
func _ready() -> void:
	super._ready()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--review-scenario="):scenario=arg.get_slice("=",1)
	var target := 23830 if scenario=="ending" else 3240
	while run.tick<target:run.step(full_pilot.decide())
	actors.reset();effects.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);hud.invalidate();hud.sync(run,float(target)/60)
	_save("start",run.snapshot());armed=true
func _save(name_: String,value: Variant) -> void:
	var f := FileAccess.open("res://"+scenario+"-"+name_+".json",FileAccess.WRITE);f.store_string(JSON.stringify(value,"\t"));f.close()
func _process(delta: float) -> void:
	super._process(delta)
	if not armed:return
	age+=delta
	if scenario=="combat":
		for at in [.2,1.0,2.0,3.0]:
			if age>=at and not saved.has(str(at)):saved[str(at)]=true;_shot("combat-%.1f"%at)
		return
	for at in [1.0,1.6,2.4]:
		if age>=at and not saved.has(str(at)):
			saved[str(at)]=true;_shot("ending-%.1f"%at)
			if at==1.0:checks["victory_world_visible_before_reward"]=not hud.overlay.visible
			if at==2.4:checks["reward_panel_visible_after_death"]=hud.overlay.visible
	if age>=2.8 and not saved.has("inventory"):
		saved.inventory=true;open_equipment();hud.sync(run,0)
	if age>=3.1 and not saved.has("scroll"):
		saved.scroll=true
		var scroll := _find_scroll(hud.modal)
		if scroll:scroll.scroll_vertical=650
	if age>=3.3 and not saved.has("select"):
		saved.select=true
		var scroll := _find_scroll(hud.modal)
		if scroll:scroll_before=scroll.scroll_vertical
		hud._selected_item=run._elite_reward_uid;hud.invalidate();hud.sync(run,0)
	if age>=3.6 and not saved.has("gear"):
		saved.gear=true
		var scroll := _find_scroll(hud.modal)
		checks["selection_preserves_scroll"]=scroll!=null and scroll_before>0 and scroll.scroll_vertical==scroll_before
		print("REVIEW17_SCROLL ",JSON.stringify({"before":scroll_before,"after":scroll.scroll_vertical if scroll else -1}))
		checks["unique_description_visible"]=_text_contains(hud.modal,"서리 빙결 문턱")
		_shot("equipment-unique")
func _find_scroll(node: Node) -> ScrollContainer:
	if node is ScrollContainer:return node
	for c in node.get_children():
		var result := _find_scroll(c)
		if result:return result
	return null
func _text_contains(node: Node,part: String) -> bool:
	if node is Label and part in node.text:return true
	for c in node.get_children():
		if _text_contains(c,part):return true
	return false
func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://"+scenario+"-shots")
	get_viewport().get_texture().get_image().save_png("res://"+scenario+"-shots/"+name_+".png")
func _print_result() -> void:
	super._print_result()
	if not armed:return
	_save("end",run.snapshot());_save("checks",checks)
