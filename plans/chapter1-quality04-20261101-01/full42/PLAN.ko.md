# 후보42 패키지 사전 준비

2026-11-13 root 검증 갱신: SELECTION.json은 별도 material trial의 전체15795/확장8653/캐시8653 동등성 통과와 native p95 16.984ms 개선을 근거로 선택했다. 추가 actor overlap 결과 캐시는17.417ms로 개선이 확인되지 않아 채택하지 않는다. 선택한 Actor42와 부모 기본 훅의 해시를 adopt 전에 확인한다. 변경하는 기존 root 파일은 조립·Demon19·Role21 세 개다. 세 파일 모두 백업하며, 기존41 stage/EXE/동결 파일과 다른 root41 파일을 보존한다. 부모 기본 훅은 기존 애니메이션 평가/재질 setter 그대로 수행하고42만 중복 작업을 생략한다. 아래의 과거 '조립 한 줄만'은 이 세 파일 계약으로 대체한다. 최종 제품16.67ms/3회 통과는 아직 미확인이다.

2026-11-13. 현재 제품은 후보41 성공 attempt02이며 SHA256은 `5da243815d2be1ce4a1e3e2265fac7fd4ef995275457d6da2a81d74188a545b2`이다. 후보42는 채택 전이다. 여기서는 PLAN/helper 작성과 읽기 전용 prepare만 허용한다. root GO 전 조립 변경·소스 동결·저장 fork·import/export·실행을 하지 않는다.

## 범위와 경로

41 closure 런타임175개에 `chapter1/view/chapter_actors_quality42.gd` 하나만 더해176개, project/preset 포함178개를 예상한다. Actor42 최종 바이트는 검증 담당이 승격하므로 지금 동결하지 않는다. 이후 root GO 시 `ChapterActors` preload36→42 한 줄만 교체한다. HUD41·FX39·Core37·데이터·모델·시각품질은 그대로다.

ID/stage/output은 `chapter1-full-candidate-20261113-42`, proof는 이 `full42`, 별도 저장은 `%APPDATA%/AshenCloisterChapterOneQuality42`다. helper 모든 prepare 외 동작에는 `--root-go`가 필요하다. 이 플래그는 실제 root 승인을 대신하지 않는다.

## 채택 후에만 수행할 순서

1. Actor42 동등성·fullsync·실속도 검증 결과를 root가 검토하고 최종 소스 채택 GO를 내린다. helper는 기존41 freeze/성공EXE, 원37/38/40/41 stage·freeze·EXE를 읽기 전용 검사한다. 원41 attempt01 실패 stage/EXE/이동 proof도 기존 `ATTEMPT01-PRESERVED.json` 패턴대로 검사한다.
2. 사용자 게임/engine이 실행 중이면 종료하지 않고 중단한다. 원37/38/40/41 main과 현재 존재하는 모든 revision journal을 해시·독립 사본으로 보존한다. 42 userdir/stage/output/backup은 처음에 없어야 하며 존재하면 중단한다. 현재41 main+모든 journal을42로 최초 한 번 바이트 복사한다. 덮어쓰기·reset·persist·보상지급은 하지 않는다.
3. 조립 한 줄 교체 후176개+project/preset 동결. 고유42 stage에서 import/export한다. 성공41 stage preset의 정확한 `chapter1/art/portrait41/ATTRIBUTION.ko.md` include_filter 항목을 그대로 유지한다. actor42만 export_files에 추가한다. credits는 성공41 것을 그대로 복사하며 자체 actor 코드에 별도 외부 출처는 추가하지 않는다.
4. 실제PCK 의존·원문 JSON/MD 해시·도구/연구 불포함을 감사한다. 실제 EXE의 Actor42/HUD41/FX39 로드, 메뉴→정상 시작/프로필 연속성, FX handoff, frozen/stun/death 기본 상태를 확인한다. frozen 검사는 live pose의 기본 연결 확인이며 직접pose 동등성·fullsync 증거를 대체하지 않는다.
5. 같은 EXE 최종 FPS 3회는 별도 root 성능 절차다. 41 실성능 p95 20.636ms 미달과 Actors 약65% 진단은 개선 방향의 근거일 뿐42 성공 근거가 아니다. 짧은 integration은 최종 FPS·전체 수동 완주·음향 승인으로 주장하지 않는다.

## 불변·재시도 계약

모든 증거는 새 고유 파일에 exclusive write한다. launch 전에 같은 실행 원시가 있으면 중단한다. 실패 디렉터리·EXE·원시는 삭제/덮어쓰지 않고 root가 새 attempt 경계와 helper 경로를 준비한 뒤 재시도한다. 정상 사용자 진행 변화는 실패로 보존하고 과거 저장으로 복원하지 않는다.

성공 계약은 closure176/178, build EXE bytes/SHA, pck-audit success, PACKAGED-INTEGRATION success, 실행종료0/timeoutfalse/launch_error null, FINAL-PRESERVATION success 및 원37/38/40/41+fork42 프로필 바이트 불변이다. 아직 어떤 성공 계약도 작성하거나 주장하지 않았다.
