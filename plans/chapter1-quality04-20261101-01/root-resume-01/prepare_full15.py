from pathlib import Path
import json,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OLD=BASE/'full14';OUT=BASE/'full15';BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full15-before-20261101-01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not OUT.exists()and not BACK.exists()
pins=json.loads((OLD/'FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));assert all(sha(ROOT/n)==h for n,h in pins.items())
movie=json.loads((BASE/'elements15/replay03/COMPARISON.json').read_text(encoding='utf-8'));assert movie['same_full_core_start_and_end']
assert not json.loads((BASE/'elements15/caps01/result.json').read_text(encoding='utf-8'))['failures']
source=json.loads((BASE/'elements15/normal01/source.json').read_text(encoding='utf-8'));assert sha(ROOT/'chapter1/view/chapter_elements_quality15.gd')==source['pins']['chapter1/view/chapter_elements_quality15.gd']
OUT.mkdir();BACK.mkdir(parents=True)
p=ROOT/'chapter1/chapter_one_view.gd';shutil.copy2(p,BACK/'chapter_one_view.gd')
(BACK/'manifest.json').write_text(json.dumps({'source14_freeze_sha256':sha(OLD/'FINAL-SOURCE-FREEZE.json'),'before':{'chapter1/chapter_one_view.gd':sha(p)},'new_source15_sha256':sha(ROOT/'chapter1/view/chapter_elements_quality15.gd'),'normal_replay03':str(BASE/'elements15/replay03/COMPARISON.json')},indent=2),encoding='utf-8')
s=p.read_text(encoding='utf-8');assert s.count('res://chapter1/view/chapter_elements_quality14.gd')==1;p.write_text(s.replace('res://chapter1/view/chapter_elements_quality14.gd','res://chapter1/view/chapter_elements_quality15.gd'),encoding='utf-8')
s=(OLD/'package_full14.py').read_text(encoding='utf-8').replace('candidate14','candidate15').replace('20261101-14','20261101-15').replace('Quality14','Quality15').replace('==99','==100')
s=s.replace("'chapter1/view/arc_quality14.gdshader']","'chapter1/view/arc_quality14.gdshader','chapter1/view/chapter_elements_quality15.gd']")
s=s.replace('same Chapter09 gameplay and13boss, with centered faceted frost/actual frozen crystals and shatter chunks, bounded bright arc paths and smaller cold/arc contact accents.','same Chapter09 gameplay and14elements/13boss; evolved-cold paid death now emits bounded ice debris/ground accent, no added freeze/damage and no duplicate real shatter.')
anchor="    assert len(elements)==1 and elements[0]['ice_targets_cap']==24 and elements[0]['arc_links_cap']==64"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n    death_elements=[json.loads(line.split('CHAPTER1_ELEMENTS15 ',1)[1])for line in smoke['stdout'].splitlines()if 'CHAPTER1_ELEMENTS15 'in line]\n    assert len(death_elements)==1 and death_elements[0]['cold_death_budget']==4 and death_elements[0]['damage']==0 and not death_elements[0]['freeze_added']")
(OUT/'package_full15.py').write_text(s,encoding='utf-8');shutil.copy2(OLD/'run_runtime.py',OUT/'run_runtime.py')
s=(OLD/'RUN.ko.md').read_text(encoding='utf-8').replace('후보14','후보15')
s+='\n15는 기본HP의 몬스터가 빙결 전에 죽는 실전을 반영해, 진화 냉기의 실제 처치에 얼음 잔해/짧은 지면 흔적을 연결했습니다. 추가 피해/빙결은 없으며 이 잔해를 기존 파쇄 피해proc와 구분합니다.\n'
(OUT/'RUN.ko.md').write_text(s,encoding='utf-8');print(str(OUT))
