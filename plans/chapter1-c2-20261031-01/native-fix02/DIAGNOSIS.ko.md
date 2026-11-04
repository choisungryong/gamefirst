# 후보01 실제 입력/HUD 문제와 후보02 수정

후보01의 실제 OS 입력 검수에서 부모가 Escape/I/R을 보냈으나 기대 동작이 보이지 않았다. 추정으로 physical0 fallback을 넣지 않고, 먼저 후보01 EXE·source를 보존한 채 명시 옵션의 source-scene observer를 실행했다.

`input-observer01/events.jsonl`의 실제 pressed/keyup 기록은 두 단계 `_input`과 `_unhandled_key_input`에 모두 도착했다. logical keycode는 Esc4194305/I73/R82로 맞지만 physical_keycode는 세 입력 모두4194313이었다. 따라서 이 CUA 입력 경로에서 physical code만 매칭한 것이 원인이다. 실제 물리 키보드 입력 자체가 고장이라고 단정하지 않는다. 관찰 전 hotkey 로직은 변경하지 않았고 diagnostic 종료는actual0이다.

수정: 메뉴 hotkey는 logical keycode를 우선하고 logical0일 때만 physical을 사용한다. 실제 키보드의 WASD 물리 위치 polling은 유지했다. observer는 `--chapter1-qa-input-log=<새 C2 증거 파일>`일 때만 동작하며 기본 실행에서는 파일을 쓰지 않는다.

HUD 문제는 별도다. mode/signature가 달라져 결과창을 만들더라도 6tick 갱신 제한이 같은 tick의 final HP를 건너뛸 수 있었다. mode/signature 변경에서는 제한을 우회해 최종 HP·레벨·기술을 즉시 반영하도록 수정했다. 실제 native 재확인은 새 실행본에서 진행한다.

선택적 QA 캡처도 보완했다. 상태가 한 프레임 유지된 뒤 새 모달 이미지를 저장하고 state 일련번호를 증가시킨다. 시간 캡처는 run 일련번호를 이름에 포함해 재도전과 충돌하지 않는다. 기존 경로 allowlist와 기존 파일 overwrite 거부는 유지한다. 명시적인 capture-dir 없이 제품을 실행하면 캡처 파일을 쓰지 않는다.

변경 전47개 파일의 백업은 `C:/Project/game-research/implementation-backups/chapter1-nativefix02-before-20261031-01/manifest.json`이다. 후보01 EXE/stage/원시 증거는 유지한다. 새 빌드는 별도 `build_candidate02.py`가 기존 builder를 불러와 새 ID·경로를 지정한다. core03은 변경하지 않았다.
