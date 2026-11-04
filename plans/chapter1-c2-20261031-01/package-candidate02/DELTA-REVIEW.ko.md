# 후보02 변경 검토 · 후보01 실제 OS 발견 반영

2026-10-31. 후보01 EXE/증거를 보존하고 런타임42개 중 두 파일만 바꿨다. 게임 코어03·아트·VFX·음향·성장 수치·드롭 수치는 유지했다. 새 builder wrapper가 새 ID/stage/output/proof를 지정하며 이전 builder와 산출물을 재실행하지 않았다.

| 변경 | 근거와 확인 | 한계 |
| --- | --- | --- |
| UI hotkey logical 우선 | 실제 입력 observer의 Esc/I/R logical은 정확하고 physical은 모두4194313이었다. logical을 우선하고 logical0 때 physical을 쓴다. | CUA 입력에서 확인한 원인이다. 물리 키보드 고장으로 일반화하지 않는다. WASD polling은 그대로다. |
| 최종 HUD 즉시 갱신 | 동일 tick에서 terminal/modal signature가 바뀌면 6tick 제한을 우회한다. | 프레임이 같은 상태라는 UI fixture와 실제 OS 화면 검수는 분리한다. |
| 선택적 QA PNG | 새 상태가 한 렌더 프레임 유지된 다음 상태별 일련번호로 저장하고 시간 PNG는 run 번호를 쓴다. overwrite 거부 및 경로 allowlist는 유지한다. | 명시 capture-dir일 때만 파일을 쓴다. 동기 저장은 프레임 시간을 교란할 수 있다. |
| 선택적 입력 observer | 명시 옵션과 새 C2 경로에만 keycode/physical/phase/mode/tick을 저장한다. 기본 실행에서 비활성이다. | 진단 source-scene용 경계이며 정상 제품 동작을 대체하지 않는다. |

독립 검증 담당의 `verification-view-02/REPORT.ko.md`는 실제 scene 인스턴스의53검사 actual0, 의도 실패54검사 actual1을 보존한다. logical Esc/I/R+physicalPause, logical0 physical fallback, release/echo, 중첩 choice/inventory/pause, 동일 tick defeat HP0, retry HP120, 장착 최대HP/무회복과 버튼 signal을 확인했다. GUI propagation·실제 키 입력 자체는 부모 native QA를 따른다. 최초 positive의 종료 ObjectDB/1resource warning은 보존했고 동일 fixture verbose 재실행은 깨끗했다. 원인이 확정되지 않아 제품 종료 수정이나 누수0 주장은 하지 않았다.

anti-pattern 재검토: 효과/배우가 피해를 만들지 않고 코어에 직접 HP/XP를 쓰지 않는다. 키 수정은 mode 조건·echo/release 조건을 우회하지 않는다. QA observer는 명시 옵션 없이는 파일을 열지 않으며, 캡처 이름은 재도전 시 일련번호를 재사용하지 않는다. source42/stage44/PCK78 closure는 새로 확인했다. 원작/연구/테스트/증거를 PCK에 추가하지 않았다.

`chapter_view.gd`: `a315c708027238b13a508a45ae0f9d36c3bd0a7a385421fee6e605f37f842bb9`.
`cloister_hud.gd`: `30360c68c4e8e0bce2e48a33ab6063a221ed74381a97571d662c2b740fea675b`.

새 EXE의3초1920×1080 일반 메뉴 smoke는actual0,5역할×7상태 import와 raw fallback0, 상태 PNG, ERROR/WARNING 없는 종료를 확인했다. 전체100초 GPU는 반복하지 않았다. 후보01의 같은 core03/아트 렌더링 raw는 참고 증거로 남기며, 후보02의 정식 성능이나 품질 통과로 바꾸지 않는다.

부모 native02 결과가 실제 hotkey·HUD·성장·장비·재도전의 최종 UI 확인이다. 작성 시 PID15952 검수가 진행 중이며 완료를 미리 표시하지 않는다. 후보는 여전히 대표 전투 구간이며 SACRATA 목표 품질·전체1장 완료 승인은 아니다.
