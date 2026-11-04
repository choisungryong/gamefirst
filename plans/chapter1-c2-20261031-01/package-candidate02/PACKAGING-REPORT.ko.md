# C2 실행 후보02 · 패키지/실제 입력 검수

2026-10-31. **별도 실행본과 실제 입력 검수를 마쳤다. 약90초 대표 전투 후보이며 5–8분 첫 장 전체나 SACRATA 목표 품질의 완료는 아니다.**

실행본: `builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe`.
109675984bytes, SHA256 `111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188`.
조작과 범위는 같은 폴더 `RUN.ko.md`에 있다. 원본 project 진입점을 바꾸지 않았고 새 프로필 저장/기존 save 변환을 구현하지 않았다.

## 새 후보에 연결한 증거

| 항목 | 결과 |
| --- | --- |
| 소스/패키지 | 명시 runtime42·외부 staging44·PCK78. import/export actual0, 동적 자원과 각 PCK payload checksum·제외 경로 감사 성공. |
| 독립 view 검증 | 실제 scene/HUD53검사 actual0, 의도 실패54검사 actual1. 최초 fixture 종료 warning과 원인 미확정 기록은 그대로 보존했고 동일 fixture verbose 재실행은 깨끗했다. |
| 실제 EXE 메뉴 smoke | 1920×1080 일반 메뉴3초 actual0. 5역할의4방향+cast/hit/death import, raw PNG fallback0, 상태 PNG와 ERROR/WARNING 없는 종료. |
| 실제 OS 입력 | 부모/root가1440×810에서 직접 조작. Esc choice↔pause, I inventory, 장비 비교/장착/무회복, 좌클릭 이동, Space cooldown, M 안내, Ember 진화와 Frost/Arc 습득, 패배 HP0, R 새 판HP120을 확인했다. |
| 실제 종료/캡처 | native PID15952 actualexit0, log ERROR/WARNING0, overwrite refusal0. 36PNG·로그·관찰 등44파일을 새 C2 evidence에 복사해 모든 해시 일치. |
| 보존 | native 종료 뒤 runtime42/core03nine/baseline51/stage02와01각44 불일치0, 이번 EXE와 후보01/phase7 EXE·기존 save2 고정 해시 일치. |

직접 조작 판의 실제 결과는57.433333초·499처치·레벨9·획득4·Ember4진화/Frost2/Arc1·HP0 패배다. 각 기술의 실제 cast67/12/10과 hit505/25/40, event overflow0을 기록했다. 부모는 정예를 처치해 native 승리하지 않았다. 실제 음향 청취·WASD 물리 키 장시간 유지·별도 focus loss도 미확인이다. 부모 관찰을 패키지 담당자의 직접 OS 조작으로 바꾸어 보고하지 않았다.

후보02에서는 전체100초 GPU를 불필요하게 반복하지 않았다. 같은 core03/아트의 후보01 packaged QA는78.15초 정예 처치·813처치·3기술·주력 진화·9획득을 보존하며1080p p95는20ms로 목표16.67ms에 미달한다. 후보02의 실제 조작 p95는1440×810/모달·PNG 동기 저장의16.666667ms이므로 정식1080p 성능 합격이 아니다. 코어03의 정상6사례5승·냉기seed71 패배/전체actual1도 그대로 유지한다.

후보01에서 발견한 키 입력과 stale HP는 실제 observer→원인 확인→두 뷰 파일 수정→독립 fixture→새 EXE→부모 native 재확인 순서로 해결했다. 후보01 EXE·실패 원시·소스 사본을 덮지 않았다. 자세한 차이는 `DELTA-REVIEW.ko.md`, 원인은 `../native-fix02/DIAGNOSIS.ko.md`, 실제 관찰과 캡처는 `../native-runtime-02/OBSERVATIONS.ko.md`를 따른다.

남은 품질: 삼각형 풀·단순 소품·바닥 반복,4키프레임/남쪽 행동, 임시 합성음과 직접 청취, 실제1080p 성능, 연속 영상 비교, 전체5–8분 장의 맵/이벤트/보스/보상/저장. 이번 후보의 기술·UI 진행을 최종 품질 승인으로 대체하지 않는다.
