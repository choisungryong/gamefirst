from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full24';assert not O.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(B/'full23/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
proof=read(B/'spike24/fixture02/RESULT.json');assert len(proof['checks'])==50 and all(proof['checks'].values())
assert read(B/'spike24/fixture02/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
assert read(B/'spike24/replay01/RESULT.json')['same_complete_core'] and read(B/'spike24/replay01/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
added='chapter1/view/chapter_actors_quality24.gd';tested=read(B/'spike24/fixture02/source.json')['pins'][added];assert sha(R/added)==tested and read(B/'spike24/replay01/source.json')['pins'][added]==tested
old_exes={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in (R/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')}
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before24-20261103-01');assert not backup.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','chapter1/ChapterOne.tscn','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'root23-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_actors_quality21.gd')==1;p.write_text(s.replace('chapter_actors_quality21.gd','chapter_actors_quality24.gd'),encoding='utf-8')
source=(B/'full23/package_full23.py').read_text(encoding='utf-8').replace('candidate23','candidate24').replace('20261103-23','20261103-24').replace('Quality23','Quality24').replace('==120','==121')
source=source.replace("'chapter1/view/chapter_hud_quality23.gd']","'chapter1/view/chapter_hud_quality23.gd','chapter1/view/chapter_actors_quality24.gd']")
start=source.index("SCOPE='");end=source.index('\n',start)
source=source[:start]+"SCOPE='Full chapter candidate24: share immutable imported minion mesh by resource path and kind, avoiding repeated mesh merge/texture reads on each spawn. Independent per-actor material/rig/poses and final boss preserved. Core16/World22/FX22/HUD23/Input21 unchanged; manual/audio/new actual performance gates separate.'"+source[end:]
source=source.replace('Only action-status HUD changed from22. Prior full17 three-primary/full19 frost proofs retained for unchanged16 simulation only; no new full23 whole run claimed.','Only immutable minion mesh cache identity changed from23. Prior full17 three-primary/full19 frost proofs retained for unchanged16 simulation only; no new full24 whole run claimed.')
(O/'package_full24.py').write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보24 개발판\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n적이 새로 나타날 때 같은 메시를 반복 합치던 비용을 줄였습니다. 각 적의 색·빙결·골격·동작과 보스 표현은 유지합니다. Quality24 별도 저장 경로이며 이전 사용자 저장을 이동하지 않습니다. 수동 전체·실청취·새 실제 성능·첫 장 품질은 별도 검수합니다.\n',encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':old_exes,'preserved23_stage':read(B/'full23/build/closure.json')['stage'],'tested_source':{added:tested},'proof':'spike24/fixture02','visual':'spike24/replay01','unchanged_core_world_fx_hud_input':True,'scope':'Development adoption, not final chapter quality approval.'},indent=2),encoding='utf-8')
assert all(sha(R/n)==h for n,h in old_exes.items());print(O,flush=True)
