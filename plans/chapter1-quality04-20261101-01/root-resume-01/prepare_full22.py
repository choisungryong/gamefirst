from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full22';assert not O.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(B/'full21/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
for proof in ['hostile22/compare02','hostile22/replay01','space22/compare04','space22/replay01']:
 assert read(B/proof/'RESULT.json')['same_complete_core']
 assert read(B/proof/'gpu-execution.json')=={'exit':0,'stderr_bytes':0}
tested=read(B/'space22/replay01/source.json')['pins']
added=['chapter1/view/chapter_world_quality22.gd','chapter1/view/chapter_elements_quality22.gd','chapter1/view/comet_hostile22.gdshader']
assert all(sha(R/n)==tested[n] for n in added)
old_exes={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in (R/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')}
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before22-20261103-01');assert not backup.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','chapter1/ChapterOne.tscn','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'root21-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8')
for old,new in [('chapter_world_quality18.gd','chapter_world_quality22.gd'),('chapter_elements_quality20.gd','chapter_elements_quality22.gd')]:
 assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
source=(B/'full21/package_full21.py').read_text(encoding='utf-8').replace('candidate21','candidate22').replace('20261103-21','20261103-22').replace('Quality21','Quality22').replace('==116','==119')
source=source.replace("'chapter1/chapter_one_input21.gd']","'chapter1/chapter_one_input21.gd',"+','.join(repr(n) for n in added)+']')
start=source.index("SCOPE='");end=source.index('\n',start)
source=source[:start]+"SCOPE='Full chapter candidate22: real rear stone arches with distinct ruin states, outward flat normals/clockwise faces, rear foundation replacement; clearer hostile projectile nose at paid center with directional tail. Core16/HUD20/Actor21/Input21 unchanged. Not final art/manual/audio/default-save/formal performance approval.'"+source[end:]
source=source.replace('Actor presentation and full-chapter mouse controller changed. Full17 three-primary/full19 frost proofs preserved; unchanged16 combat simulation, no new full21 whole run claimed. Input fix separately tested.','World and hostile-projectile presentation changed. Prior full17 three-primary/full19 frost proofs retained for unchanged16 simulation only; no new full22 whole run claimed. New partial visual/core comparisons are separate.')
(O/'package_full22.py').write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보22 개발판\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n북쪽 석조 아치의 실제 두께·구역별 붕괴 상태·그림자, 적 탄환의 밝은 중심과 방향 꼬리를 개선했습니다. 전투/성장과21 입력은 유지합니다. Quality22 별도 저장 경로로 기존 사용자 저장을 이동하지 않습니다. 실제 수동 전체·실청취·기본 저장 경로·최종 성능·첫 장 품질은 미완료입니다.\n',encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':old_exes,'preserved21_stage':read(B/'full21/build/closure.json')['stage'],'tested_sources':{n:tested[n] for n in added},'proofs':['hostile22/compare02','hostile22/replay01','space22/compare04','space22/replay01'],'unchanged_core_hud_actor_input':True,'scope':'Development adoption, not final chapter quality approval.'},indent=2),encoding='utf-8')
assert all(sha(R/n)==h for n,h in old_exes.items());print(O,flush=True)
