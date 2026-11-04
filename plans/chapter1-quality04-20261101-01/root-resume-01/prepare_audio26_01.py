from pathlib import Path
h=Path('plans/chapter1-quality04-20261101-01/root-resume-01')
s='''extends SceneTree
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
 f.store_string(JSON.stringify({"primary":view.primary,"start_tick":start_tick,"final_tick":view.run.tick,"zone":view.run.zone,"mode":view.run.mode,"same_complete_core":same,"played":view.audio.played-played_before,"dropped":view.audio.dropped-dropped_before,"cue_counts":cues,"master_volume":view.audio.master_volume,"muted":view.audio.muted,"wav_save_result":code,"scope":"Actual26 packaged normal earned16000tick checkpoint then14s real-time live combat Master-bus recording. Other learned skills remain active. Independent final core match; no microphone/hearing/manual/formal-performance approval."},"\\t"));f.close()
 view.audio.reset()
 for i in 4:await process_frame
 quit(0 if same and code==OK else 1)
'''
(h/'audio26_observer.gd').write_text(s,encoding='utf-8')
s='''from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;BASE=B/'full26/audio';BASE.mkdir(exist_ok=True);read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=read(B/'full26/build/build.json');exe=Path(build['exe']);script=H/'audio26_observer.gd';assert sha(exe)==build['sha256']
for primary in ['ember','frost','arc']:
 o=BASE/(primary+'01');runtime=exe.parent/('qa-probe/audio-'+primary+'01');assert not o.exists() and not runtime.exists();o.mkdir();shutil.copy2(script,o/script.name)
 for label,args in [('check',['--headless','--check-only','--script',str(script)]),('gpu',['--script',str(script),'--resolution','1920x1080','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-seed=90131','--chapter1-primary=chapter1.skill.'+primary,'--audio26-dir='+str(runtime)])]:
  cmd=[str(exe)]+args
  with (o/(label+'.stdout.txt')).open('xb') as out,(o/(label+'.stderr.txt')).open('xb') as err:
   p=subprocess.Popen(cmd,stdout=out,stderr=err);(o/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(script)},indent=2));print(primary,label,p.pid,flush=True);code=p.wait(timeout=150)
  d={'exit':code,'stderr_bytes':(o/(label+'.stderr.txt')).stat().st_size};(o/(label+'-execution.json')).write_text(json.dumps(d));assert code==0 and d['stderr_bytes']==0
 shutil.copytree(runtime,o/'proof');assert read(o/'proof/RESULT.json')['same_complete_core'];assert sha(exe)==build['sha256'];print(primary,'PASS',flush=True)
'''
(h/'run_audio26_01.py').write_text(s,encoding='utf-8')
