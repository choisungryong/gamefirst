from pathlib import Path
import json,hashlib,shutil
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';o=b/'full25';assert not o.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=read(b/'full24/FINAL-SOURCE-FREEZE.json');assert all(sha(r/n)==v for n,v in f.items())
added='chapter1/view/chapter_actors_quality25_warm.gd';pin=sha(r/added)
for case in ['warm-fixture01','warm-fixture02','warm-replay01','warm-profile01']:
 assert read(b/f'pool25/{case}/gpu-execution.json')=={'exit':0,'stderr_bytes':0};assert read(b/f'pool25/{case}/source.json')['pins'][added]==pin
assert all(read(b/'pool25/warm-fixture02/RESULT.json')['checks'].values())
assert read(b/'pool25/warm-replay01/RESULT.json')['same_complete_core']
comparison=read(b/'pool25/source-performance/MATCHED-COMPARISON01.json')['runs'];assert comparison['trial02']['audit']['valid'] and comparison['control01']['audit']['valid'];assert comparison['trial02']['over_33330_us']<comparison['control01']['over_33330_us']
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before25-20261103-01');assert not backup.exists();backup.mkdir();o.mkdir()
for n in ['chapter1/chapter_one_view.gd','chapter1/ChapterOne.tscn','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,p)
(backup/'root24-freeze.json').write_text(json.dumps(f,indent=2),encoding='utf-8')
p=r/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_actors_quality24.gd')==1;p.write_text(s.replace('chapter_actors_quality24.gd','chapter_actors_quality25_warm.gd'),encoding='utf-8')
s=(b/'full24/package_full24.py').read_text(encoding='utf-8').replace('candidate24','candidate25').replace('20261103-24','20261103-25').replace('Quality24','Quality25').replace('==121','==122')
s=s.replace("'chapter1/view/chapter_actors_quality24.gd']","'chapter1/view/chapter_actors_quality24.gd','chapter1/view/chapter_actors_quality25_warm.gd']")
start=s.index("SCOPE='");end=s.index('\n',start);s=s[:start]+"SCOPE='Full chapter candidate25: preallocate224 ordinary actor presenters before menu and recycle only removed core entities by kind. Retained corpses and elite/final boss lifetime preserved. Core16/World22/FX22/HUD23/Input21 unchanged. One matched source experiment reduced long frames; packaged actual/manual/audio/final3run quality approval remains separate.'"+s[end:]
s=s.replace('Only immutable minion mesh cache identity changed from23.','Only ordinary actor allocation/recycling changed from24.').replace('no new full24 whole run claimed.','no new full25 whole run claimed.')
(o/'package_full25.py').write_text(s,encoding='utf-8')
(o/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':{str(p.relative_to(r)).replace('\\','/'):sha(p) for p in (r/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')},'tested_source':{added:pin},'proof':'pool25/warm-fixture01 + warm-fixture02 + warm-replay01 + source-performance/MATCHED-COMPARISON01.json','scope':'Development adoption, not final chapter quality approval.'},indent=2),encoding='utf-8')
(o/'RUN.ko.md').write_text('# 후보25 개발판\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.\n\n일반 적 표시 노드를 메뉴 전에 준비해 전투 중 반복 생성 비용을 줄입니다. Quality25 별도 저장 경로이며 과거 저장은 이동하지 않습니다. 실제 제품 성능·수동 전체·실청취·최종 품질 검수는 남아 있습니다.\n',encoding='utf-8')
print(o)
