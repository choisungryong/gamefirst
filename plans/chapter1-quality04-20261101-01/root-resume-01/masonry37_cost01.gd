extends SceneTree
var folder := ""
var variant := "37b"
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--masonry-cost-dir="):folder=arg.trim_prefix("--masonry-cost-dir=")
  if arg.begins_with("--masonry-cost-world="):variant=arg.trim_prefix("--masonry-cost-world=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 var view=load("res://chapter1/ChapterOne.tscn").instantiate()
 view.world=load("res://chapter1/view/chapter_world_quality%s.gd"%variant).new()
 root.add_child(view);view.set_process(false);view.set_physics_process(false)
 while view.run.tick<9000:view.run.step(view.full_pilot.decide())
 view.actors.reset();view.effects.reset();view.hud.reset()
 view.world.update_camera(Vector2(0,-14),10);view.world.update_camera(Vector2(48,-14),10);view.world.update_camera(Vector2(96,-14),10);view.world.update_camera(view.run.hero.position,10)
 view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
 var frozen: Dictionary=view.run.snapshot().duplicate(true)
 await RenderingServer.frame_post_draw
 var before=root.get_texture().get_image().get_size()
 OS.delta_smoothing=false
 var settings: Dictionary={"actual_before":[before.x,before.y],"window":str(root.size),"scale3d":root.scaling_3d_scale,"msaa":root.msaa_3d,"vsync":DisplayServer.window_get_vsync_mode(root.get_window_id()),"max_fps":Engine.max_fps,"delta_smoothing":OS.delta_smoothing,"rendering_method":RenderingServer.get_current_rendering_method(),"qa_ignore_focus":view._qa_ignore_focus,"display_server":DisplayServer.get_name()}
 if before!=Vector2i(1920,1080) or Engine.max_fps!=0 or settings.vsync!=0:push_error("Static cost preflight failed");quit(1);return
 var warm: int=Time.get_ticks_usec()
 while Time.get_ticks_usec()-warm<2000000:await process_frame
 var rows: Array[Array]=[]
 var start: int=Time.get_ticks_usec();var previous: int=start
 while Time.get_ticks_usec()-start<10000000:
  await process_frame
  var now: int=Time.get_ticks_usec()
  rows.append([now-start,now-previous,int(root.has_focus()),int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))]);previous=now
  if rows.size()>30000:push_error("Static cost capacity exceeded");quit(1);return
 var sample_us: int=previous-start
 var same: bool=frozen==view.run.snapshot()
 await RenderingServer.frame_post_draw
 var after=root.get_texture().get_image().get_size()
 var csv=FileAccess.open(folder.path_join("frames.csv"),FileAccess.WRITE);csv.store_string("elapsed_us,interval_us,focused,draw_calls\n")
 var intervals: Array[int]=[];var focus_false := 0;var draws: Array[int]=[]
 for row in rows:
  csv.store_csv_line(PackedStringArray([str(row[0]),str(row[1]),str(row[2]),str(row[3])]))
  intervals.append(row[1]);focus_false+=1-int(row[2]);draws.append(row[3])
 csv.close();csv=null;intervals.sort();draws.sort()
 var result: Dictionary={"world":variant,"settings":settings,"actual_after":[after.x,after.y],"sample_count":rows.size(),"sample_us":sample_us,"warmup_us":2000000,"unfocused_frames":focus_false,"same_complete_core":same,"snapshot":frozen,"p95_ms":float(intervals[ceili(intervals.size()*.95)-1])/1000.,"p99_ms":float(intervals[ceili(intervals.size()*.99)-1])/1000.,"max_ms":float(intervals[-1])/1000.,"draw_calls_median":draws[draws.size()/2],"raw_sha256":FileAccess.get_sha256(folder.path_join("frames.csv")),"scope":"Exclusive CPU/GPU reservation static frozenCore36 tick9000 normalhero camera;2s warm+10s1run. Auto start/ignorefocus set but actual focus recorded. Pre/post readback only,no image files,no IO/readback in sample. Relative rendering regression screen,not formal dynamic1080p3x."}
 var f=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();f=null
 view.audio.reset();view.queue_free()
 for frame in 4:await process_frame
 view=null;quit(0 if same and after==Vector2i(1920,1080) else 2)
