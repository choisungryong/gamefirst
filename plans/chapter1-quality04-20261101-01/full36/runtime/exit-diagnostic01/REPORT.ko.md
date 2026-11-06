# 후보36 종료 경고 원인분리01 · 2026-11-06

## 결과

원래 `default-profile-earn01`의 ObjectDB 종료 경고는 이번 제한 진단에서 **재현되지 않았다**. 경고 해결이나 원인 확정으로 승격하지 않는다. 제품 EXE·소스·프로필 수정은 없다.

실제 후보36 EXE SHA256 `a889be6fcb57120083d78e84dacd4ae4976482edb04285ef017dbf37e993e22f`의 headless/verbose 실행만 사용했다. 원래 최초 프로필 획득 검사는 재실행하지 않았다. GPU는 실행하지 않았다.

| 경우 | 범위 | 종료 | stderr |
|---|---|---|---|
| observer_live | 씬 생성 후 정지 + 별도 코어120틱, 원관찰기처럼 local RefCounted/FileAccess를 보유하고4프레임 대기→quit | 0 | 0bytes |
| observer_cleanup | 같은 조건 + local 해제·scene queue_free 후4프레임→quit | 0 | 0bytes |
| scene_only | 메뉴 씬과 미시작 보조모델 생성·명시적 해제(코어 진행0틱) | 0 | 0bytes |
| model_live | 씬/프로필 없는 코어만 정상 입력정책·빈 시작장비로21498틱 승리, 참조 보유 후4프레임→quit | 0 | 0bytes |
| model_cleanup | 같은 코어 승리 후pilot.run/local 참조 명시 해제 후4프레임→quit | 0 | 0bytes |

코어 승리 두 경우 실행시간은 각각24.437초/26.718초. 짧은 씬 경우는 각2.3–2.8초. 프로필 비활성화 플래그를 전달하고, 씬 경우는 `view._profile_off` 및 `not view.profile.available`을 실제 확인했다. model 경우에는 프로필 클래스·씬을 생성하지 않았다.

## 해석과 한계

- 짧은 씬의 보유 참조 및 정상 코어 완주 local 참조만으로는 경고가 나지 않았다. 이 사실만으로 원래 관찰기 또는 제품의 결함을 배제하지 않는다.
- 원래 경고는 단일124byte 메시지만 있어 누수 object class/id가 없었다. 새 verbose 실행에서도 재현되지 않아 leaked class를 확보하지 못했다.
- 원래 최초 저장·완주 씬·보조 모델·종료 수명이 한꺼번에 결합된 실행과 이번 제한 진단은 다르다. 정상 저장 파일은 다시 최초없음 상태로 만들지 않았고 새 보상도 저장하지 않았다.
- 정상 core의 self-reference 생성 후보로 `_near`의 `sort_custom` lambda와 소유객체를 확인했으나, full model에서 quiet 종료되어 특정 cycle 원인이라고 주장할 근거가 없다.
- 다음 추가 진단이 필요하다면 **프로필 OFF의 별도 verbose 실제 씬 완주 종료**에서만 재현 여부를 확인하고, 원래 최초저장 결과는 그대로 보존한다. 재현 없이 제품 종료 코드를 임의 변경하지 않는다.

## 보존 근거

`SUMMARY.json`, `MODEL-SUMMARY.json`의 실행 전/후 최신 ADDENDUM02 사용자9핀 전부true. EXE 해시 불변. 각 경우의 `launch.json`에 명령·observer/EXE SHA256, `execution.json`에 exit/시간/stderr, `stdout.txt`/`stderr.txt` 원시가 있다. 기존 실패 원시·helper·소스·EXE는 변경하지 않았다. 새 작업 파일은 이 디렉터리에 한정한다.
