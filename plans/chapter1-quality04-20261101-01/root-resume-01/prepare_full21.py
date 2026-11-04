from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full21';assert not O.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(read(B/'roles21/fixture02/RESULT.json')['checks'].values());assert all(read(B/'input21/fixture02/RESULT.json')['checks'].values())
assert read(B/'roles21/fixture02/gpu-execution.json')=={'exit':0,'stderr_bytes':0};assert read(B/'input21/fixture02/fixture-execution.json')=={'exit':0,'stderr_bytes':0}
freeze=read(B/'full20/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
assert sha(R/'chapter1/view/chapter_actors_quality21.gd')==read(B/'roles21/fixture02/source.json')['pins']['chapter1/view/chapter_actors_quality21.gd']
assert sha(R/'chapter1/chapter_one_input21.gd')==read(B/'input21/fixture02/source.json')['pins']['chapter1/chapter_one_input21.gd']
old_exes={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in (R/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')}
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before21-20261103-01');assert not backup.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','chapter1/ChapterOne.tscn','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'root20-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_actors_quality20.gd')==1;p.write_text(s.replace('chapter_actors_quality20.gd','chapter_actors_quality21.gd'),encoding='utf-8')
p=R/'chapter1/ChapterOne.tscn';s=p.read_text(encoding='utf-8');assert s.count('chapter_one_view.gd')==1;p.write_text(s.replace('chapter_one_view.gd','chapter_one_input21.gd'),encoding='utf-8')
source=(B/'full20/package_full20.py').read_text(encoding='utf-8').replace('candidate20','candidate21').replace('20261102-20','20261103-21').replace('Quality20','Quality21').replace('==114','==116')
source=source.replace("'chapter1/view/chapter_elements_quality20.gd']","'chapter1/view/chapter_elements_quality20.gd','chapter1/view/chapter_actors_quality21.gd','chapter1/chapter_one_input21.gd']")
start=source.index("SCOPE='");end=source.index('\n',start)
source=source[:start]+"SCOPE='Full chapter candidate21: rigged ranged/charger roles, shared single-surface staff, paid dash/recovery and bounded distant pose updates. Full-chapter click target uses unlocked core bounds, fixing later-zone first-arena clamp. Core16/World18/HUD20/FX20 unchanged. Not final art/manual/audio/save-path/formal performance approval.'"+source[end:]
source=source.replace('Only Actor/HUD/FX presentation changed. Full17 three-primary and full19 frost whole-run proofs preserved; unchanged16 combat sources, no new full20 whole run claimed.','Actor presentation and full-chapter mouse controller changed. Full17 three-primary/full19 frost proofs preserved; unchanged16 combat simulation, no new full21 whole run claimed. Input fix separately tested.')
(O/'package_full21.py').write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보21\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n원거리·돌진 적도 실제 골격 동작으로 연결하고, 후반 구역의 클릭 목표가 첫 구역으로 잘못 제한되던 문제를 수정했습니다. 기존 발견·보스 마무리·전투 규칙은 유지합니다. Quality21 고유 저장 경로이며 기존 저장을 옮기지 않습니다. 수동·음향·기본 저장 경로·최종 성능·첫 장 품질 검수 미완료.\n',encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':old_exes,'preserved20_stage':read(B/'full20/build/closure.json')['stage'],'role_proof':str(B/'roles21/fixture02/RESULT.json'),'input_proof':str(B/'input21/fixture02/RESULT.json'),'mixed_crowd':str(B/'roles21/crowd02/RESULT.json'),'unchanged_core_world_hud_fx':True,'scope':'Development adoption, not final chapter quality approval.'},indent=2),encoding='utf-8')
assert all(sha(R/n)==h for n,h in old_exes.items());print(O,flush=True)
