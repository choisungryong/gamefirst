from pathlib import Path
import json,hashlib,shutil
HERE=Path(__file__).parent;ROOT=Path('C:/Project/d2r-combat-baseline')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
 p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2)
b=read(HERE/'build/build.json');g=read(HERE/'GPU-FULL-RESULT.json');n=read(HERE/'NATIVE-REWARD-UI.json')
assert g['actual_exit']==0 and all(g['same_gameplay_as09'].values()) and n['final_weapon_uid']==36
source=ROOT/'chapter1/art/rigged_mage/v01/mage_animated.glb'
ledger={'candidate':11,'scope':'Current presentation additions, not final art approval. Existing source/asset/audio ledgers still apply to other assets.',
 'hero':{'source':'https://opengameart.org/content/rigged-textured-mage','author':'thecubber','rig_credit':'Julius / OpenGameArt','license':'CC BY-SA3.0','license_url':'https://creativecommons.org/licenses/by-sa/3.0/','runtime_path':str(source.relative_to(ROOT)).replace('\\','/'),'sha256':sha(source),'bytes':source.stat().st_size,'bones_actual_godot':53,'clips':['idle','run','cast','hit','death'],'changes':['legacy material conversion','own authored IK animation/baking, not mocap','unweighted vertex2053 repaired with one-ring inverse-distance weights; four low-weight vertices normalized','metre conversion','distance gait/upper-body blend/runtime artist lighting/readability'],'derived_source_directory':'C:/Project/game-research/art-sources/oga-mage-20261101-01/gltf-preview-06','runtime_attribution':'chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md','derivative_model_and_renders':'CC BY-SA3.0','open_art_work':['natural run','staff grip/fingers','cloth deformations']},
 'independent_geometry':['chapter1/view/ember_staff_visual.gd','chapter1/view/chapter_world_quality10.gd'],
 'independent_shaders':['chapter1/view/chapter_grass_quality10.gdshader','chapter1/view/chapter_ground_quality10.gdshader','chapter1/view/contact_quality10.gdshader'],
 'grass':{'patches':545,'blades':11492,'surfaces':1,'removed_round_foliage_quads':720,'collision_added':False},
 'contact':{'duration_seconds':.13,'per_consume':8,'active_cap':96,'drives_damage':False},
 'rejected':['AI eight-walk03 repeated leading foot','unrepaired mage black chest spike','gold clone depth tint reveals robe internal surfaces','grass01 invisible under lighting','grass02 sRGB-linear mismatch too pale','candidate10 PCK missing attribution MD'],
 'not_used':['D2/SACRATA protected runtime art or source','CMU mocap (research only)'],
 'root_import_ignore_archived':'C:/Project/game-research/implementation-backups/chapter1-full10-before-20261101-01/mage-research-before-adoption.gdignore'}
