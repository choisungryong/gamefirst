extends SceneTree
var view: Node3D
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 var expected: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full36/runtime/default-profile-earn01/proof/RESULT.json"))
 view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 for index in 4:await process_frame
 var expected_profile: Dictionary=load("res://chapter1/core/chapter_profile.gd").normalize(expected.profile_state)
 var same: bool=view.profile.available and not expected_profile.is_empty() and view.profile.state==expected_profile
 var result: Dictionary={"same_profile_after_process_restart":same,"default_profile_enabled":not view._profile_off,"completed_runs":view.profile.state.completed_runs,"items":view.profile.state.items.size(),"profile_path":ProjectSettings.globalize_path(view.profile.path),"scope":"Separate actual36 EXE process loading original default user36 earned profile. No grants/equip/start or profile writes; explicit observer cleanup before quit. Not native clicks/manual."}
 var f=FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full36/runtime/default-profile-reload02/RESULT.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();f=null
 view.audio.reset();view.queue_free()
 for index in 4:await process_frame
 view=null
 quit(0 if same else 2)
