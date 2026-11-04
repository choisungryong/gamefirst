from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full19'
assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(read(B/'motion19/fixture02/RESULT.json')['checks'].values())
crowd=read(B/'motion19/crowd02/rig19-result.json');assert crowd['core_restored'] and crowd['actors']==180 and crowd['p95_ms']<16.67
freeze=read(B/'full18/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
old_exes={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in (R/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')}
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before19-20261102-01');assert not backup.exists();backup.mkdir()
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'root18-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_actors_quality17.gd')==1;p.write_text(s.replace('chapter_actors_quality17.gd','chapter_actors_batched19.gd'),encoding='utf-8')
source=(B/'full18/package_full18.py').read_text(encoding='utf-8').replace('candidate18','candidate19').replace('20261102-18','20261102-19').replace('Quality18','Quality19').replace('==108','==111')
source=source.replace("'chapter1/view/chapter_world_quality18.gd']","'chapter1/view/chapter_world_quality18.gd','chapter1/view/chapter_actors_demon19.gd','chapter1/view/chapter_actors_readable19.gd','chapter1/view/chapter_actors_batched19.gd']")
start=source.index("SCOPE='");end=source.index('\n',start)
source=source[:start]+"SCOPE='Full chapter candidate19: actual73bone ordinary/middle-elite motion, readable tint/shoulder armor, one-surface shared mesh and no ordinary directional shadow. Existing hero/final boss/ranged/charger unchanged. Core16/FX16/HUD17/World18 preserved. Not final art/manual/audio/formal performance approval.'"+source[end:]
source=source.replace('Only decorative ground-plane extent/cached viewport calculation added. Full17 complete three-primary core proofs preserved; no new full18 run claimed.','Only Actor presentation changed. Full17 complete three-primary core proofs preserved, unchanged16 combat sources; no new full19 whole run claimed.')
(O/'package_full19.py').write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보19\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n일반 적과 중간 정예를 실제 골격 동작으로 바꾼 개발 후보입니다. 냉기 사체 제거/공격 실제 시점 연결, 일반·정예 색/어깨 구분. 영웅/최종 보스/원거리/돌진은 기존 경로이며 추가 품질 개선 대상입니다. Quality19 고유 저장 경로를 쓰며 기존 저장을 옮기지 않습니다. 최종 품질·수동·음향·실전 성능 검수 미완료.\n',encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved18_stage':read(B/'full18/build/closure.json')['stage'],'preserved_exes':old_exes,'fixtures':str(B/'motion19/fixture02/RESULT.json'),'crowd':crowd,'unchanged_core_fx_hud_world':True,'scope':'Development adoption; actual packaged visual/fullrun/native save/audio/performance gates remain open.'},indent=2),encoding='utf-8')
assert all(sha(R/n)==h for n,h in old_exes.items())
print(O,flush=True)
