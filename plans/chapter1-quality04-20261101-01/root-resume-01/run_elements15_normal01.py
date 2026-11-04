from pathlib import Path
import hashlib,json,shutil,subprocess,time
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'elements15/normal01';STAGE=Path('C:/Project/game-research/build-staging/chapter1-elements15-normal-20261101-01');assert not OUT.exists()and not STAGE.exists();OUT.mkdir(parents=True);STAGE.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((BASE/'full14/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));assert all(sha(ROOT/n)==h for n,h in pins.items())
old=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-14');pins=json.loads((BASE/'full14/build/staging-manifest.json').read_text(encoding='utf-8'))
for n,h in pins.items():
 assert sha(old/n)==h
 p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(ROOT/'chapter1/view/chapter_elements_quality15.gd',STAGE/'chapter1/view/chapter_elements_quality15.gd')
p=STAGE/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('chapter_elements_quality14.gd','chapter_elements_quality15.gd'),encoding='utf-8')
p=STAGE/'project.godot';p.write_text(p.read_text(encoding='utf-8').replace('Quality14','Elements15Normal01'),encoding='utf-8')
s=(BASE/'full14/cold-observer01/observer.gd').read_text(encoding='utf-8').replace('COLD_NORMAL_OBSERVER14','COLD_NORMAL_OBSERVER15').replace('Passive external observer on actual packaged14/default core+pilot, headlessfixed60seed90131; no gameplay changes, not GPU/manual/performance','Source15 realGPU/default normal core+pilot/seed90131, partial190wallsec; no supplied HP/rank, not packaged/manual/fullchapter/performance')
s=s.replace('func _print_result() -> void:\n\tsuper._print_result()','func _print_result() -> void:\n\tobserved["cold_death_accents"]=effects.cold_death_accents\n\tsuper._print_result()')
(STAGE/'observer.gd').write_text(s,encoding='utf-8');(STAGE/'Observer.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://observer.gd" id="1"]\n[node name="Observer" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
(OUT/'source.json').write_text(json.dumps({'stage':str(STAGE),'root14_freeze_matches_before':True,'pins':{str(p.relative_to(STAGE)).replace('\\','/'):sha(p)for p in STAGE.rglob('*')if p.is_file()},'scope':'Source15 actual normal default HP/progression/seed90131, cold kill debris cosmetic; not new freeze/shatter damage.190wallseconds partialGPU only.'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';capture=STAGE/'plans/chapter1-quality04-20261101-01/elements15/normal01/captures'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://observer.gd']),('gpu',['res://Observer.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=190','--chapter1-capture-dir='+str(capture)])]:
 cmd=[engine,'--path',str(STAGE)]+args
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'label':label,'pid':p.pid}),flush=True);code=p.wait(timeout=280)
 report={'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};(OUT/(label+'-execution.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
 if code!=0 or report['stderr_bytes']:raise RuntimeError(label)
shutil.copytree(capture,OUT/'captures')
rows=(OUT/'gpu.stdout.txt').read_text(encoding='utf-8').splitlines();r=[json.loads(s.split('COLD_NORMAL_OBSERVER15 ',1)[1])for s in rows if'COLD_NORMAL_OBSERVER15 'in s][-1]
assert r['observed']['cold_death_accents']>0,r
(OUT/'RESULT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(r),flush=True)
