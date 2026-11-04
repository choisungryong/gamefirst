extends RefCounted
## Role selection only. No enemy definition, core state or save data is modified.
var bindings: Dictionary={}
var warnings: Array[String]=[]
var error := ""
var loaded := false
func configure(path: String) -> bool:
	bindings.clear();warnings.clear();error="";loaded=false
	var doc: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not doc is Dictionary or doc.get("schema")!=1 or not doc.get("bindings") is Dictionary:error="Invalid sprite role registry";return false
	for role in doc.bindings:
		if role not in ["hero","walker","ranged","charger","elite"]:error="Unknown role: "+str(role);return false
		var slot: Dictionary=doc.bindings[role]
		var asset: String=slot.get("asset","")
		if not asset.begins_with("res://") or ".." in asset or not FileAccess.file_exists(asset):error="Missing registered asset: "+asset;return false
		var actor: Variant=JSON.parse_string(FileAccess.get_file_as_string(asset))
		if not actor is Dictionary or not actor.get("clips") is Dictionary or actor.get("kind")!=role:error="Asset role does not match slot: "+role;return false
		for direction in ["south","east","north","west"]:
			if not actor.clips.has("move_"+direction):error="Missing movement direction: "+direction;return false
		var cast: Array=actor.clips.get("cast",actor.clips.get("cast_south",[]))
		var release: int=slot.get("release_frame",actor.get("release_frame",-1))
		if not cast.is_empty() and (release<0 or release>=cast.size()):error="Choose an authored release frame for role: "+role;return false
		for action in ["cast","hit","death"]:
			if actor.clips.has(action):warnings.append(role+":"+action+" uses common authored facing")
			elif not actor.clips.has(action+"_south"):
				if not slot.get("allow_missing_preview",false):error="Missing combat action: "+role+":"+action;return false
				warnings.append(role+":"+action+" missing; preview fallback")
		bindings[role]={"asset":asset,"release_frame":release}
	loaded=true
	return true
