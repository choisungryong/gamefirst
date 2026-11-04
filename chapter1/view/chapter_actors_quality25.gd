extends "res://chapter1/view/chapter_actors_quality24.gd"
## Recycle only ordinary role presenters after their core entity is gone.
## Boss/elite ownership and all retained corpses keep their original lifetime.
const POOL25_CAP := 96
var _pool25: Dictionary={}
var _pool25_root: Node3D
var pool25_hits := 0
var pool25_created := 0
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	_pool25_root=Node3D.new();_pool25_root.name="DormantActors25"
	_pool25_root.visible=false;_pool25_root.process_mode=Node.PROCESS_MODE_DISABLED
	owner_view.add_child(_pool25_root)
func _pool25_size() -> int:
	var count := 0
	for entries in _pool25.values():count+=entries.size()
	return count
func _stash25(actor: Node3D) -> bool:
	var kind: String=actor.get_meta("kind","")
	if kind not in ["walker","ranged","charger"] or not actor.has_meta("minion19") or _pool25_size()>=POOL25_CAP:return false
	if actor.get_parent()!=null:actor.get_parent().remove_child(actor)
	_pool25_root.add_child(actor)
	var entries: Array=_pool25.get(kind,[]);entries.append(actor);_pool25[kind]=entries
	return true
func _create(kind: String) -> Node3D:
	var entries: Array=_pool25.get(kind,[])
	if kind in ["walker","ranged","charger"] and not entries.is_empty():
		var actor: Node3D=entries.pop_back();_pool25_root.remove_child(actor)
		for name_ in actor.get_meta_list():
			if name_ not in ["kind","minion19","role21"]:actor.remove_meta(name_)
		actor.transform=Transform3D.IDENTITY;actor.visible=true
		var state: Dictionary=actor.get_meta("minion19")
		state.fade=1.0;state.death_age=0.0;state.clip="";state.bucket=-1
		state.model.position=Vector3.ZERO;state.model.rotation=Vector3.ZERO
		state.erase("staff21_time");state.erase("staff21_clip")
		state.skeleton.reset_bone_poses()
		state.player.stop();state.player.play("idle",0);state.player.seek(0,true);state.player.advance(0)
		if state.has("staff21"):state.staff21.position=Vector3.ZERO
		for material_ in state.materials:material_.albedo_color=material_.get_meta("demon19_tint")
		pool25_hits+=1
		return actor
	var actor := super._create(kind)
	if kind in ["walker","ranged","charger"]:pool25_created+=1
	return actor
func sync(run: RefCounted,delta: float) -> void:
	var wanted: Dictionary={}
	for entity in run.enemies.values():wanted["%d:%d"%[entity.generation,entity.id]]=true
	for key in actors.keys():
		if not wanted.has(key) and _stash25(actors[key]):actors.erase(key)
	super.sync(run,delta)
func reset() -> void:
	for key in actors.keys():
		if _stash25(actors[key]):actors.erase(key)
	super.reset()
