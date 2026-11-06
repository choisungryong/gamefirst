# 번개 진화명 후속37 · 미채택 · 2026-11-06

## 변경

- `chapter1/data/growth_quality37.json`: 원36카탈로그와 전체 dictionary 대조 시 `skills[2].evolution_name`의 `두 갈래 폭풍`→`세 갈래 폭풍` 한 필드만 다르다. 실제 진화 branches3은 유지했다.
- `chapter1/core/run_growth_quality37.gd`: 기존 RunGrowth를 상속. 후속 JSON을 기존 GrowthCatalog로 읽고 검증해 private template로 보관한다. 각 configure에서 기존 전달 정의를 깊은 복사한 뒤 승인된 진화명만 바꾼 expected와 후속 정의를 전필드 비교한다. ChapterRun이 전달한 FULL_XP를 정확히 유지한다. 다른 필드 차이가 있으면 실패하며 기존 super.configure를 정확히 한 번만 호출한다.
- `chapter1/core/chapter_run_quality37.gd`:36을 상속하고 `_init`에서 아직 사용되지 않은 기본 growth를 successor growth로 교체한다. 전투 코어 복제, post-start 추가 configure, private epoch 보정, HUD 문자열 가로채기 없음. 원36파일·root assembly는 그대로다.

기존 base start와 chapter start는 configure를 각각 한 번 호출한다. post-super.start 재configure 방식은 epoch3이 되어 offer token을 바꾸므로 사용하지 않았다. 새 방식은 최초 start epoch2, 동일 객체 재시작 epoch4로 기존과 같다. `run_growth`에는 run을 역참조하는 필드가 없으므로 새 growth가 원run과 cycle을 만들지 않는다. 상속된 `_catalog`는 원36 초기 정의를 전달하지만 실제 효과·offer·표시명 권위인 `growth`가 승인된 successor 정의를 사용한다. 기존 `_catalog`의 숫자와 successor 숫자가 동일함을 configure 시 검증한다.

## 실행 검증

`verify_text37.gd`를 Godot4.5.1 headless로 실행: actual exit0, stderr0bytes, RESULT39checks 모두 true. 기존 완료런을 다시 돌리지 않았고 GPU·프로필을 사용하지 않았다.

- 원/후속 카탈로그 기존 validator 통과, 전체 dictionary 차이 정확히 진화명1개.
- 정상seed90131의 화염·냉기·번개 각각1200frame 입력정책 실행. 매 frame 전체 snapshot을 승인된 문구만 원문으로 정규화한 뒤 비교. spawn/loot/growth RNG 상태도 매 frame 동일.1200tick/처치30·34·40/level2.
- 각 primary의 시작 snapshot 동일, epoch2, FULL_XP 동일. 동일 객체 재시작 snapshot 및 epoch4 동일.
- 별도 pure growth fixture에서 XP1640을 직접 부여하고 실제 protected offer·choose를 거쳐 primary 진화까지 도달. token·card IDs·수치·RNG·성장 snapshot 동일. 이는 정상플레이 전체 진화검사로 확대하지 않는다.
- 번개 진화 offer title과 effective_skill.name 모두 `세 갈래 폭풍`, evolved numeric effects 전부 동일.
- PRESERVATION.json: 원제품158freeze·사용자9핀·후보36EXE 해시 불변.

## 제한 및 다음

제품/root에 아직 연결하지 않았다. 후속 채택 시 ChapterRun37·World37최종선택·원Actor/HUD/FX 조합을 새 후보로 연결하고 패키지 의존성 수집에 새 JSON/새 growth가 포함되는지 확인해야 한다. 새 진화명 실제 GPU/HUD 표시는 아직 직접 검수하지 않았다. 정식성능·전체수동·실청취 승인 아님. 보존된36 source/EXE를 변경하지 않는다.
