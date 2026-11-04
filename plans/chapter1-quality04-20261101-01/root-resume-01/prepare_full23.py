from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full23';assert not O.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(B/'full22/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
proof=read(B/'hud23/fixture01/RESULT.json');assert proof['same_complete_core_restored'] and len(proof['records'])==9 and all(v['fits'] and v['two_lines'] and v['inside_viewport'] for v in proof['records'])
assert read(B/'hud23/fixture01/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
added='chapter1/view/chapter_hud_quality23.gd';tested=read(B/'hud23/fixture01/source.json')['pins'][added];assert sha(R/added)==tested
old_exes={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in (R/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')}
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before23-20261103-01');assert not backup.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','chapter1/ChapterOne.tscn','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'root22-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_hud_quality20.gd')==1;p.write_text(s.replace('chapter_hud_quality20.gd','chapter_hud_quality23.gd'),encoding='utf-8')
source=(B/'full22/package_full22.py').read_text(encoding='utf-8').replace('candidate22','candidate23').replace('20261103-22','20261103-23').replace('Quality22','Quality23').replace('==119','==120')
source=source.replace("'chapter1/view/comet_hostile22.gdshader']","'chapter1/view/comet_hostile22.gdshader','chapter1/view/chapter_hud_quality23.gd']")
start=source.index("SCOPE='");end=source.index('\n',start)
source=source[:start]+"SCOPE='Full chapter candidate23: clear two-line dodge and potion HUD, no forced mid-word wrapping. Core16/World22/FX22/Actor21/Input21 unchanged. Manual whole/audio/default-save/formal performance quality gates remain separate.'"+source[end:]
source=source.replace('World and hostile-projectile presentation changed. Prior full17 three-primary/full19 frost proofs retained for unchanged16 simulation only; no new full22 whole run claimed. New partial visual/core comparisons are separate.','Only action-status HUD changed from22. Prior full17 three-primary/full19 frost proofs retained for unchanged16 simulation only; no new full23 whole run claimed.')
(O/'package_full23.py').write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보23 개발판\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n회피 준비·재사용 대기와 회복약을 명확한 두 줄로 표시합니다.22의 배경·적 탄환과 전투·성장을 유지합니다. Quality23 별도 저장 경로로 기존 사용자 저장을 이동하지 않습니다. 수동 전체·음향·기본 저장 지속성·최종 성능·첫 장 품질은 각 증거로 별도 검수합니다.\n',encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':old_exes,'preserved22_stage':read(B/'full22/build/closure.json')['stage'],'tested_source':{added:tested},'proof':'hud23/fixture01','unchanged_core_world_fx_actor_input':True,'scope':'Development adoption, not final chapter quality approval.'},indent=2),encoding='utf-8')
assert all(sha(R/n)==h for n,h in old_exes.items());print(O,flush=True)
