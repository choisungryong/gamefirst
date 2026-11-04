extends SceneTree
func _initialize() -> void:
	var namespace: String=ProjectSettings.get_setting("application/config/custom_user_dir_name","")
	var path := ProjectSettings.globalize_path("user://chapter-one-profile-v1.json")
	var exists := FileAccess.file_exists("user://chapter-one-profile-v1.json")
	print("DEFAULT23_PREFLIGHT ",JSON.stringify({"namespace":namespace,"path":path,"exists":exists,"scope":"Read-only path/absence check; profile class not configured."}))
	quit(0 if namespace=="AshenCloisterChapterOneQuality23" and not exists else 1)
