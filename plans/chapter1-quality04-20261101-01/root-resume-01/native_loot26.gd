extends SceneTree
var view: Node3D
var output := ""
var target := -1
var picked := -1
var checkpoint := 0
var active := false
var ending := false
var started_us := 0
var recording: AudioEffectRecord
var record_index := -1
var input_log: Array=[]
class NativeLog26 extends Node:
 var main: SceneTree
 var seq := -1
 func _input(event: InputEvent) -> void:
  if event is InputEventMouseButton and event.pressed:main.input_log.append({"tick":main.view.run.tick,"mode":main.view.run.mode,"mouse":event.button_index,"position":str(event.position)})
  elif event is InputEventKey and event.pressed and not event.echo:main.input_log.append({"tick":main.view.run.tick,"mode":main.view.run.mode,"key":event.keycode})
 func _physics_process(_delta: float) -> void:
  if not main.active:return
  for event in main.view.run.events:
   if int(event.seq)<=seq:continue
   seq=int(event.seq)
   if event.type=="item_pickup" and event.item.uid==main.target and main.picked<0:
    main.picked=main.view.run.tick;main._after_pick()
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
 started_us=Time.get_ticks_usec()
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--native-loot26-dir="):output=arg.trim_prefix("--native-loot26-dir=")
 if output.is_empty() or DirAccess.dir_exists_absolute(output):push_error("Fresh native output required");quit(1);return
 DirAccess.make_dir_recursive_absolute(output)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 view.set_process(false);view.set_physics_process(false);view._capture_dir=""
 if view._pilot or not view._profile_off:push_error("Native fixture must preserve saves and disable pilot");quit(1);return
 while view.run.tick<16143:view.run.step(view.full_pilot.decide())
 checkpoint=view.run.tick
 for item in view.run.items:
  if item.position.distance_squared_to(view.run.hero.position)<64:target=item.uid;break
 if target<0:push_error("No actual nearby checkpoint drop");quit(1);return
 view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
 view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
 var logger := NativeLog26.new();logger.main=self;logger.process_physics_priority=100;root.add_child(logger)
 view.tree_exiting.connect(_save)
 await _shot("before.png")
 print("NATIVE26_READY ",JSON.stringify({"target_uid":target,"checkpoint":checkpoint,"pilot":view._pilot,"fx":view.effects.get_script().resource_path,"scope":"Actual26 PCK scene, earned checkpoint held until actual native ground click; then original controller, no movement injection. Partial input/collection proof, not manual whole."}))
func _process(_delta: float) -> bool:
 if not is_instance_valid(view) or ending:return false
 if not active and view._has_move_target:
  active=true
  recording=AudioEffectRecord.new();recording.format=AudioStreamWAV.FORMAT_16_BITS
  record_index=AudioServer.get_bus_effect_count(0);AudioServer.add_bus_effect(0,recording);recording.set_recording_active(true)
  view.set_process(true);view.set_physics_process(true)
  print("NATIVE26_STARTED ",JSON.stringify({"move_target":str(view._move_target),"native_inputs":input_log.size()}))
 if Time.get_ticks_usec()-started_us>180000000:ending=true;quit(1)
 return false
func _after_pick() -> void:
 await create_timer(1.0).timeout
 if ending:return
 ending=true;view.set_physics_process(false);view.set_process(false)
 await _shot("collected.png")
 view.audio.reset();quit()
func _shot(name_: String) -> void:
 for i in 2:await process_frame
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(output.path_join(name_))
func _save() -> void:
 var audio_result := -1
 if recording!=null:
  recording.set_recording_active(false)
  var stream := recording.get_recording()
  if stream!=null:audio_result=stream.save_to_wav(output.path_join("actual-game-mix.wav"))
  AudioServer.remove_bus_effect(0,record_index)
 var missing := not view.effects.item_nodes.has(target)
 for row in view.effects.layout26_records:if int(row.uid)==target:missing=false
 var file := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE)
 file.store_string(JSON.stringify({"checkpoint":checkpoint,"target_uid":target,"pickup_tick":picked,"final_tick":view.run.tick,"pilot":view._pilot,"profile_off":view._profile_off,"fx_script":view.effects.get_script().resource_path,"name_and_node_removed":missing,"native_inputs":input_log,"audio_save_result":audio_result,"actual_final_readback":str(root.get_texture().get_image().get_size()),"scope":"Actual26 EXE/PCK normal earned checkpoint then real native click/original input controller. Master-bus game output WAV recorded during active segment; not microphone or hearing approval. Not whole manual/performance."},"\t"));file.close()
