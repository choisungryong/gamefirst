from pathlib import Path
import json,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/full14/cold-observer01';assert not OUT.exists();OUT.mkdir()
script=OUT/'observer.gd'
script.write_text('''extends "res://chapter1/chapter_one_view.gd"
var observed := {"frozen_hit_events":0,"shatter_events":0,"normal_frozen_hit_events":0,"normal_frozen_alive_tick_samples":0,"elite_frozen_alive_tick_samples":0,"max_frozen_alive":0,"peak_ice_instances":0}
var observer_seq := -1
func _consume_events() -> void:
	for event in run.events:
		if int(event.seq)<=observer_seq:continue
		observer_seq=int(event.seq)
		if event.type=="shatter":observed.shatter_events+=1
		elif event.type=="hit" and event.get("frozen",false):
			observed.frozen_hit_events+=1
			var e: Dictionary=run.enemies.get(event.target_id,{})
			if not e.is_empty() and not e.elite:observed.normal_frozen_hit_events+=1
	super._consume_events()
func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if run.mode!="playing":return
	var count_ := 0
	for e in run.enemies.values():
		if e.hp_raw<=0 or run.tick>=int(e.frozen_until):continue
		count_+=1
		if e.elite:observed.elite_frozen_alive_tick_samples+=1
		else:observed.normal_frozen_alive_tick_samples+=1
	observed.max_frozen_alive=maxi(observed.max_frozen_alive,count_)
func _process(delta: float) -> void:
	super._process(delta)
	observed.peak_ice_instances=maxi(observed.peak_ice_instances,effects.ice_batch.multimesh.visible_instance_count)
func _print_result() -> void:
	super._print_result()
	print("COLD_NORMAL_OBSERVER14 ",JSON.stringify({"mode":run.mode,"tick":run.tick,"observed":observed,"scope":"Passive external observer on actual packaged14/default core+pilot, headlessfixed60seed90131; no gameplay changes, not GPU/manual/performance"}))
''',encoding='utf-8')
runner=OUT/'runner.gd';runner.write_text('extends SceneTree\nfunc _initialize() -> void:call_deferred("execute")\nfunc execute() -> void:\n\troot.add_child(load("'+script.as_posix()+'").new())\n',encoding='utf-8')
exe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'
cmd=[str(exe),'--headless','--fixed-fps','60','--script',str(runner),'--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=500']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'pid':p.pid}),flush=True);code=p.wait(timeout=180)
report={'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(report,indent=2),encoding='utf-8');assert code==0 and not report['stderr_bytes'],report
rows=(OUT/'stdout.txt').read_text(encoding='utf-8').splitlines();observed=[json.loads(s.split('COLD_NORMAL_OBSERVER14 ',1)[1])for s in rows if 'COLD_NORMAL_OBSERVER14 'in s];assert observed and observed[-1]['mode']=='victory'
(OUT/'RESULT.json').write_text(json.dumps(observed[-1],indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(observed[-1]),flush=True)
