extends SceneTree
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
 var view=load("res://chapter1/ChapterOne.tscn").instantiate()
 view.actors=load("res://chapter1/view/chapter_actors_quality34b.gd").new();root.add_child(view)
 for i in 20:await process_frame
 print("OUTLAW34_BOOT_DIAGNOSTIC ",JSON.stringify({"tick":view.run.tick,"pool_created":view.actors.pool25_created,"replacements":view.actors.replacements34,"scope":"Short initial render and disposal diagnosis only, not art/combat/adoption approval"}))
 view.audio.reset();view.queue_free()
 for i in 8:await process_frame
 quit(0)
