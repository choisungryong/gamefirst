# 품질03 독립 검증 · 코드 검토

2026-11-01, Asia/Seoul. 대상은 FX v02와 world verification02의 동결 소스다. 제품 파일은 변경하지 않았다. 기존 verification-01의 actual94/95 및 구현자 결과를 보존하고, 별도 verification-02에 검사와 원시를 만들었다.

## 실행 결과

- `prepare.py`가 이전 독립 실제 씬 fixture를 새 경로로 복사했다. 그 fixture에는 파일 쓰기 코드가 없으며 `--script` 대상도 verification-02로 고정했다. 구 버전의 소품500 상한만, 새 식생을 포함하는 총700 상한으로 바꾸고 실제620개·중앙 통로·키/배치·바깥 소품·코어 불변 및 최악 기술명 검사를 추가했다.
- 실제 `positive-execution.json`: **158 checks / actual exit0 / failures[] / stderr 빈 문자열**. 실제 `negative-execution.json`: **159 checks / actual exit1**, 의도한 실패 한 건이다. 의도 실패를 성공으로 바꾸지 않았다.
- 실제 시작·동일tick 패배HP0·재도전HP120·논리키 우선/physical fallback·echo/release·정지·중첩 장비/성장복귀·장착무회복·버튼 연결·화면 흔들림·표현 뒤 코어 snapshot 불변을 확인했다. HP/XP/장비를 지정한 부분은 명시적인 합성 경계 검사이며 일반 플레이를 주장하지 않는다.
- FX 사건 중복 방지·paid radius/발사 후 성장과 무관한 탄 모양·정지 중 효과 수명 보존·960파편/96stroke/48impact·13voice/중요2예비·mute/pause/UI cue/reset·4방향 각각4시전프레임을 확인했다.
- 배치된 새 월드는 revision `verge-ribbons-20261101-01`, 총673소품/식생620개/접촉그림자673/atlas2면이다. 사분면별 식생161/146/160/153, 높이1m 미만, 중앙 paving 안으로 발이 침범하지 않음, solid-looking 소품의 발은 ±19m 밖임을 확인했다. 이는 실제 화면의 밀도/가독성 승인이나 충돌 추가가 아니다.
- 1280×720,1440×810,1920×1080 별도 SubViewport에서 세 진화 기술명 전체가 두 줄로 보이고 서로 겹치지 않으며 HP/XP/회피도 화면 안에 있다. 가장 작은1280에서 기술명 폭201–202px, 긴 줄94px다. GPU/실제 모니터 렌더 검사는 부모가 별도로 진행한다.
- `audio-independent.json`:20개 WAV 각각 mono48kHz/PCM16, clipping sample0. 실제 청취·믹스·손맛은 파형으로 승인하지 않는다. 소스 트리 headless에서는 아직 가져오지 않은 PNG/WAV raw fallback이 기록되며, 내보낸 패키지의 imported resource/fallback0은 패키징 QA의 별도 조건이다.

## 보존 확인

`pins-before.json`과 `pins-after.json`은 같은 값이다. FX33/world6/core03nine/baseline51은 각 동결 manifest와 불일치0, 후보02/phase7 실행본 두 개 및 사용자 equipment/progress 저장 두 개도 지정 핀과 일치했다. 새로운 변경과 검사는 옛 실행본·과거 성공/실패·저장을 덮지 않았다. 이 검사는 핀하지 않은 과거 증거 전체의 바이트 불변이나 역사적인 두 보고서 복구를 입증하지 않는다.

## Anti-pattern 검토

`review_scan.py`와 `anti-pattern-scan.json`에 열 개 파일의 패턴 후보/행/해시를 남겼다. 수동으로 전체 파일과 호출 문맥도 검토했다.

- 표현자에서 `run.hero/enemies/projectiles/items`를 대입하는 코드는 없다. FX/actor/world/HUD 뒤 전체 snapshot 불변도 실행 검사했다. glue의 `run.step/choose/equip/request_dash`는 명시적 입력/선택 전달이다.
- 프로필/원작 경로 쓰기, 프로세스 실행·네트워크 전송, 무한 while, 거부한 hero_run/attempts 또는 구 합성음 경로는 대상 런타임에 없다.
- glue의 파일 쓰기는 선택적 QA key log와 PNG다. simplify_path 뒤 정확한 새 증거/실행파일 qa-captures 디렉터리 prefix를 검사하고, 기존 파일을 거부한다. 기본 실행에서는 경로가 비어 쓰지 않는다. 실제 프로필에는 접근하지 않는다.
- 새 노드 생성은 setup, mode signature 변경, 실제 새 actor/loot 때다. actor 수는 코어 retained512, ground loot32에 의해 제한된다. 루프 후 제거도 존재한다. 매 프레임 세 ImmediateMesh 객체는 재사용하며, 파편/리본 배열·convex hull은 유한하지만 계속 재구성된다. 생성 수의 상한이 실제 GPU 성능을 보증하지 않는다.
- 새 foliage 후보는 초기화 때57×57격자를 한 번 순회하고620개만 굽는다. 바닥·props의 shader는 읽기 전용이다. 불꽃 rim support는 네 모서리에서 alpha와 heat/core 발광에 함께 곱해져 수학적으로0이며 실제 렌더 경계는 GPU에서 확인해야 한다.

## Code quality 검토와 잔여 항목

현재 기능을 막는 P0/P1 결함은 발견하지 않았다. HUD v02의 폭/높이는 독립 경계 검사에서도 재현 가능하게 확인했다. 비교적 좁은 표현 패치이며 코어03/원래 진입점은 바이트를 유지했다.

1. **P3, 새 음향의 활성 cue gain 복원** — `chapter1/presentation/combat_audio.gd:96`의 `apply_volume()`는 모든 활성 one-shot에 같은 master×.11을 적용한다. `_play_cue()`의 cue별 GAINS는 그 시점에만 적용되므로 M으로 mute/unmute하거나 master를 바꾸면 재생 중인 발걸음의 .38 gain이1로 바뀔 수 있다(약2.63배). 상한 .9031 내이고 코어/리소스 오류는 아니다. 다음 음향 믹스 수정에서 voice별 cue gain을 보존하는 편이 좋다. 부모에게 전달했다.
2. **품질/성능 관문 열림** — `chapter1/view/cloister_effects.gd:186` 부근 원거리 전조 hull 및 per-frame 배열과 새 식생/ground shader의 fragment 비용은 실제 전경1080p로 측정해야 한다. headless 통과나 고정 FPS movie는 실제60FPS 통과가 아니다.
3. **시각 승인 열림** — geometry/배치 검사는 그림자·경계·가림·질감 반복·시전 보간·타격감의 최종 품질을 판정하지 못한다. 연속 영상·부모 직접 플레이·사용자 품질 판단이 필요하다. 이 대표90초는5–8분짜리1장 전체 완성본이 아니다.

커밋·업로드·제품 소스 수정·GPU 실행·실청취를 하지 않았다.
