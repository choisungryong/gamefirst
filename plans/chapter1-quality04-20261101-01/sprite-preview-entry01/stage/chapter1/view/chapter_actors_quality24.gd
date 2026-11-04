extends "res://chapter1/view/chapter_actors_quality21.gd"
## Frozen imported mesh path identifies immutable geometry across scene instances.
## Keep per-actor material overrides, skeletons and poses independent.
var _shared_skin24: Dictionary={}
var skin24_builds := 0
var skin24_hits := 0
func _demon19_materials(node: Node,materials: Array[StandardMaterial3D],kind: String) -> void:
	var aliases: Array[Dictionary]=[]
	for child in node.get_children():
		if not child is MeshInstance3D:continue
		var path: String=child.mesh.resource_path
		if kind not in ["walker","elite"] or not path.begins_with(WARDEN+"::"):continue
		var key := path+":"+kind
		var transient := str(child.mesh.get_instance_id())+":"+kind
		if _shared_skin24.has(key):
			_batch19_cache[transient]=_shared_skin24[key];skin24_hits+=1
		aliases.append({"key":key,"transient":transient})
	super._demon19_materials(node,materials,kind)
	for alias in aliases:
		if not _shared_skin24.has(alias.key):
			_shared_skin24[alias.key]=_batch19_cache[alias.transient];skin24_builds+=1
		_batch19_cache.erase(alias.transient)
