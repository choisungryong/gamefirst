from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full32';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(R/n)==h for n,h in read(B/'full31/FINAL-SOURCE-FREEZE.json').items())
assert read(B/'motion32/directions01/gpu/RESULT.json')['passed'] and read(B/'motion32/mapped02/COMPARISON.json')['passed']
assert all(r['core_equal'] for r in read(B/'motion32/cost01/COMPARISON.json')['runs'])
actor='chapter1/view/chapter_actors_quality32b.gd';assert sha(R/actor)==read(B/'motion32/cost01/source.json')['pins'][actor]
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before32-20261105-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
pins=read(B/'full31/ADOPTION.json')['preserved_exes'];build=read(B/'full31/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace(chr(92),'/')]=build['sha256'];assert all(sha(R/n)==h for n,h in pins.items())
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full31/FINAL-SOURCE-FREEZE.json',backup/'root31-freeze.json')
users={}
for ns in ['AshenCloisterChapterOneQuality23','AshenCloisterChapterOneQuality29']:
 folder=Path('C:/Users/twins/AppData/Roaming')/ns;assert folder.exists();dest=backup/'user-profiles'/ns;dest.mkdir(parents=True)
 for p in folder.glob('chapter-one-profile-v1*.json'):shutil.copy2(p,dest/p.name);users[str(p)]=sha(p)
assert len(users)>=6
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_actors_quality30c.gd')==1;p.write_text(s.replace('chapter_actors_quality30c.gd','chapter_actors_quality32b.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,user_pins=users,tested_actor_sha256=sha(R/actor),scope='Actor30c to32b only. Role-specific upper-body anticipation/recovery, original paid clips/core16/World31d/HUD27/Input21/FX26 retained. Modal/frozen/lower-body/pool checks and source frame/core comparison passed. Final quality gates open.'),indent=2),encoding='utf-8')
s=(B/'full31/package_full31.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261105-31','chapter1-full-candidate-20261105-32').replace('Quality31','Quality32').replace('candidate31 workflow','candidate32 workflow').replace('==131','==132')
s=s.replace("'chapter1/view/chapter_world_quality31d.gd']","'chapter1/view/chapter_world_quality31d.gd','chapter1/view/chapter_actors_quality32b.gd']")
s=re.sub(r'^SCOPE=.*$',"SCOPE="+repr('Candidate32: Core16/World31d/Actor32b/HUD27/Input21/FX26. Distinct ordinary/elite upper-body anticipation and recovery while retaining paid attack timing, lower-body, frozen/modal pose, hit28, role proportions and224pool. Source tests support adoption, not manual/hearing/final focused performance or final-art approval.'),s,flags=re.M).replace('Only world column shadows changed from30. Prior core16 results retain their scope; no new full31 whole run claimed.','Only role upper-body poses changed from31. Prior core16 results retain their scope; no new full32 whole run claimed.')
p=O/'package_full32.py';p.write_text(s,encoding='utf-8');(O/'RUN.ko.md').write_text('# 후보32\n\n일반 적·정예의 준비 및 회복 자세를 구분한 검수 후보입니다. 별도Quality32 저장 경로. 이전 후보와 사용자 저장은 보존합니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(p),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True);subprocess.run([sys.executable,str(p),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in users.items());print('PACKAGE32 COMPLETE',flush=True)
