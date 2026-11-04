extends SceneTree
var view: Node3D
var folder := ""
var started_us := -1
var start_tick := -1
var played_before := 0
var dropped_before := 0
var variants_before: Dictionary={}
var ending := false
var recorder: AudioEffectRecord
var effect_index := -1
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--audio26-dir="):folder=arg.trim_prefix("--audio26-dir=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):push_error("Fresh audio evidence folder required");quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 while view.run.tick<16000:view.run.step(view.full_pilot.decide())
 view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
 view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(folder.path_join("before.png"))
 recorder=AudioEffectRecord.new();recorder.format=AudioStreamWAV.FORMAT_16_BITS
 effect_index=AudioServer.get_bus_effect_count(0);AudioServer.add_bus_effect(0,recorder);recorder.set_recording_active(true)
 played_before=view.audio.played;dropped_before=view.audio.dropped;variants_before=view.audio.variants.duplicate(true)
 start_tick=view.run.tick;started_us=Time.get_ticks_usec()
 print("AUDIO26_RECORDING ",JSON.stringify({"primary":view.primary,"tick":start_tick,"method":"actual Master bus, no microphone"}))
func _process(_delta: float) -> bool:
 if started_us<0 or ending:return false
 if Time.get_ticks_usec()-started_us>=14000000:
  ending=true;view.set_physics_process(false);view.set_process(false);call_deferred("_finish")
 return false
func _finish() -> void:
 recorder.set_recording_active(false)
 var wav := recorder.get_recording();var code := wav.save_to_wav(folder.path_join("actual-game-mix.wav"));AudioServer.remove_bus_effect(0,effect_index)
 var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference
 var ok: bool=reference.start(view.seed_,view.primary)
 while reference.tick<view.run.tick:reference.step(policy.decide())
 var same: bool=ok and reference.snapshot()==view.run.snapshot()
 var cues: Dictionary={}
 for cue in view.audio.variants:cues[cue]=int(view.audio.variants[cue])-int(variants_before.get(cue,0))
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(folder.path_join("after.png"))
 var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify({"primary":view.primary,"start_tick":start_tick,"final_tick":view.run.tick,"zone":view.run.zone,"mode":view.run.mode,"same_complete_core":same,"played":view.audio.played-played_before,"dropped":view.audio.dropped-dropped_before,"cue_counts":cues,"master_volume":view.audio.master_volume,"muted":view.audio.muted,"wav_save_result":code,"scope":"Actual26 packaged normal earned16000tick checkpoint then14s real-time live combat Master-bus recording. Other learned skills remain active. Independent final core match; no microphone/hearing/manual/formal-performance approval."},"\t"));f.close()
 view.audio.reset()
 for i in 4:await process_frame
 quit(0 if same and code==OK else 1)