write(ROOT/'chapter1/art/QUALITY11-LEDGER.json',ledger)
shutil.copy2(ROOT/'chapter1/art/QUALITY11-LEDGER.json',Path(b['exe']).parent/'credits/QUALITY11-LEDGER.json')
book=HERE/'book-v05/dist'
write(HERE/'book-v05/REVISION-02.json',{'initial_build':'BUILD.json','changes':['Korean heading word-break keep-all avoids a single trailing syllable','long executable hash wraps on mobile'],'browser_checks':{'desktop':{'viewport_width':1440,'document_width':1425,'pages':8,'screenshots_observed':['index before/after typography','reference','research video playing17.293706s before book copy']},'mobile':{'viewport_width':390,'document_width':375,'pages':8,'screenshot_observed':'validation'},'video_metadata':{'duration':24,'ready_state':4,'error':None},'viewport_reset':True,'owned_tab_closed':True,'server_8781_pid25540_stopped':True,'remaining_tab1_untouched':'old localhost8768 remaining.html tab; do not identify it as a current YouTube tab'},'static_links':110,'missing':[],'print_checked':False,'current_artifacts':{str(p.relative_to(book)).replace('\\','/'):sha(p)for p in book.rglob('*')if p.is_file()}})
status=f'''# 전체1장 후보11 · 표현 개선 · 목표 active

최신 실행: `builds/chapter1/chapter1-full-candidate-20261101-11/AshenCloister-Chapter1.exe`.
SHA256 `{b['sha256']}`, {b['bytes']}bytes, runtime92/stage94/PCK164.
freeze SHA `{sha(HERE/'FINAL-SOURCE-FREEZE.json')}`.

실제 영웅53골격/5클립, 거리 기반 보행/연속회전/상체 시전·피격, 독립 코드 지팡이를 연결했다. 로브의 무가중치 정점2053과4개 약한 가중치를 원본 보존 파생물에서 수정했다. 라이선스는 CC BY-SA3.0, 저자thecubber/원리그Julius·OGA. PCK와 별도credits에 출처가 있다. 새 `chapter1/art/QUALITY11-LEDGER.json`과credits사본을 따른다. 원작 보호 자산은 추가하지 않았다. CMU 모캡은 조사만 했고 사용하지 않았다.

둥근 식생720장을545군락/11,492곡선 풀잎으로 대체하고 바람/뿌리 명도/판석 조명 요철·MSAA4x를 연결했다. 실제 지형 충돌을 추가하지 않았다. 실제 hit에0.13초 흰 섬광(consume당8/전체96)을 추가했다. 시전은 하체10개를 보존하고 상체26개를 실제로 바꾼다. 앞 적만32%로 흐리게 하고 뒤/옆은100%, 원래 사체 페이드를 유지했다. 표현 fixture22/actual0/stderr0, 확대8m 이미지5장. 미술 완성 승인이 아니다.

전체 실제GPU 정상 입력은 **21749틱/362.4833초/3185처치/Lv11/주력진화/고유보상 소유**로 승리했다. 첫 승리 snapshot의 mode/tick/kills/hero/growth/metrics/chapter/equipped/inventory/elite_reward_uid가09와 모두 같다. 자동 정책은 이동/실제 선택/장착/회복약만 사용한다. 이후 root가 CUA로 승리·23개 보상·마지막 잿꽃의 유언(-10%피해/+1발사체/화염처치폭발)을 직접 선택/장착했다. 현재 장비 열 변경/적용 알림/완료 화면 복귀를 확인했고 최종raw weaponUID36·HP37703 유지와 일치한다. 전체 도전의 수동 플레이가 아니다.520초 wall 종료0/stderr0/23PNG. `GPU-FULL-RESULT.json`은 첫 자동 승리와 후속 UI 최종 상태를 분리한다. `NATIVE-REWARD-UI.json`. 저장은 명시적으로 껐으며 실제 보관함 저장 승인이 아니다.

후보10은 import/export0 이후 모델출처MD 누락으로 PCK 감사가 실제1 종료했다. 원 preset의 *.md 배제가 원인이었다. 실패10 EXE/stage/freeze/log는 그대로 남겼다.11은 격리 preset에서만MD 배제를 제거하고 명시 출처 파일의PCK 해시도 확인했다. 루트 Baseline main/export preset은 유지했다.09 source freeze85개 중 변경은 chapter_one_view.gd의 표현 preload3개뿐이며 이전 바이트는 full10-before 백업에 있다. 나머지09 runtime/core는 같다. 기존09 EXE와 baseline51/backup77/oldEXEs3·사용자저장2/oldstage72 선택핀을 확인했다. 역사적 모든sidecar 불변 주장은 하지 않는다. 리깅 폴더의 연구용.gdignore는 채택 후 정상 import를 위해 같은백업으로 단일파일 이동해 보존했다. root 전체 editor import는 하지 않았다.

`SACRATA-COMPARISON.ko.md`는 기존25개 유효 관찰과 추가 재생표본/우리09·11의차이를 제작 단위로 정리한다. 소리·원작 내부 규칙·전체 프레임을 확인한 것으로 쓰지 않는다. `rigged-hero-05/hero-comparison-24s.mp4`는09 대 연구05의 같은입력/같은전투상태·오프라인30FPS 영상이다. 후보11 최신 영상으로 바꿔 부르지 않는다.

도감 `book-v05/dist/index.html`:8페이지,110로컬참조 누락0,1440desktop/390mobile의8페이지 제목/이동/가로 넘침 확인. 비교/표지/모바일 검증 화면과24초 video metadata/재생을 관찰했다. 제목의 마지막 한음절 줄바꿈을 keep-all로 고쳤고 긴hash 모바일줄바꿈을 적용했다. initial BUILD/이전CSS/REVISION02를 보존했다. 인쇄/모든사진/모든터치상호작용 검수는 아니다. 임시탭/localhost8781 정리, 남은기존탭1(옛localhost8768)은 변경하지 않았다.

다음 최우선은 공통 스프라이트인 정예/보스의 고유 실루엣·리그/예고·공격·회복·사망과 냉기/번개의 큰 형태다. 이어서 큰 공간의 깊이/보상/장비 목록 선택 때 스크롤 초기화, 새 보관함 실제 비어 있지 않은 재시작·저장 경쟁 구간을 보완한다. 최종 아트의 수동5–8분/실청취/동일1080p3회 성능을 통과해야 한다. 기능 검사나 새 리깅 하나로 SACRATA 품질을 승인하지 않는다.2·3장으로 넘어가지 않으며 목표active를 유지한다.
'''
(HERE/'STATUS.ko.md').write_text(status,encoding='utf-8')
backup=Path('C:/Project/game-research/implementation-backups/chapter1-full11-docs-before-20261101-01');assert not backup.exists();backup.mkdir(parents=True)
prefix=f'''# 2026-11-01 최신 — 전체1장 후보11 표현 개선 · 목표 active

먼저 `plans/chapter1-quality04-20261101-01/full11/STATUS.ko.md`를 읽는다. 최신 실행은 `builds/chapter1/chapter1-full-candidate-20261101-11/AshenCloister-Chapter1.exe`, SHA `{b['sha256']}`,129170136bytes/runtime92/stage94/PCK164다. 기존09·실패10/과거증거·사용자 저장을 보존했다.

영웅53골격/5클립·보행/상체혼합·코드지팡이·앞적가림fade,720둥근식생을545군락/11492곡선풀잎으로교체·판석조명요철·MSAA4x·실명중0.13초흰섬광을 연결했다. OGA thecubber/Julius CC BY-SA3.0 파생 모델은 가중치정점2053/4개 정규화·자체IK/재질을고쳤다. CMU모캡미사용. `QUALITY11-LEDGER.json`과PCK출처/credits를따른다. 금색복제윤곽/어둡고흰풀/출처누락10은 실패로보존했다.

패키지release기본진행/외부7동작과 실제표현22/0/stderr0. 전체GPU화염은21749틱/362.4833초/3185처치/Lv11 승리,첫승리 전투상태11개항목이09와모두같다. 이후root가실제CUA로보상23개/잿꽃의유언비교·장착·현재열변경/완료복귀를확인했고최종UID36/HP유지다.520초wall종료0/stderr0/23PNG. 저장off/자동한판이므로수동전체·실청취·정식성능승인이아니다. `GPU-FULL-RESULT.json`과`NATIVE-REWARD-UI.json`에자동완료/후속수동UI를분리했다.

도감v05 `plans/chapter1-quality04-20261101-01/full11/book-v05/dist/index.html`8페이지/110참조누락0/1440desktop·390mobile8페이지이동·폭확인. `SACRATA-COMPARISON.ko.md`가재비교분석이다.24초전후movie는09대연구05이며최신11영상과다르다. 초기BUILD/CSS/수정REVISION02유지. 임시탭/8781서버정리. 옛localhost8768기존탭1은변경하지않았다.

다음은고유정예/보스리그·실루엣/실동작과냉기·번개의큰형태,공간깊이/파밍UX다. 영웅쥠/달리기/옷감도완성승인전이다. 실제nonempty보관함재시작/저장경쟁구간/수동5–8분/실청취/최종1080p3회는열림. 목표active,2·3장미착수. agents는사용량제한으로root단독. root전체editorimport/동일출력재실행/기존증거덮어쓰기/커밋·업로드·구매·보호자산복사는하지않는다.

아래 이전 본문은 exact bytes suffix로 보존했다.

---

'''
records={}
for name in ['HANDOFF.md','chapter1/FULL-CHAPTER.ko.md']:
 p=ROOT/name;old=p.read_bytes();shutil.copy2(p,backup/Path(name).name)
 p.write_bytes(prefix.encode('utf-8')+old)
 assert p.read_bytes().endswith(old)
 records[name]={'old_sha256':sha(backup/Path(name).name),'new_sha256':sha(p),'old_bytes':len(old),'exact_old_suffix':True}
write(HERE/'HANDOFF-PRESERVATION.json',{'backup':str(backup),'files':records})
write(HERE/'DELIVERABLES.json',{'build':b,'status':str(HERE/'STATUS.ko.md'),'book':str(book/'index.html'),'gpu_first_victory_seconds':g['result']['tick']/60,'manual_unique_equipped_after_victory':True,'goal':'active','artifact_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p)for p in [HERE/'STATUS.ko.md',HERE/'SACRATA-COMPARISON.ko.md',HERE/'GPU-FULL-RESULT.json',HERE/'NATIVE-REWARD-UI.json',HERE/'book-v05/REVISION-02.json',ROOT/'chapter1/art/QUALITY11-LEDGER.json']}})
print(json.dumps({'docs_finalized':True,'candidate':11,'goal':'active'}))
