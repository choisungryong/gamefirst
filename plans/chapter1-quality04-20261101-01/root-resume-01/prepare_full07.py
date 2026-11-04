from pathlib import Path
import json,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent
source=ROOT/'plans/chapter1-quality04-20261101-01/packaging/package_quality06.py'
folder=ROOT/'plans/chapter1-quality04-20261101-01/full07';assert not folder.exists();folder.mkdir()
s=source.read_text(encoding='utf-8')
s=s.replace('candidate06','full candidate07').replace('chapter1-c2-candidate-20261101-06','chapter1-full-candidate-20261101-07')
s=s.replace("PROOF=HERE/'build06'","PROOF=HERE/'build'")
extras=['chapter1/presentation/frame_probe.gd','chapter1/view/hero_occlusion_rim.gdshader','chapter1/ChapterOne.tscn','chapter1/chapter_one_view.gd','chapter1/core/chapter_items.gd','chapter1/core/chapter_profile.gd','chapter1/core/chapter_run.gd','chapter1/core/chapter_pilot.gd','chapter1/view/chapter_effects.gd','chapter1/view/chapter_hud.gd','chapter1/view/chapter_world.gd','chapter1/view/chapter_ground.gdshader']
s=s.replace("EXTRAS=['chapter1/presentation/frame_probe.gd','chapter1/view/hero_occlusion_rim.gdshader']",'EXTRAS='+repr(extras))
s=s.replace("SCOPE='Representative C2 candidate06; not full5-8min chapter, SACRATA approval, manual play, sound-hearing or formal performance'","SCOPE='Full chapter candidate07; three zones/trials/champions/boss/persistent gear implemented. Not SACRATA quality, manual/audio or formal performance approval.'")
# Above candidate06 wording may already have been changed by the docstring pass.
s=s.replace("SCOPE='Representative C2 full candidate07; not full5-8min chapter, SACRATA approval, manual play, sound-hearing or formal performance'","SCOPE='Full chapter candidate07; three zones/trials/champions/boss/persistent gear implemented. Not SACRATA quality, manual/audio or formal performance approval.'")
s=s.replace('len(set(result))==72','len(set(result))==82')
s=s.replace('Ashen Cloister Chapter1 C2 Quality06','Ashen Cloister ChapterOne Quality07').replace('AshenCloisterChapter1C2Quality06','AshenCloisterChapterOneQuality07').replace('Chapter1 Quality06 Windows','ChapterOne Quality07 Windows')
s=s.replace('run/main_scene="res://chapter1/Chapter1.tscn"','run/main_scene="res://chapter1/ChapterOne.tscn"')
s=s.replace("'--chapter1-start','--chapter1-pilot'","'--chapter1-profile-off','--chapter1-start','--chapter1-pilot'")
(folder/'package_full07.py').write_text(s,encoding='utf-8')
(folder/'RUN.ko.md').write_text('''# 잿빛 회랑 · 제1장 구현 후보07

AshenCloister-Chapter1.exe를 실행합니다. 이전 C2 후보06은 보존되어 있습니다.

- WASD 또는 좌클릭: 이동 / Space: 회피 / Q: 회복약 / E: 가까운 선택 의식
- 자동 기술3계열 / 레벨 선택 / I: 장비 비교·장착 / Esc: 정지 / M: 음소거
- 세 마당의 봉인 주변 적을 처치하고 정예를 잡아 동쪽 회랑을 여세요. 재의 성소 보스를 실제 처치하면 완료됩니다.
- 끝나면 획득 장비를 새 전용 보관함에 저장합니다. 보관함에서 다음 판 장비 선택/해체가 가능합니다. 기존 Baseline 저장은 읽거나 변환하지 않습니다.
- 회복약은 시작3/최대5, Q는35% 회복과4초 재사용 시간을 갖습니다. 장비 교체는 전투 중 현재 생명력을 회복하지 않습니다.

현재는 전체1장 기능을 연결한 검토 후보입니다. SACRATA 품질·최종 아트·실청취·정식1080p 성능·수동5–8분 완료는 승인 전입니다. 실제 기본 영웅은 기존 스프라이트이며 리깅 연구 모델은 채택하지 않았습니다.
''',encoding='utf-8')
pins={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in extras if (ROOT/p).exists()}
with (HERE/'full07-preparation.json').open('x',encoding='utf-8') as f:json.dump({'generator_source':str(source),'runtime_expected':82,'extras':extras,'new_source_pins':pins,'no_build_yet':True},f,indent=2)
print(json.dumps({'script':str(folder/'package_full07.py'),'expected_runtime':82}))
