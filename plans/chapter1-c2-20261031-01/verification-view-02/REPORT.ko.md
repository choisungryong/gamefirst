# C2 뷰 수정02 독립 검증

2026-10-31. **동일 tick 패배 시 HUD가 생명력0을 즉시 표시하고, 단축키가 실제 전달된 논리 키 값을 사용함을 확인했다.** 제품 코드는 수정하지 않았다. 실제 OS 조작·내보낸 후보02·화면 품질·GPU·음향·정상 플레이 완주 검증은 이 보고서의 범위가 아니다.

검증한 `chapter_view.gd` SHA256은 `a315c708027238b13a508a45ae0f9d36c3bd0a7a385421fee6e605f37f842bb9`, `cloister_hud.gd`는 `30360c68c4e8e0bce2e48a33ab6063a221ed74381a97571d662c2b740fea675b`다. 기존 후보01의 runtime42개 중 이 두 파일만 예상된 후속 변경으로 구분했다. 나머지40개와 core03 현재/보관9개, 기존 baseline51개 및 후보01 EXE는 전후 불일치0이다. 새 후보02의 패키지는 별도 manifest로 검증해야 한다.

## 실제 실행

| 실행 | actual exit | 결과 |
| --- | ---: | --- |
| 실제 Chapter1 씬을 생성한 독립 headless fixture | 0 | 53검사, 실패 없음 |
| 동일 fixture `--prove-failure` | 1 | 54검사, 의도 실패1 |
| 변경하지 않은53검사 fixture `--verbose` 재실행 | 0 | 실패/경고/오류 없음 |

각 `*-execution.json`에 전체 argv·cwd·stdout·stderr·실제 returncode를 보존했다. 최초 positive 실행은 기능53개가 통과했지만 종료 시 ObjectDB 및 resource1개 경고를 출력했다. negative와 별도 verbose 재실행에는 이 경고가 없었다. 최초 원시를 그대로 보존했고 원인은 확정하지 못했다. **누수0 또는 제품 종료 오류 해결이라는 주장을 하지 않는다.** 이 관찰만으로 제품 수명 코드를 임의 변경하지 않았다.

이 fixture는 실제 `chapter1/Chapter1.tscn`을 생성하고 실제 HUD·코어·버튼 signal 연결을 사용한다. 일반 process/physics 진행은 끄고, 체력·XP·소유 장비의 경계 상태를 명시적으로 합성한다. 따라서 실제 일반 플레이나 OS 키 전달의 증거와 혼동하지 않는다. source 미리보기는 PNG raw fallback을 사용했고, 내보낸 패키지의 imported-resource proof는 별도다.

## 확인한 경계

- tick100의 마지막 HUD를 HP5로 만든 뒤 실제 `_hero_damage` 전이로 같은 tick에 HP0/defeat가 됐다. 즉시 bar0 및 `0 / 120` 표시와 패배 모달을 확인했다. HUD sync 전후 코어 snapshot은 같다.
- 논리 R/물리 Pause 이벤트가 실제 retry handler를 거쳐 seed를 정확히1 늘리고 tick0·HP120·새 런 소지품으로 재시작한다. HUD도 즉시120으로 복원된다.
- 논리 Escape/I/Space/M과 무관한 물리 Pause 조합에서 실제 pause·장비·dash cooldown·mute 상태 전이가 동작한다. 논리 값0일 때만 물리 Escape fallback을 사용한다. release·echo·알 수 없는 논리 F12는 명령을 수행하지 않는다.
- XP6으로 생성한 실제3카드 선택이 장비 열기/닫기 및 중첩 pause/resume 후 같은 token으로 복원된다. 정지 상태의 step20회가 snapshot을 바꾸지 않는다.
- 실제 HUD 장착 버튼 signal이 소유 UID41을 장착한다. 최대HP120→150, 현재HP111 유지, 같은 tick의 HUD `111 / 150` 표시가 일치한다.
- 실제 성장 선택/장착/장비 닫기 signal은 `_has_move_target`을 만들지 않는다. 실제 버튼 callback 연결 검증이며, OS 마우스 이벤트가 GUI를 통과하는 전체 경로까지 실행한 검사는 아니다.
- 선택 버튼으로 실제 rank2 및 playing 복귀가 적용된다. optional key observer 함수가 코어 snapshot을 바꾸지 않는다.

## 원인 자료와 코드 품질 검토

부모의 실제 OS 진단 원시 `native-fix02/input-observer01/events.jsonl`에는 Escape의 keycode4194305, I73, R82가 각각 정확하지만 physical_keycode는 모두4194313으로 기록됐다. `_input`과 `_unhandled_key_input` 양쪽에 실제 이벤트가 도착했다. 따라서 메뉴 명령에 `event.keycode`를 우선하고0일 때만 physical을 사용하는 수정은 관찰된 전달 값에 대응한다. 이것이 모든 실제 하드웨어 키보드의 오류였다는 뜻은 아니다. WASD의 물리 키 polling은 변경하지 않았고 이 fixture는 WASD OS 입력을 승인하지 않는다.

| 코드 품질 / anti-pattern 확인 | 결과와 한계 |
| --- | --- |
| HUD 제한 갱신 | mode/offer/장비 signature가 바뀌면6tick throttle을 건너뛴다. 평상시 표시 갱신 제한은 유지된다. 동일 tick terminal 및 장착 경계를 실행했다. |
| 입력 중복·GUI 경계 | 단축키는 기존 unhandled-key 단계에 있고 pressed/non-echo만 처리한다. world 이동은 unhandled mouse pressed 및 playing에만 있다. GUI Button/overlay가 먼저 처리하는 경로는 정적 검토했고 실제 OS 후속 검수가 필요하다. |
| optional observer | 명시된 QA argument 없이는 파일을 열지 않는다. 새 C2 evidence 경로/기존 파일 부재 guard와 flush만 추가하며 게임 수치에 쓰지 않는다. fixture에서 snapshot 불변을 확인했다. |
| optional capture | 명시된 capture-dir 때만 동작한다. mode가 한 render frame 유지된 뒤 저장하며 run/state 순번과 기존 파일 거부로 retry 덮어쓰기를 방지한다. allowlist는 새 C2 evidence 또는 실행 파일 아래 qa-captures다. 실제 PNG 저장은 이 headless fixture에서 실행하지 않았다. |
| 코어/밸런스 조작 | 없음. core03 9pin 불변이며 HP/XP/소유 장비 합성은 이 독립 fixture 안에만 있다. 기존 정상6사례의5승1패를 다시 성공으로 바꾸거나 숨기지 않았다. |
| 기존 파일·저장 영향 | 기존 실행본/제품51개/이전 증거를 수정하지 않았다. 사용자 profile 파일을 열거나 쓰지 않았다. 새 로그/fixture/pin만 이 검증 디렉터리에 작성했다. |

검토 범위에서 새 진행 차단 결함은 발견하지 못했다. 최초 종료 경고는 미확정 관찰로 남으며 후보02 실제 종료 로그와 구분해 추적한다. C2 표현·밸런스·정식 성능 및5–8분 첫 장의 품질 관문은 계속 열려 있다.
