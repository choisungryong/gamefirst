from pathlib import Path
import json,shutil,hashlib,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent
STAGE=Path('C:/Project/game-research/build-staging/chapter1-elements-20261101-03');OUT=BASE/'elements14/arena03';assert not STAGE.exists()and not OUT.exists();STAGE.mkdir();OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((BASE/'full13/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));assert all(sha(ROOT/n)==h for n,h in pins.items())
old=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-13');pins=json.loads((BASE/'full13/build/staging-manifest.json').read_text(encoding='utf-8'))
for n,h in pins.items():
 assert sha(old/n)==h
 p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for n in ['chapter_elements_quality14.gd','comet_quality14.gdshader','impact_quality14.gdshader','arc_quality14.gdshader']:shutil.copy2(ROOT/'chapter1/view'/n,STAGE/'chapter1/view'/n)
p=STAGE/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('chapter_effects_quality10.gd','chapter_elements_quality14.gd'),encoding='utf-8')
p=STAGE/'project.godot';p.write_text(p.read_text(encoding='utf-8').replace('Quality13','Elements14Arena03'),encoding='utf-8')
for script,node in [('elements_fixture14.gd','ElementsFixture'),('elements_caps14.gd','ElementsCaps')]:
 shutil.copy2(HERE/script,STAGE/script)
 (STAGE/(node+'.tscn')).write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://'+script+'" id="1"]\n[node name="'+node+'" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
(OUT/'stage.json').write_text(json.dumps({'stage':str(STAGE),'pins':{str(p.relative_to(STAGE)).replace('\\','/'):sha(p)for p in STAGE.rglob('*')if p.is_file()},'scope':'Refined elements14 actual-core arena plus separate synthetic caps; root13 runtime still frozen'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('caps',['--headless','res://ElementsCaps.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus']),('gpu',['--fixed-fps','60','res://ElementsFixture.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=14','--elements-variant=after14'])]:
 command=[engine,'--path',str(STAGE)]+args
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(command,stdout=stdout,stderr=stderr);(OUT/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':command},indent=2),encoding='utf-8');print(json.dumps({'label':label,'pid':p.pid}),flush=True)
  code=p.wait(timeout=160)
 report={'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};(OUT/(label+'-execution.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
 if code!=0 or report['stderr_bytes']:raise RuntimeError(label)
shutil.copy2(STAGE/'caps-result.json',OUT/'caps-result.json');shutil.copy2(STAGE/'elements-result.json',OUT/'result.json');shutil.copytree(STAGE/'fixture-captures',OUT/'captures')
a=json.loads((OUT/'result.json').read_text(encoding='utf-8'));b=json.loads((BASE/'elements14/arena02/before13/result.json').read_text(encoding='utf-8'));same={k:a[k]==b[k]for k in ['tick','kills','counts','max_frozen','metrics','hero','growth']};assert all(same.values()),same
(OUT/'COMPARISON.json').write_text(json.dumps({'same_core_arena':same,'after':a,'scope':'Refined14 actual-core configured arena vs retained13arena02. Fixed60 GPU, not normal whole chapter/manual/performance/art approval.'},indent=2),encoding='utf-8');print(json.dumps({'same':same,'counts':a['counts']}),flush=True)
