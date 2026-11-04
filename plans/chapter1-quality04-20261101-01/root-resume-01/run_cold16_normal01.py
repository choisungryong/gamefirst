from pathlib import Path
import json,subprocess,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'cold16/normal01';STAGE=Path('C:/Project/game-research/build-staging/chapter1-cold16-normal-20261101-01');assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-14');pins=json.loads((BASE/'full14/build/staging-manifest.json').read_text(encoding='utf-8'))
for n,h in pins.items():
 assert sha(old/n)==h
 p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for n in ['chapter1/core/chapter_run_quality16.gd','chapter1/view/chapter_elements_quality16.gd','chapter1/view/chapter_hud_quality16.gd']:shutil.copy2(ROOT/n,STAGE/n)
p=STAGE/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8').replace('res://chapter1/core/chapter_run.gd','res://chapter1/core/chapter_run_quality16.gd').replace('res://chapter1/view/chapter_elements_quality14.gd','res://chapter1/view/chapter_elements_quality16.gd').replace('res://chapter1/view/chapter_hud.gd','res://chapter1/view/chapter_hud_quality16.gd');p.write_text(s,encoding='utf-8')
p=STAGE/'project.godot';p.write_text(p.read_text(encoding='utf-8').replace('Quality14','Cold16Normal01'),encoding='utf-8')
s=(BASE/'full14/cold-observer01/observer.gd').read_text(encoding='utf-8').replace('COLD_NORMAL_OBSERVER14','COLD_NORMAL_OBSERVER16').replace('Passive external observer on actual packaged14/default core+pilot, headlessfixed60seed90131; no gameplay changes, not GPU/manual/performance','Source16 actualGPU defaultHP/normalpolicy/seed90131; new cold rule, one evolution modal held for screenshot; no grants, not packaged/manual/performance')
s=s.replace('var observer_seq := -1','''var observer_seq := -1
var _evo_armed := false
var _evo_ready := false
var _evo_done := false
var _event_groups := 0
var _next_event := 0
var _shots: Array[Dictionary]=[]
func _pilot_input() -> Vector2:
	if run.mode=="choice" and not _evo_done:
		for card in run.get_offer().get("cards",[]):
			if card.kind=="evolve"and card.skill_id=="chapter1.skill.frost":
				_evo_armed=true
				if not _evo_ready:return Vector2.ZERO
	return super._pilot_input()
func _save_event_shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var path := "res://plans/chapter1-quality04-20261101-01/cold16/normal01/event-captures/"+name_+".png"
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	if not FileAccess.file_exists(path):get_viewport().get_texture().get_image().save_png(path)
''')
s=s.replace('if event.type=="shatter":observed.shatter_events+=1','''if event.type=="shatter":
			observed.shatter_events+=1
			if event.get("cause","")=="cold_death":observed["cold_death_shatters"]=int(observed.get("cold_death_shatters",0))+1
			if _event_groups<6 and run.tick>=_next_event:
				_next_event=run.tick+90;_event_groups+=1
				for offset in [0,6,15]:_shots.append({"group":_event_groups,"tick":run.tick+offset,"offset":offset})''')
s=s.replace('func _print_result() -> void:', '''	observed["peak_shatter_fragments"]=maxi(int(observed.get("peak_shatter_fragments",0)),effects.ice_fragment_batch.multimesh.visible_instance_count)
	if _evo_armed and not _evo_done and run.mode=="choice":
		_evo_done=true
		await _save_event_shot("evolution-frost")
		_evo_ready=true
	var keep: Array[Dictionary]=[]
	for shot in _shots:
		if run.tick>=int(shot.tick):_save_event_shot("shatter-%02d-after%02d"%[shot.group,shot.offset])
		else:keep.append(shot)
	_shots=keep
func _print_result() -> void:''')
(STAGE/'observer.gd').write_text(s,encoding='utf-8');(STAGE/'Observer.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://observer.gd" id="1"]\n[node name="Observer" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
(OUT/'source.json').write_text(json.dumps({'stage':str(STAGE),'pins':{str(p.relative_to(STAGE)).replace('\\','/'):sha(p)for p in STAGE.rglob('*')if p.is_file()},'scope':'Source16 new real cold proc; defaultHP/normal earned growth+items/pilot90131. One evolution modal held for render capture; sim remains paused there. No resource grants/manual/packaged/performance approval.'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';capture=STAGE/'plans/chapter1-quality04-20261101-01/cold16/normal01/captures'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://observer.gd']),('gpu',['res://Observer.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=520','--chapter1-capture-dir='+str(capture)])]:
 cmd=[engine,'--path',str(STAGE)]+args
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'label':label,'pid':p.pid}),flush=True);code=p.wait(timeout=590)
 report={'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};(OUT/(label+'-execution.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
 if code!=0 or report['stderr_bytes']:raise RuntimeError(label)
shutil.copytree(capture,OUT/'captures');events=STAGE/'plans/chapter1-quality04-20261101-01/cold16/normal01/event-captures';shutil.copytree(events,OUT/'event-captures')
rows=(OUT/'gpu.stdout.txt').read_text(encoding='utf-8').splitlines();r=[json.loads(s.split('COLD_NORMAL_OBSERVER16 ',1)[1])for s in rows if'COLD_NORMAL_OBSERVER16 'in s][-1];assert r['mode']=='victory'and r['observed']['shatter_events']>0
(OUT/'RESULT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(r),flush=True)
