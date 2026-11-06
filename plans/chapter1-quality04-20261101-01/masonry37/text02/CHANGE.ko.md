# 37 성장 입력 검증 보완 · 2026-11-06

독립 정적 검토의 P2를 수정했다. 새 `run_growth_quality37.configure`는 중첩 값을 읽거나 successor template을 로드하기 전에 기존 `SuccessorCatalog.validate(candidate)`를 호출한다. 검증 실패 시 기존 RunGrowth와 동일하게 `errors=issues` 후 false를 반환한다. 다른37/36 정의·전투·실행본·root assembly는 수정하지 않았다.

수정 전37 소스는 `run_growth_quality37.before.gd`로 보존했고 PREPARATION.json에 해시가 있다. text01의 정상39검사·재시작21검사 원시는 덮어쓰거나 다시 실행하지 않았다.

캐시 이동이 끝난 뒤 승인된 단일 headless 검사 `verify_invalid37.gd`를 실행했다. 결과 actual exit0, stderr0bytes, RESULT30checks 전부 true. launch.json은 정확한 인수·관찰기와 수정 소스 해시를 기록한다.

네 잘못된 입력은 정수17, skills:[17], skills:[17,17,17], xp_thresholds:17이다. 각각 fresh와 이미 설정된 growth에서 false·기존 validator와 같은 오류를 확인했다. 실패 전후 snapshot·offer·RNG·epoch·cached successor template이 그대로인지 대조했다. 정상 configure/offer와 오류 이후 정상 reconfigure도 기존 RunGrowth의 snapshot·epoch·RNG와 같고 errors가 지워진다.

PRESERVATION.json: 기존 후보36 freeze158개·현재 사용자9핀 불일치0, 후보36 EXE SHA 그대로. GPU·full old completion·새 stage·editor 전체 import·프로필 쓰기 없음. 이 검사는 malformed API failfalse 보완 범위이며 최종 수동·음향·성능 승인으로 확대하지 않는다.
