from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full30';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(B/'crowd30/equivalence03/RESULT.json')['passed'] and read(B/'crowd30/mapped01/COMPARISON.json')['passed'];assert all(r['core_equal'] for r in read(B/'crowd30/cost02/COMPARISON.json')['runs'])
actor='chapter1/view/chapter_actors_quality30c.gd';assert sha(R/actor)==read(B/'crowd30/cost02/source.json')['pins'][actor]
frozen=read(B/'full29/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in frozen.items())
pins=read(B/'full29/ADOPTION.json')['preserved_exes'];build=read(B/'full29/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace('\\','/')]=build['sha256'];assert all(sha(R/n)==h for n,h in pins.items())
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before30-20261104-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full29/FINAL-SOURCE-FREEZE.json',backup/'root29-freeze.json')
user_pins={}
for namespace in ['AshenCloisterChapterOneQuality23','AshenCloisterChapterOneQuality29']:
 folder=Path('C:/Users/twins/AppData/Roaming')/namespace;assert folder.exists();dest=backup/'user-profiles'/namespace;dest.mkdir(parents=True)
 for p in folder.glob('chapter-one-profile-v1*.json'):shutil.copy2(p,dest/p.name);user_pins[str(p)]=sha(p)
assert len(user_pins)>=6
assembly=R/'chapter1/chapter_one_view.gd';s=assembly.read_text(encoding='utf-8');assert s.count('chapter_actors_quality29.gd')==1;assembly.write_text(s.replace('chapter_actors_quality29.gd','chapter_actors_quality30c.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,user_pins=user_pins,tested_actor_sha256=sha(R/actor),scope='Only Actor29->30c assembly plus same tested30c source. Four role-preserving body/head/shoulder/arm proportions selected by stable entity ID, cached pose restoration. Core16/World22/HUD27/Input21/FX26 retained. Source stage tests support candidate adoption, not final quality completion.'),indent=2))
source=(B/'full29/package_full29.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261104-29','chapter1-full-candidate-20261104-30').replace('Quality29','Quality30').replace('candidate29 workflow','candidate30 workflow')
source=source.replace("'chapter1/view/chapter_actors_quality29.gd']","'chapter1/view/chapter_actors_quality29.gd','chapter1/view/chapter_actors_quality30c.gd']").replace('==126','==127')
scope='Full chapter candidate30: same tested30c ordinary role silhouette proportions, cached bone bases; existing hit28, paid recover facing29 shadow and224 pool retained. Core16/World22/Actor30c/HUD27/Input21/FX26. Modest same-family variation, not new monster species. No geometry or combat-rule additions. Manual/hearing/final performance/whole final quality gates remain separate.'
source=re.sub(r'^SCOPE=.*$','SCOPE='+repr(scope),source,flags=re.M).replace('Only ordinary model shadow casting changed from28. Prior results apply to unchanged core16 only; no new full29 whole run claimed.','Only actor proportions/presentation changed from29. Prior core16 results retain their scope; no new full30 whole run claimed.')
script=O/'package_full30.py';script.write_text(source,encoding='utf-8');(O/'RUN.ko.md').write_text('# 후보30\n\n일반 적의 역할별 체형 변형을 반영한 검수 후보입니다. AshenCloister-Chapter1.exe로 실행합니다. 별도Quality30 저장 경로이며 기존23·29 저장과 후보는 보존합니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(script),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True);subprocess.run([sys.executable,str(script),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in user_pins.items());print('CANDIDATE30 PACKAGE COMPLETE; ACTUAL GPU PENDING',flush=True)
