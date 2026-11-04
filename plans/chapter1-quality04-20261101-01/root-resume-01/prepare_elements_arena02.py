from pathlib import Path
import json,shutil
HERE=Path(__file__).parent;ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01/elements14'
shutil.copy2(HERE/'elements_fixture14.gd',BASE/'arena01/fixture-before-step-fix.gd')
p=HERE/'elements_fixture14.gd';s=p.read_text(encoding='utf-8');assert s.count('run.step(Vector2.ZERO,false)')==1;p.write_text(s.replace('run.step(Vector2.ZERO,false)','run.step(Vector2.ZERO)'),encoding='utf-8')
stage=Path('C:/Project/game-research/build-staging/chapter1-elements-20261101-02');assert not stage.exists();stage.mkdir()
pins=json.loads((BASE/'stage01.json').read_text(encoding='utf-8'));old=Path(pins['stage'])
for n in pins['pins']:
 p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
p=stage/'project.godot';p.write_text(p.read_text(encoding='utf-8').replace('Elements14Research01','Elements14Research02'),encoding='utf-8')
s=(HERE/'run_elements_arena01.py').read_text(encoding='utf-8').replace('chapter1-elements-20261101-01','chapter1-elements-20261101-02').replace('chapter1-elements-before13-20261101-01','chapter1-elements-before13-20261101-02').replace("OUT=BASE/'elements14/arena01'","OUT=BASE/'elements14/arena02'").replace('Elements13BeforeArena01','Elements13BeforeArena02')
p=HERE/'run_elements_arena02.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(str(p))
(BASE/'arena01/FAILURE.ko.md').write_text('배치 검사 스크립트가 ChapterRun.step에 인자2개를 전달해 parse 실패(actual1/stderr291)했다. 제품 FX 소스의 parse는 통과했다. 원시 출력/stage/수정 전 검사 소스를 보존하고1인자로 고친 arena02를 새 경로에서 실행한다. GPU 실행/시각 승인은 아직 없다.\n',encoding='utf-8')
