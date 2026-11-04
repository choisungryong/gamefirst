from pathlib import Path
import json,hashlib,shutil
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';o=b/'full26';assert not o.exists();read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=read(b/'full25b/FINAL-SOURCE-FREEZE.json');assert all(sha(r/n)==h for n,h in f.items())
added='chapter1/view/chapter_elements_quality26.gd';pin=sha(r/added)
for case in ['fixture02','replay02','collection01']:
 assert read(b/f'loot26/{case}/gpu-execution.json')=={'exit':0,'stderr_bytes':0};assert read(b/f'loot26/{case}/source.json')['pins'][added]==pin
assert all(read(b/'loot26/fixture02/RESULT.json')['checks'].values());assert read(b/'loot26/replay02/RESULT.json')['same_complete_core'];collect=read(b/'loot26/collection01/RESULT.json');assert collect['same_complete_core'] and collect['name_and_node_removed'] and collect['pickup_tick']>0
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before26-20261104-01');assert not backup.exists();backup.mkdir();o.mkdir()
for n in ['chapter1/chapter_one_view.gd','chapter1/ChapterOne.tscn','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,p)
(backup/'root25b-freeze.json').write_text(json.dumps(f,indent=2),encoding='utf-8')
p=r/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_elements_quality22.gd')==1;p.write_text(s.replace('chapter_elements_quality22.gd','chapter_elements_quality26.gd'),encoding='utf-8')
s=(b/'full25b/package_full25b.py').read_text(encoding='utf-8').replace('candidate25b','candidate26').replace('20261103-25b','20261104-26').replace('Quality25b','Quality26').replace('==122','==123')
s=s.replace("'chapter1/view/chapter_actors_quality25b.gd']","'chapter1/view/chapter_actors_quality25b.gd','chapter1/view/chapter_elements_quality26.gd']")
start=s.index("SCOPE='");end=s.index('\n',start);s=s[:start]+"SCOPE='Full chapter candidate26: readable nearby ground gear names with camera-scaled text, priority layout and displacement leaders. Core16/World22/Actor25b/HUD23/Input21 and all drop/collection rules preserved. Actor26 hit-blend study not adopted. Actual packaged/manual/audio/new formal performance gates separate.'"+s[end:]
s=s.replace('Only ordinary actor allocation/recycling changed from24.','Only ground-item name presentation changed from25b.').replace('no new full25 whole run claimed.','no new full26 whole run claimed.')
(o/'package_full26.py').write_text(s,encoding='utf-8')
(o/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':{str(p.relative_to(r)).replace('\\','/'):sha(p) for p in (r/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')},'tested_source':{added:pin},'proof':'loot26/fixture02 + replay02 + collection01','unchanged_core_world_actors_hud_input':True,'scope':'Development presentation adoption, not final chapter quality approval.'},indent=2),encoding='utf-8')
(o/'RUN.ko.md').write_text('# 후보26 개발판\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n가까운 장비 이름을 읽기 쉽게 키우고 겹치는 이름의 간격을 조정합니다. 기존 드롭·자동 회수 규칙은 유지합니다. Quality26 별도 저장 경로이며 이전 저장을 이동하지 않습니다. 피격 동작 연구26은 미채택입니다. 실제 제품·수동 전체·음향·최종 성능과 품질 검수는 계속합니다.\n',encoding='utf-8')
print(o)
