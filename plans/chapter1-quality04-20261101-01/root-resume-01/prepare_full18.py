from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full18';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
test=read(B/'ground18/matrix01/RESULT.json');assert test['all_new_floor_covers'] and test['core_unchanged'] and len(test['cases'])==36
freeze=read(B/'full17b/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before18-20261102-01');assert not backup.exists();backup.mkdir()
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'root17b-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_world_quality17.gd')==1;p.write_text(s.replace('chapter_world_quality17.gd','chapter_world_quality18.gd'),encoding='utf-8')
source=(B/'full17b/package_full17b.py').read_text(encoding='utf-8').replace('candidate17b','candidate18').replace('20261102-17b','20261102-18').replace('Quality17b','Quality18').replace('==107','==108')
source=source.replace("'chapter1/view/chapter_world_quality17.gd']","'chapter1/view/chapter_world_quality17.gd','chapter1/view/chapter_world_quality18.gd']")
start=source.index("SCOPE='");end=source.index('\n',start)
source=source[:start]+"SCOPE='Full chapter candidate18: viewport-derived single ground plane covers all legal camera targets with3m margin, world-space terrain unchanged. Inherits17b presentation and16 combat. Not final art/manual/audio/formal performance approval.'"+source[end:]
source=source.replace('Only decorative World17 positions changed. Full17 complete three-primary core proofs are preserved and separately compared; this is not a new full17b run.','Only decorative ground-plane extent/cached viewport calculation added. Full17 complete three-primary core proofs preserved; no new full18 run claimed.')
(OUT/'package_full18.py').write_text(source,encoding='utf-8');(OUT/'RUN.ko.md').write_text('# 후보18\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n경계·넓은화면의빈바닥을수정한개발후보입니다.17b장비/보상/사체표현과16전투규칙유지.Quality18고유저장경로를사용하며기존저장을이동하지않습니다.최종품질·수동·음향·성능검수미완료.\n',encoding='utf-8')
(OUT/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved17b_stage':read(B/'full17b/build/closure.json')['stage'],'added_source':'chapter1/view/chapter_world_quality18.gd','source_test':str(B/'ground18/matrix01/RESULT.json'),'no_core_hud_actor_fx_changes':True},indent=2),encoding='utf-8');print(str(OUT),flush=True)
