extends SceneTree
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
 var records: Array=[]
 for variant in ["quality24","quality25_warm"]:
  var owner_ := Node3D.new();root.add_child(owner_)
  var presenter=load("res://chapter1/view/chapter_actors_"+variant+".gd").new()
  var before_memory := OS.get_static_memory_usage()
  var before_time := Time.get_ticks_usec()
  presenter.setup(owner_)
  records.append({"variant":variant,"setup_usec":Time.get_ticks_usec()-before_time,"memory_delta_bytes":OS.get_static_memory_usage()-before_memory,"pooled":presenter._pool25_size() if variant=="quality25_warm" else 0})
  owner_.queue_free()
  for i in 4:await process_frame
 var path := ""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--startup-output="):path=arg.trim_prefix("--startup-output=")
 assert(not path.is_empty() and not FileAccess.file_exists(path))
 var file := FileAccess.open(path,FileAccess.WRITE)
 file.store_string(JSON.stringify({"records":records,"scope":"One sequential headless actor.setup per variant in same imported source stage. Includes hero setup and warm pool allocation; not cold boot/first visible menu/GPU shader latency/process working set."},"\t"));file.close()
 quit()
