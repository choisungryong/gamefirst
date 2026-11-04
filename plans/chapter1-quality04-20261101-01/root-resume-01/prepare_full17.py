from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17';assert not OUT.exists();OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
review=read(B/'presentation17/review04/RESULT.json');assert all(v for row in review['same_core'].values() for v in row.values()) and all(review['after_checks'].values())
freeze=read(B/'full16/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before17-20261102-01');assert not backup.exists();backup.mkdir()
for n,h in freeze.items():
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(backup/'manifest.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
exe_pins={}
for candidate in ['20261101-14','20261101-16']:
 p=R/('builds/chapter1/chapter1-full-candidate-'+candidate+'/AshenCloister-Chapter1.exe');exe_pins[str(p)]=sha(p)
extras=['chapter1/view/'+n for n in ['chapter_hud_quality17.gd','equipment_sigil_quality17.gd','chapter_actors_quality17.gd','chapter_world_quality17.gd']]
tested=read(B/'presentation17/review04/after17-source.json')['pins'];assert all(sha(R/n)==tested[n] for n in extras)
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8')
for a,b in [('chapter_hud_quality16','chapter_hud_quality17'),('chapter_actors_quality16','chapter_actors_quality17'),('chapter_world_quality10','chapter_world_quality17')]:
 assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s,encoding='utf-8')
source=(B/'full16/package_full16.py').read_text(encoding='utf-8').replace('candidate16','candidate17').replace('20261101-16','20261102-17').replace('Quality16','Quality17').replace('==103','==107')
source=source.replace("'chapter1/view/chapter_actors_quality16.gd']","'chapter1/view/chapter_actors_quality16.gd',"+','.join(repr(n) for n in extras)+']')
start=source.index("SCOPE='");end=source.index("\n",start)
source=source[:start]+"SCOPE='Full chapter candidate17 presentation: staggered sprite gait/paid windup lean, six stone batches with own geometry and existing texture, persistent inventory scroll/slot sigils/unique descriptions, 1.3s boss-death reveal and actual unique reward card. Same16 combat rules. Final art/manual/audio/performance gates remain open.'"+source[end:]
(OUT/'package_full17.py').write_text(source,encoding='utf-8')
(OUT/'RUN.ko.md').write_text('# 잿빛 회랑 후보17\n\nWASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지. 기술은 자동 시전됩니다.\n\n16의 냉기 규칙을 유지하며 장비 설명·스크롤과 보스 보상 리듬, 적 자세·폐허 입체 구조를 보완한 개발 후보입니다. 고유 저장 경로 Quality17을 사용하며 후보14·16 저장을 이동하지 않습니다. 최종 품질/수동/음향/성능 승인 전입니다.\n',encoding='utf-8')
(OUT/'ADOPTION.json').write_text(json.dumps({'backup16_source':str(backup),'preserved_exes':exe_pins,'added':extras,'review':str(B/'presentation17/review04/RESULT.json'),'root_assembly_now17':True},indent=2),encoding='utf-8')
print(str(OUT),flush=True)
