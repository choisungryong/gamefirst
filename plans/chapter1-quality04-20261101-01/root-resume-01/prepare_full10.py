from pathlib import Path
import json,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OLD=BASE/'full09';OUT=BASE/'full10'
BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full10-before-20261101-01')
assert not OUT.exists() and not BACK.exists();OUT.mkdir();BACK.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((OLD/'FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/n)==h for n,h in freeze.items()),'Preserve source09 before adoption'
name='chapter1/chapter_one_view.gd';shutil.copy2(ROOT/name,BACK/'chapter_one_view.gd')
with(BACK/'manifest.json').open('x',encoding='utf-8')as f:json.dump({'source09_freeze':str(OLD/'FINAL-SOURCE-FREEZE.json'),'source09_sha256':sha(OLD/'FINAL-SOURCE-FREEZE.json'),'before':{name:sha(ROOT/name)}},f,indent=2)
p=ROOT/name;s=p.read_text(encoding='utf-8')
for before,after in [('view/chapter_actors.gd','view/rigged_hero_actors.gd'),('view/chapter_world.gd','view/chapter_world_quality10.gd'),('view/chapter_effects.gd','view/chapter_effects_quality10.gd')]:
 assert s.count(before)==1;s=s.replace(before,after)
p.write_text(s,encoding='utf-8')
credits=ROOT/'chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md'
shutil.copy2(credits,BACK/'ATTRIBUTION-before-adoption.ko.md')
credits.write_text(credits.read_text(encoding='utf-8').replace('아직 비교 중인 후보이며 기본09 실행은 교체하지 않았습니다.','후보10에서 영웅 표현으로 사용합니다. 후보09 실행본은 그대로 보존했습니다. 동작/아트 최종 품질 승인과는 별개입니다.'),encoding='utf-8')
script=(OLD/'package_full09.py').read_text(encoding='utf-8').replace('candidate09','candidate10').replace('20261101-09','20261101-10').replace('Quality09','Quality10')
extra=['chapter1/view/rigged_hero_actors.gd','chapter1/view/ember_staff_visual.gd','chapter1/art/rigged_mage/v01/mage_animated.glb','chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md','chapter1/view/chapter_world_quality10.gd','chapter1/view/chapter_grass_quality10.gdshader','chapter1/view/chapter_ground_quality10.gdshader','chapter1/view/chapter_effects_quality10.gd','chapter1/view/contact_quality10.gdshader']
script=script.replace("'chapter1/view/chapter_actors.gd']","'chapter1/view/chapter_actors.gd',"+','.join(repr(n)for n in extra)+']')
script=script.replace('==83','==92').replace("'.png','.wav')","'.png','.wav','.glb')").replace("('.png','.wav')","('.png','.wav','.glb')")
script=script.replace('chapter1/art/quality03_audio/LICENSE-*.txt\"','chapter1/art/quality03_audio/LICENSE-*.txt,chapter1/art/rigged_mage/v01/*.md\"')
script=script.replace("(STAGE/'project.godot').write_text(project,encoding='utf-8')","project=project.replace('[rendering]','[rendering]\\nanti_aliasing/quality/msaa_3d=2')\n    (STAGE/'project.godot').write_text(project,encoding='utf-8')")
script=script.replace("if ext in ('.json','.txt'):","if ext in ('.json','.txt','.md'):")
script=script.replace("shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')","shutil.copy2(ROOT/'chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md',credits/'ATTRIBUTION-Rigged-Mage.ko.md')\n    shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')")
script=script.replace('three zones/trials/champions/boss/persistent gear implemented.','same Chapter09 gameplay; rigged hero, procedural staff/tapered grass, contact flashes, shaded paving and MSAA4x.')
(OUT/'package_full10.py').write_text(script,encoding='utf-8')
(OUT/'run_runtime.py').write_text((OLD/'run_runtime.py').read_text(encoding='utf-8'),encoding='utf-8')
(OUT/'RUN.ko.md').write_text('''# 잿빛 회랑 · 전체1장 후보10

AshenCloister-Chapter1.exe를 실행합니다. 메뉴에서 화염/냉기/번개를 선택합니다.
이동 WASD/방향키 또는 좌클릭, Space 회피, Q 회복약, E 가까운 선택 의식,
I 장비 비교/장착, Esc 정지, M 음소거. 세 봉인과 정예2·보스를 처치하면 승리합니다.
장비 보관/다음 출발 선택은 새 후보10 전용 저장을 사용합니다. 후보09 저장을 가져오지 않습니다.

후보09와 전투 규칙은 같습니다. 영웅 실제 리깅/무기, 가림 처리, 긴 풀잎,
판석 조명 요철, 짧은 명중 섬광, MSAA4x를 적용했습니다. 후보09와 과거 증거는 보존했습니다.
이는 품질 개선 후보입니다. SACRATA 수준, 수동 전체 플레이·실청취·정식 성능 통과가 아닙니다.
공개 리깅 모델과 파생 렌더는 credits/ATTRIBUTION-Rigged-Mage.ko.md의 CC BY-SA3.0을 따릅니다.
''',encoding='utf-8')
print(str(OUT))
