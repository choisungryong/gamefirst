from pathlib import Path
import json,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OLD=BASE/'full13';OUT=BASE/'full14';BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full14-before-20261101-01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not OUT.exists()and not BACK.exists()
pins=json.loads((OLD/'FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));assert all(sha(ROOT/n)==h for n,h in pins.items())
proof=json.loads((BASE/'elements14/arena04/COMPARISON.json').read_text(encoding='utf-8'));assert all(proof['same_core_arena'].values())
OUT.mkdir();BACK.mkdir(parents=True)
p=ROOT/'chapter1/chapter_one_view.gd';shutil.copy2(p,BACK/'chapter_one_view.gd')
(BACK/'manifest.json').write_text(json.dumps({'source13_freeze_sha256':sha(OLD/'FINAL-SOURCE-FREEZE.json'),'before':{'chapter1/chapter_one_view.gd':sha(p)},'source14_added_files':['chapter_elements_quality14.gd','comet_quality14.gdshader','impact_quality14.gdshader','arc_quality14.gdshader']},indent=2),encoding='utf-8')
s=p.read_text(encoding='utf-8');assert s.count('res://chapter1/view/chapter_effects_quality10.gd')==1;p.write_text(s.replace('res://chapter1/view/chapter_effects_quality10.gd','res://chapter1/view/chapter_elements_quality14.gd'),encoding='utf-8')
s=(OLD/'package_full13.py').read_text(encoding='utf-8').replace('candidate13','candidate14').replace('20261101-13','20261101-14').replace('Quality13','Quality14').replace('==95','==99')
extra=['chapter1/view/chapter_elements_quality14.gd','chapter1/view/comet_quality14.gdshader','chapter1/view/impact_quality14.gdshader','chapter1/view/arc_quality14.gdshader']
s=s.replace("'chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md']","'chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md',"+','.join(repr(x)for x in extra)+']')
s=s.replace('same Chapter09 gameplay plus unique final-boss73bone/eightclip presentation, paid release timing, freeze/thaw continuity, posed-capsule owner coverage and terminal-clock-independent death; hero/grass/contact presentation retained from11.','same Chapter09 gameplay and13boss, with centered faceted frost/actual frozen crystals and shatter chunks, bounded bright arc paths and smaller cold/arc contact accents.')
s=s.replace("    full=execute('packaged-full-normal'","    elements=[json.loads(line.split('CHAPTER1_ELEMENTS14 ',1)[1])for line in smoke['stdout'].splitlines()if 'CHAPTER1_ELEMENTS14 'in line]\n    assert len(elements)==1 and elements[0]['ice_targets_cap']==24 and elements[0]['arc_links_cap']==64\n    full=execute('packaged-full-normal'")
s=s.replace("    victory=next(row for row in states if row['mode']=='victory')","    assert not full['stderr'],full['stderr']\n    victory=next(row for row in states if row['mode']=='victory')")
(OUT/'package_full14.py').write_text(s,encoding='utf-8')
shutil.copy2(OLD/'run_runtime.py',OUT/'run_runtime.py')
s=(OLD/'RUN.ko.md').read_text(encoding='utf-8').replace('후보13','후보14')
s+='\n14는 냉기창의 중심/면, 실제 빙결의 반투명 얼음, 실제 파쇄의 큰 파편과 번개 중심/잔광을 추가했습니다. 냉기·번개의 겹치는 흰 명중 섬광은 줄였습니다.\n'
(OUT/'RUN.ko.md').write_text(s,encoding='utf-8');print(str(OUT))
