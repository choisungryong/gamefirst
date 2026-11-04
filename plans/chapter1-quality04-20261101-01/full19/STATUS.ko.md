# 후보19 — 일반·정예 골격 동작 / 실제 전체 GPU 종료

개발 EXE: `builds/chapter1/chapter1-full-candidate-20261102-19/AshenCloister-Chapter1.exe`

SHA256 `a21313f1be939098e791e3f44c7b45b5cd643bf2a5438bc50be34c42ff4db263`,130029040bytes/runtime111/stage113/PCK200. 루트는 core16/FX16/HUD17/World18/ActorBatched19다. root main/preset은 Baseline, 패키지는 ChapterOne/Quality19 고유 저장 경로다. 기존 저장을 옮기지 않았다.

## 변화와 확인 범위

walker/중간 elite에 기존 허가 Mophs73골격의 실제 walk·windup·slam/fan·death를 연결했다. paid release .157초, 빙결/메뉴 정지·냉기 일반 사체 소멸을 유지한다. 일반 얼굴/윤곽광과 정예 색/어깨 장갑·뿔을 구분했다. 보스·영웅·원거리·돌진은 기존 경로이며 추가 개선 대상이다.

최대 군중에서 최초 골격안이 느려 body/mask를 한 surface로 연결했다. 원본 diffuse가 동일함을 검사하고 정점·UV·bone/weight를 유지하며 종류별 색은 vertex color로 옮겼다. mesh 캐시 공유/actor별 재질 fade·tint 유지. 일반 모델 directional shadow는 기존 일반 sprite와 같이 끄고 hero/final boss는 유지한다. 최종 픽셀 전체가 같다는 주장은 아니다.

- motion19/fixture01과 최적화 후 fixture02: 각각16항목 true/import0/check0/GPU0/stderr0. 복사한 단일 적의 네 방향/근접 준비·release/빙결/가림/냉기·화염 사체·정예 제외/reset 검사이며 정상 전체 플레이가 아니다. 원래 전체 core snapshot 복원 확인.
- motion19/crowd01: 실제 PNG1920×1080, 합성180walker/120warmup+360frame. 기존 sprite 평균7.8458ms/p95 7.5758/draw467, 최초 골격 평균17.4916/p95 19.4444/draw1187. 드문 긴 프레임 때문에 평균이 p95보다 클 수 있다.
- motion19/crowd02: 최적화 평균14.9454ms/p95 15.068/draw467. 실제 PNG에서 body/mask 구분·형태 확인. vsync off/uncapped 합성 부하이며 패키지 MSAA2/정상 전투·최종3회 성능과 구분한다. 각 core 복원 true/quiet.
- build import/export/PCK/30simsec 정상 headless·입력정책 probe 통과. 원17 전체3주력 core 결과는 코어 불변 범위로 상속하며19 전체 실행이라고 쓰지 않는다.

## 전체 GPU 종료 — 중복 실행 금지

runtime/gpu-cold01 observer19 headless65simsec 사전검사 exit0/stderr0,epoch1/39shatter/38cold-death. 실제19 EXE GPU PID14704/session68243은 종료했다. gpu exit0/stderr0,397.7초/tick23862/3451처치/Lv12/파쇄840/cold-death823. 실제16과10게임 상태 동일.27PNG 모두1920×1080이며 전투90초/승리후.35초와1.60초를 직접 봤다. 보스 사망 진행과 실제 겨울의 심장 보상을 확인했다. 같은 전체 검사를 재실행하지 않는다.

profile-off/정상 획득·성장/frost90131/vsync off/maxfps120. engine delta 평균8.83ms/p959.09/p9921.52는 제한·캡처를 포함한 관찰값이다. 캐시된 TIME_PROCESS의 평균은 frame 비용으로 무효 처리했고, 종료콜백 texture2304×1296과 실제PNG1920×1080의 차이도 원인 미확정이다. runtime/gpu-cold01/REVIEW.ko.md에 원시값/한계를 분리했다. 최종3회는 OS monotonic 시각과 실행 중 실제 이미지 크기를 기록해 별도 검증한다. 수동·실청취·저장UI·최종 성능 승인은 남았다.

## 보존과 다음 작업

14·16·17·17b·18 EXE/stage/연구 원본 보존. 원18 조립/project/preset은 `C:/Project/game-research/implementation-backups/chapter1-before19-20261102-01/`에 보존,18 freeze 대조. ADOPTION.json 기존 EXE pins 확인. 사용자 저장을 쓰는 실행은 하지 않았다.

독립 감사23개가 root/stage/EXE/PCK/검사한 Actor 출처/기존14·16·17·17b·18 보존/전체GPU를 확인했다. 에셋북v12는18페이지/406refs/missing0,실제 브라우저18페이지×1440/390폭36case h1/가로넘침 통과/표지 직접 확인했다. 이어 원거리·돌진 동작/공간/발견·보상/저장·수동 전체·음향을 개선한다. 미연결 HUD20은 discovery20/replay01..03 화면 높이 실패를 보존한 뒤04에서 실제 정상45초 획득 마법UID2/희귀UID3를 짧은512×122logical 카드로 보여주고 독립 정상정책 전체core동일/quiet를 확인했다. edge 검사·제품 통합은 남았다. Actor20 보스 넘어짐은 소스 시안만 추가/미실행이다. 첫 장 목표 active,2·3장 미착수.
