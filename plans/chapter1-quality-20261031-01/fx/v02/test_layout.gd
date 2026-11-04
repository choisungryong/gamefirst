extends SceneTree
## Synthetic all-evolved HUD fixture; it does not change product balance/state.
## Font width pattern: https://docs.godotengine.org/en/4.5/classes/class_font.html#class-font-method-get-string-size
## Canvas bounds: https://docs.godotengine.org/en/4.5/classes/class_control.html#class-control-method-get-global-rect
const Run=preload("res://chapter1/core/combat_run.gd")
var checks:=0
var failures:Array[String]=[]
var observations:Array=[]
func check(value:bool,message:String)->void:
	checks+=1
	if not value:failures.append(message)
func _initialize()->void:call_deferred("execute")
func execute()->void:
	var hud_path:="res://chapter1/view/cloister_hud.gd"
	if "--hud-before" in OS.get_cmdline_user_args():hud_path="res://plans/chapter1-quality-20261031-01/fx/v02/before/chapter1/view/cloister_hud.gd"
	var hud_script=load(hud_path)
	for resolution in [Vector2i(1440,810),Vector2i(1920,1080),Vector2i(1600,900)]:
		var viewport:=SubViewport.new()
		viewport.size=resolution
		root.add_child(viewport)
		var view:=Node3D.new()
		viewport.add_child(view)
		var hud=hud_script.new()
		hud.setup(view)
		var run=Run.new()
		check(run.start(90131,"chapter1.skill.ember"),"run configured")
		# Presentation-only worst-label fixture, not a normal-play/evolution claim.
		run.growth._ranks={"chapter1.skill.ember":4,"chapter1.skill.frost":4,"chapter1.skill.arc":4}
		run.growth._evolved.assign(["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"])
		run.growth._level=12
		run.growth._xp=396
		var before:Dictionary=run.snapshot()
		hud.sync(run,0)
		for i in 5:await process_frame
		var viewport_rect:=Rect2(Vector2.ZERO,Vector2(resolution))
		var previous_end:=0.0
		var row_record:={"resolution":[resolution.x,resolution.y],"labels":[]}
		for id_ in hud.skill_labels:
			var label:Label=hud.skill_labels[id_]
			var rect:=label.get_global_rect()
			var chip_rect:Rect2=label.get_parent().get_global_rect()
			var panel_rect:Rect2=label.get_parent().get_parent().get_parent().get_parent().get_global_rect()
			var lines:=label.text.split("\n")
			var longest:=0.0
			for line in lines:
				longest=maxf(longest,label.get_theme_font("font").get_string_size(line,HORIZONTAL_ALIGNMENT_LEFT,-1,label.get_theme_font_size("font_size")).x)
			var prefix:String=str(resolution)+" "+String(id_)
			check(label.autowrap_mode==TextServer.AUTOWRAP_OFF,prefix+" only intended line break")
			check(label.get_line_count()==2,prefix+" exactly two displayed lines")
			check(label.get_visible_line_count()==2,prefix+" both lines visible")
			check(longest<=rect.size.x+.5,prefix+" full text width without ellipsis")
			check(rect.size.y>=label.get_line_height()*2+label.get_theme_constant("line_spacing"),prefix+" full two-line height")
			check(viewport_rect.encloses(rect),prefix+" inside viewport")
			check(panel_rect.encloses(rect),prefix+" inside bottom frame")
			check(chip_rect.encloses(rect),prefix+" inside skill chip")
			check(rect.position.x>=previous_end,prefix+" no prior label overlap")
			previous_end=rect.end.x
			row_record.labels.append({"id":id_,"text":label.text,"rect":[rect.position.x,rect.position.y,rect.size.x,rect.size.y],"frame":[panel_rect.position.x,panel_rect.position.y,panel_rect.size.x,panel_rect.size.y],"longest_text_px":longest,"line_count":label.get_line_count(),"visible_lines":label.get_visible_line_count()})
		for pair in [["status",hud.status],["dash",hud.dash],["hp",hud.hp],["xp",hud.xp]]:
			check(viewport_rect.encloses(pair[1].get_global_rect()),str(resolution)+" "+pair[0]+" inside viewport")
		check(run.snapshot()==before,"HUD layout leaves core snapshot unchanged")
		observations.append(row_record)
		viewport.free();view=null;hud=null;run=null
		await process_frame
	if "--prove-failure" in OS.get_cmdline_user_args():check(false,"intentional negative")
	print("QUALITY_HUD_LAYOUT ",JSON.stringify({"checks":checks,"failures":failures,"hud_path":hud_path,"observations":observations,"scope":"Synthetic headless container/text geometry; GPU render and final visual quality pending"}))
	quit(0 if failures.is_empty() else 1)
