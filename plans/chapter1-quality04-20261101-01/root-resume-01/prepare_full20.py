from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full20'
assert not O.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ending=read(B/'ending20/replay02/RESULT.json');assert ending['same_complete_core_as_normal_reference'] and len(ending['checks'])>=15 and all(ending['checks'].values())
assert read(B/'ending20/replay02/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
discovery=read(B/'discovery20/replay04/RESULT.json');assert discovery['same_complete_core_as_independent_policy'] and len(discovery['receipts'])==2
freeze=read(B/'full19/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
tested=read(B/'ending20/replay02/source.json')['pins']
names=['chapter_hud_quality20.gd','chapter_actors_quality20.gd','chapter_elements_quality20.gd']
assert all(sha(R/'chapter1/view'/n)==tested['chapter1/view/'+n] for n in names)
old_exes={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in (R/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')}
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before20-20261102-01');assert not backup.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'root19-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8')
for old,new in [('chapter_hud_quality17.gd','chapter_hud_quality20.gd'),('chapter_actors_batched19.gd','chapter_actors_quality20.gd'),('chapter_elements_quality16.gd','chapter_elements_quality20.gd')]:assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
source=(B/'full19/package_full19.py').read_text(encoding='utf-8').replace('candidate19','candidate20').replace('20261102-19','20261102-20').replace('Quality19','Quality20').replace('==111','==114')
source=source.replace("'chapter1/view/chapter_actors_batched19.gd']","'chapter1/view/chapter_actors_batched19.gd','chapter1/view/chapter_hud_quality20.gd','chapter1/view/chapter_actors_quality20.gd','chapter1/view/chapter_elements_quality20.gd']")
start=source.index("SCOPE='");end=source.index('\n',start)
source=source[:start]+"SCOPE='Full chapter candidate20: actual earned magic/rare discovery, bounded brief card, final-boss collapse and combat-remnant fade while retaining loot. Core16/HUD rules/World18 unchanged, actual rig19 inherited. Not final art/manual/audio/saveUI/formal performance approval.'"+source[end:]
source=source.replace('Only Actor presentation changed. Full17 complete three-primary core proofs preserved, unchanged16 combat sources; no new full19 whole run claimed.','Only Actor/HUD/FX presentation changed. Full17 three-primary and full19 frost whole-run proofs preserved; unchanged16 combat sources, no new full20 whole run claimed.')
(O/'package_full20.py').write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보20\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n실제 마법/희귀 장비 발견을 짧은 상단 카드로 알리고, 보스가 쓰러진 뒤 잔여 전투 표현을 정리해 전리품을 보여주는 개발 후보입니다. 실제 지급/성장/전투 규칙은 그대로입니다. Quality20 고유 저장 경로이며 기존 저장을 옮기지 않습니다. 수동·음향·저장UI·최종 성능·첫 장 품질 검수 미완료.\n',encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved19_stage':read(B/'full19/build/closure.json')['stage'],'preserved_exes':old_exes,'ending_proof':str(B/'ending20/replay02/RESULT.json'),'discovery_proof':str(B/'discovery20/replay04/RESULT.json'),'source_added':names,'unchanged_core_and_world':True,'scope':'Development adoption after visual review, not completion of full chapter quality.'},indent=2),encoding='utf-8')
assert all(sha(R/n)==h for n,h in old_exes.items());print(O,flush=True)
