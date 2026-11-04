extends SceneTree
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	var view=load("res://chapter1/ChapterOne.tscn").instantiate()
	view.actors=load("res://chapter1/presentation/sprite_role_actors_preview.gd").new()
	if not view.actors.registry.configure("res://sprite-preview-registry.json"):
		push_error(view.actors.registry.error);quit(1);return
	root.add_child(view)
	DisplayServer.window_set_title("스프라이트 역할 전투 미리보기 · 저장 꺼짐")
	view.hud.notify("등록 에셋 역할 미리보기 · 기존 저장에 반영하지 않습니다")
