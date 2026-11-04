from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full33';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(R/n)==h for n,h in read(B/'full32/FINAL-SOURCE-FREEZE.json').items())
assert read(B/'loot33/compare01/COMPARISON.json')['passed'] and read(B/'flame33/compare01/COMPARISON.json')['passed']
assert all(r['core_equal'] for r in read(B/'loot33/cost01/COMPARISON.json')['runs'])
actor='chapter1/view/chapter_elements_quality33b.gd';assert sha(R/actor)==read(B/'loot33/cost01/source.json')['pins'][actor]
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before33-20261105-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
pins=read(B/'full32/ADOPTION.json')['preserved_exes'];build=read(B/'full32/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace(chr(92),'/')]=build['sha256'];assert all(sha(R/n)==h for n,h in pins.items())
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full32/FINAL-SOURCE-FREEZE.json',backup/'root32-freeze.json')
users={}
for ns in ['AshenCloisterChapterOneQuality23','AshenCloisterChapterOneQuality29']:
 folder=Path('C:/Users/twins/AppData/Roaming')/ns;assert folder.exists();dest=backup/'user-profiles'/ns;dest.mkdir(parents=True)
 for p in folder.glob('chapter-one-profile-v1*.json'):shutil.copy2(p,dest/p.name);users[str(p)]=sha(p)
assert len(users)>=6
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_elements_quality26.gd')==1;p.write_text(s.replace('chapter_elements_quality26.gd','chapter_elements_quality33b.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,user_pins=users,tested_fx_sha256=sha(R/actor),scope='FX26 to33b: lower fire plumes and rarity-specific ground light/label tint/rare halos. Same paid impacts/core16/World31d/Actor32b/HUD27/Input21. Unique color support is not new unique drop generation. Source visual/core/lifetime checks passed; final quality gates open.'),indent=2),encoding='utf-8')
s=(B/'full32/package_full32.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261105-32','chapter1-full-candidate-20261105-33').replace('Quality32','Quality33').replace('candidate32 workflow','candidate33 workflow').replace('==132','==135')
s=s.replace("'chapter1/view/chapter_actors_quality32b.gd']","'chapter1/view/chapter_actors_quality32b.gd','chapter1/view/chapter_elements_quality33.gd','chapter1/view/flame_bloom_quality33.gdshader','chapter1/view/chapter_elements_quality33b.gd']")
s=re.sub(r'^SCOPE=.*$',"SCOPE="+repr('Candidate33: Core16/World31d/Actor32b/HUD27/Input21/FX33b. Lower fire plumes retaining paid ground impacts, clearer existing drop rarity light hierarchy. No damage/generation/collection/save rule changes. Prior actual whole31 and elite32 retain scope; final same-product whole/manual/hearing/focused performance gates remain open.'),s,flags=re.M).replace('Only role upper-body poses changed from31. Prior core16 results retain their scope; no new full32 whole run claimed.','Only fire/ground loot presentation changed from32. Prior core16 results retain their scope; no new full33 whole run claimed.')
p=O/'package_full33.py';p.write_text(s,encoding='utf-8');(O/'RUN.ko.md').write_text('# 후보33\n\n화염 몸가림을 줄이고 바닥 드롭의 등급을 구분한 검수 후보입니다. 별도Quality33 저장 경로. 이전 후보와 사용자 저장은 보존합니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(p),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True);subprocess.run([sys.executable,str(p),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in users.items());print('PACKAGE33 COMPLETE',flush=True)
