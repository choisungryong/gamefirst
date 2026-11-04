from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'ending20/replay01';S=Path('C:/Project/game-research/build-staging/chapter1-ending20-replay01')
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path(read(B/'full19/build/closure.json')['stage']);pins=read(B/'full19/build/staging-manifest.json')
for n,h in pins.items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for n in ['chapter_hud_quality20.gd','chapter_actors_quality20.gd','chapter_elements_quality20.gd']:shutil.copy2(R/'chapter1/view'/n,S/'chapter1/view'/n)
p=S/'chapter1/chapter_one_view.gd';text=p.read_text(encoding='utf-8').replace('chapter_hud_quality17.gd','chapter_hud_quality20.gd').replace('chapter_actors_batched19.gd','chapter_actors_quality20.gd').replace('chapter_elements_quality16.gd','chapter_elements_quality20.gd');p.write_text(text,encoding='utf-8')
shutil.copy2(H/'ending20_replay.gd',S/'ending.gd')
(S/'Ending.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://ending.gd" id="1"]\n[node name="Ending" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
frozen={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
write(O/'source.json',{'stage':str(S),'pins':frozen})
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://ending.gd']),('gpu',['res://Ending.tscn','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=3'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);write(O/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(label,p.pid,flush=True);code=p.wait(timeout=180)
 report={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};write(O/(label+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,report
shutil.copy2(S/'ending20-result.json',O/'RESULT.json');shutil.copy2(S/'ending20-start.json',O/'start.json');shutil.copytree(S/'ending20-shots',O/'shots')
report=read(O/'RESULT.json');assert report['same_complete_core_as_normal_reference'] and report['mode']=='victory'
assert all(sha(S/n)==h for n,h in frozen.items())
freeze=read(B/'full19/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items());print('PASS',flush=True)
