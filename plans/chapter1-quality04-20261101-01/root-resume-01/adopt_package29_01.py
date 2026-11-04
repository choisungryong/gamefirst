from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full29'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(B/'space29/shadow01/RESULT.json')['all_same'] and all(r['core_equal'] for r in read(B/'space29/cost01/COMPARISON.json')['runs'])
assert sha(R/'chapter1/view/chapter_actors_quality29.gd')==read(B/'space29/cost01/source.json')['pins']['chapter1/view/chapter_actors_quality29.gd']
frozen=read(B/'full28/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in frozen.items())
pins=read(B/'full28/ADOPTION.json')['preserved_exes'];build=read(B/'full28/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace('\\','/')]=build['sha256'];assert all(sha(R/n)==h for n,h in pins.items())
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before29-20261104-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full28/FINAL-SOURCE-FREEZE.json',backup/'root28-freeze.json')
assembly=R/'chapter1/chapter_one_view.gd';s=assembly.read_text(encoding='utf-8');assert s.count('chapter_actors_quality28.gd')==1;assembly.write_text(s.replace('chapter_actors_quality28.gd','chapter_actors_quality29.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,scope='Only Actor28->29 assembly and Actor29 shadow dependency. World22/HUD27/FX26 unchanged. SSAO World29 and floor27 studies not adopted.'),indent=2),encoding='utf-8')
source=(B/'full28/package_full28.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261104-28','chapter1-full-candidate-20261104-29').replace('Quality28','Quality29').replace('candidate28 workflow','candidate29 workflow')
source=source.replace("'chapter1/view/chapter_actors_quality28.gd']","'chapter1/view/chapter_actors_quality28.gd','chapter1/view/chapter_actors_quality29.gd']").replace('==125','==126')
scope='Full chapter candidate29: existing ordinary/middle-elite model meshes cast directional shadows using the existing moon, improving ground contact. Core16/World22/Actor29/HUD27/Input21/FX26; no extra geometry/light or combat-rule changes. SSAO World29 and floor27 studies not adopted. Actual package/manual/hearing/final performance gates separate.'
source=re.sub(r'^SCOPE=.*$','SCOPE='+repr(scope),source,flags=re.M)
source=source.replace('Only actor presentation changed from27. Prior simulation results apply to unchanged core16 only; no new full28 whole run claimed.','Only ordinary model shadow casting changed from28. Prior results apply to unchanged core16 only; no new full29 whole run claimed.')
script=O/'package_full29.py';script.write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보29\n\nAshenCloister-Chapter1.exe를 실행합니다. 일반 적과 중간 정예의 방향성 그림자로 접지감을 보완했습니다. Quality29 별도 저장 경로이며 기존 저장은 변경하지 않습니다. 이전 후보·실패 증거는 보존했습니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(script),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
subprocess.run([sys.executable,str(script),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());print('CANDIDATE29 PACKAGE COMPLETE; ACTUAL GPU PENDING',flush=True)
