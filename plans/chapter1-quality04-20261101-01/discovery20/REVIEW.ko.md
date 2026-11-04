# 발견20 — 실제 마법·희귀 획득 카드 / 제품 미연결

제품은 후보19를 유지한다. root HUD17 조립/19 freeze는 그대로이고 새 chapter_hud_quality20.gd는 외부 stage에서만 조립했다. 시작 장비는 조용히 seed하고 실제 inventory의 첫 magic·부위별 첫 rare만 카드로 알린다. unique는 우선순위 큐, 큐 최대4개/발견 간격/UID 중복 방지. 아이템 지급/등급/능력/장착 규칙을 바꾸지 않는다. 일시정지·장비창에서는 발견 시간도 정지한다.

## 실패와 수정

- replay01: 실제 정상45초의 magic UID2/rare UID3를 정확히 가리키고 독립 정상정책 전체 core동일/quiet. 그러나 실제 PNG에서 카드가 화면 아래까지 늘어나 전투를 가렸다. 기술 pass를 품질 승인으로 쓰지 않는다.
- replay02: 이름 Label만 줄바꿈을 끄고 높이를 설정했으나 나머지 Label의 임시 최소 높이 때문에 실제 희귀 카드가 여전히 길었다. quiet/core동일이어도 채택 제외.
- replay03: 모든 줄바꿈을 껐고 첫 magic 카드는512×122 logical로 개선됐다. 하지만 두 번째 카드 교체시 PanelContainer 이전 큰 rect가 남아 geometry assert가 실패했다. GPU exit0/stderr168, helper가 실패 판정했다. source stage/원시 결과/첫 카드 PNG 보존.
- replay04: Label 속성을 attach 전에 정하고 교체후2layout frame에 높이를 다시 맞췄다. 같은 내용의 기존 획득 toast도 숨겼다. 실제 정상 frost90131/defaultHP/획득성장45초, magic UID2 tick1243/rare UID3 tick1630 두 카드 모두512×122 logical, 전투 화면 높이40% 위 조건 통과. 실제 희귀 PNG에서 짧은 상단 카드와 영웅/예고 가시성을 직접 확인했다. import/check/GPU exit0/stderr0. 최종tick2701 전체 core snapshot이 별도 ChapterRun+ChapterPilot의 정상정책 결과와 완전히 같다. 실제 소유 이름/UID/등급/부위도 같다.

원시01..04/외부 stage/실패 로그를 덮어쓰지 않았다.19 root freeze 보존. 모든 게임 실행 terminal이다. 실제 장비창 입력과 pause/queue/reset/스타터 제외 edge 검증, 제품 패키징은 아직 하지 않았다. 카드 문양은 기존17 코드형 slot emblems다. 보스 넘어짐의 새 Actor20은 소스 시안만 추가했고 미실행/미연결이다.
