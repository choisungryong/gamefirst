from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full31';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
assert all(sha(R/n)==h for n,h in read(B/'full30/FINAL-SOURCE-FREEZE.json').items())
assert all(r['core_equal'] for r in read(B/'space31/cost01/COMPARISON.json')['runs'])
for n in ['chapter_world_quality31.gd','chapter_world_quality31b.gd','chapter_world_quality31c.gd']:assert sha(R/'chapter1/view'/n)==read(B/'space31/cost01/source.json')['pins']['chapter1/view/'+n]
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before31-20261105-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
pins=read(B/'full30/ADOPTION.json')['preserved_exes'];build=read(B/'full30/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace('\\','/')]=build['sha256'];assert all(sha(R/n)==h for n,h in pins.items())
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full30/FINAL-SOURCE-FREEZE.json',backup/'root30-freeze.json')
users={}
for ns in ['AshenCloisterChapterOneQuality23','AshenCloisterChapterOneQuality29']:
 folder=Path('C:/Users/twins/AppData/Roaming')/ns;assert folder.exists();dest=backup/'user-profiles'/ns;dest.mkdir(parents=True)
 for p in folder.glob('chapter-one-profile-v1*.json'):shutil.copy2(p,dest/p.name);users[str(p)]=sha(p)
assert len(users)>=6
wrapper=R/'chapter1/view/chapter_world_quality31d.gd';assert not wrapper.exists();wrapper.write_text('extends "res://chapter1/view/chapter_world_quality31c.gd"\n## Product default for the reviewed narrower shadow-only proxies.\nfunc setup(owner: Node3D) -> void:\n\tsuper.setup(owner)\n\tset_columns31(true)\n',encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_world_quality22.gd')==1;p.write_text(s.replace('chapter_world_quality22.gd','chapter_world_quality31d.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,user_pins=users,scope='World22 to31d only;31d enables reviewed31c shadow proxies after setup. Original ornate sprites/anchors/contact retained; no core/light/collider changes. Two shadow batches/33 columns. Final quality gates remain open.'),indent=2))
s=(B/'full30/package_full30.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261104-30','chapter1-full-candidate-20261105-31').replace('Quality30','Quality31').replace('candidate30 workflow','candidate31 workflow').replace('==127','==131')
s=s.replace("'chapter1/view/chapter_actors_quality30c.gd']","'chapter1/view/chapter_actors_quality30c.gd','chapter1/view/chapter_world_quality31.gd','chapter1/view/chapter_world_quality31b.gd','chapter1/view/chapter_world_quality31c.gd','chapter1/view/chapter_world_quality31d.gd']")
s=re.sub(r'^SCOPE=.*$',"SCOPE="+repr('Candidate31: Core16/World31d/Actor30c/HUD27/Input21/FX26. Original ornate columns with narrower directional shadow-only proxies. Source comparative visual and10sec cost tests passed; actual package visual/whole/manual/hearing/final focused performance remain separate.'),s,flags=re.M).replace('Only actor proportions/presentation changed from29. Prior core16 results retain their scope; no new full30 whole run claimed.','Only world column shadows changed from30. Prior core16 results retain their scope; no new full31 whole run claimed.')
p=O/'package_full31.py';p.write_text(s,encoding='utf-8');(O/'RUN.ko.md').write_text('# 후보31\n\n기존 기둥 장식을 보존하면서 바닥 방향 그림자를 보강한 검수 후보입니다. 별도 Quality31 저장 경로. 기존 후보·사용자 저장은 보존합니다. 최종 품질 검수는 진행 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(p),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True);subprocess.run([sys.executable,str(p),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in users.items());print('PACKAGE31 COMPLETE',flush=True)
