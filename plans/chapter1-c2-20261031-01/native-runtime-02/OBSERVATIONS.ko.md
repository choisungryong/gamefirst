# 후보02 실제 OS 입력 관찰

2026-10-31. **부모/root가 CUA로 실제 Windows 창을 직접 조작했다.** 패키지 담당자는 UI 입력을 하지 않았으며, 부모가 전달한 관찰과 actual process exit·Godot raw log·저장된 PNG를 연결해 이 문서를 작성했다. 자동 pilot이 아니다. autostart/pilot/focus 무시/입력 observer 플래그 없이 일반 메뉴로 실행했고, 명시적인 QA PNG 옵션만 사용했다.

## 실제 입력에서 확인한 동작

- 1440×810 메뉴의 세 시작 버튼과 안내가 맞았다. 마우스로 Ember를 시작하고 성장 선택을 눌렀다.
- choice에서 Esc → paused → Esc → 같은 choice를 실제로 확인했다. I로 inventory를 열고 닫았으며, choice/inventory/paused를 오가는 상태 PNG가 남았다.
- 소유한 `균열의 잿불 가지`의 피해+14%·발사체+1을 비교한 뒤 장착 체크와 양쪽 비교 열을 확인했다. 현재HP65는 장착으로 회복되지 않았다.
- I로 돌아온 뒤 월드 좌클릭 이동과 카메라 이동을 확인했다. Space 회피 후 Esc로 멈춘 화면에서 재사용 대기3.0초가 보였다.
- M 입력으로 `소리 꺼짐` 안내가 보였다. 실제 소리를 청취해 음소거를 승인한 것은 아니다.
- `회수의 재결정`을 획득/장착했고 회수 반경+1m·기술 주기 단축8%를 확인했다.
- 주력 rank1→2→3→4, 잿불 계열 선행 패시브, 약29초의 `연쇄 화염구` 진화를 실제 화면에서 확인했다. 이어 Frost·Arc를 습득하고 Frost2와 세 기술 HUD를 확인했다.
- 첫 판은 실제57.433333초,499처치,레벨9,소유 장비4개에서 패배했다. 결과 HUD의 **0/120**을 확인해 후보01의 stale HP 문제가 해결된 것을 실제로 검수했다.
- 패배 후 R과 Esc로 새 판의 clock0·처치0·레벨1·HP120/120을 확인했다. run 번호가 바뀌어 QA PNG 이름 충돌은 없었다.
- 창 X로 종료했고 프로세스 actualexit0이다.

## Raw log가 확인하는 첫 판의 결과

`pilot=false`, `qa_ignore_focus=false`, `mode=defeat`, elapsed57.4333333333333, HPraw0, XP250이다. 장착은 weapon UID1/charm UID3, 성장은 Ember4 진화/Frost2/Arc1이다. 실제 cast는 Ember67/Frost12/Arc10, hit는505/25/40이다. 드롭7·획득4, 최대 동시 생존91·최대 발사체39·event overflow0을 기록했다. HP/XP/장비/스폰/피해를 주입하지 않았다.

frame p95는16.666667ms/3346표본이지만1440×810의 모달·동기 PNG가 있는 실제 조작 QA다. 정식1080p GPU 성능 합격으로 해석하지 않는다. 전체 벽시계447.815948초에는 관찰·모달·정지가 포함되며, 이를5–8분짜리 장 완주 시간으로 주장하지 않는다.

## 증거와 한계

`state-0001-run-000-menu.png`부터 `state-0033-run-002-paused.png`, run별 시간 PNG, `godot.log`, `native-menu-exit.json` 사본/참조와 캡처 해시 manifest를 보존한다. `state-0031-run-001-defeat.png`는 최종0/120, `state-0033-run-002-paused.png`는 새 판120/120을 보여 준다. 기존 후보01의 실패 키 입력·stale HUD와 덮기 거절 로그는 별도 그대로 남았다.

부모는 이 native 판에서 정예를 처치해 승리하지 않았다. 실제 음향 청취, WASD 물리 키를 길게 누르는 조작, 별도 OS focus loss는 확인하지 않았다. 전체5–8분 첫 장, 최종 아트/음향/재미,1080p 성능 승인은 열려 있다. 후보01 같은 core03의 packaged 자동 정상 입력 승리와 이번 직접 조작 패배는 서로 다른 증거로 유지한다.
