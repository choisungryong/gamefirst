# Frozen C2 core candidate02 독립 검증

2026-10-31. 구현 변경 없이 검증했다. 현재 source 및 보관 source 사본 6개가 candidate02 manifest SHA256과 검증 전후 모두 일치했다. 이 결과는 코어 실행 검증이며 아트·화면·GPU·사운드·재미·5–8분 첫 장 완료의 승인이 아니다.

**판정: 정상 입력 경로 재현 성공. 보상 포화 경계 결함 1개를 남긴 조건부 코어 검증 결과다.**

## 실제 실행 결과

모든 명령 배열·stdout·stderr·실제 프로세스 exit code는 각각 `*-execution.json`에 저장했다. Python wrapper는 subprocess returncode를 그대로 반환하며 기존 증거를 덮어쓰지 않는다.

| 실행 | 실제 exit | 결과 |
| --- | ---: | --- |
| 원본 `test_combat_run.gd` | 0 | 52검사, 실패 없음 |
| 같은 테스트 `--prove-failure` | 1 | 53검사, 의도 실패 1개 |
| 원본 `test_growth.gd` | 0 | 188검사, 실패 없음 |
| 원본 `pilot_combat_run.gd` | 0 | 3주력 × seed71/907, 6/6 실제 정예 처치 승리 |
| 독립 fixture v1 | 1 | 검증 좌표 오류 1개; 아래 정정 기록 |
| 독립 fixture v2 | 0 | 45검사, 실패 없음. 알려진 보상 결함의 재현을 별도 observation으로 보존 |

`independent.gd`는 합성 XP/개체/장비/상태를 사용하는 **경계 검사용 fixture**이다. 이를 정상 플레이로 표시하지 않는다. 정상 pilot은 동결된 원본 그대로 실행했고 이동·dash·실제로 제시된 성장 카드 선택·실제로 얻은 장비 장착 외의 입력을 추가하지 않았다. HP/XP/item/spawn/kill/정의 주입은 정상 pilot에 없다.

| 주력 | seed | 실제 승리 초 | 처치 | 최대 동시 생존 |
| --- | ---: | ---: | ---: | ---: |
| Ember | 71 | 75.70 | 764 | 92 |
| Ember | 907 | 77.90 | 795 | 101 |
| Frost | 71 | 81.67 | 850 | 170 |
| Frost | 907 | 86.72 | 924 | 170 |
| Arc | 71 | 83.13 | 900 | 146 |
| Arc | 907 | 88.12 | 964 | 179 |

모든 정상 사례에서 3기술 습득·3기술 실제 시전/명중·주력 진화·4개 장비 슬롯 소유/장착·정예 실제 사망을 확인했다. event overflow는 전부0이다. 기존 candidate02 `results.json`과 새 `normal-results.json`은 CPU 소요 시간 필드만 제외하면 **전체 구조가 동일하다**. 이 수치를 렌더링 성능으로 해석하지 않는다.

## 확인한 독립 경계

- 실제 제공된 rank 카드와 cooldown 장비를 발사 뒤 적용해도 기존 발사 context의 피해·형태·예약 tick이 바뀌지 않는다. 기존 rank1 탄은 rank2 선택 뒤에도 3072raw로 명중하고, 첫 다음 시전은 기존 due73에 발생한다. 그 다음부터 rank2+charm 주기61tick을 쓴다.
- choice 상태에서 300번 step을 요청해도 전체 공개 snapshot이 그대로다. effective_skill 반환 객체 수정도 실제 효과에 영향을 주지 않는다.
- 합법 카드로 3기술을 해제한 뒤 200tick에서 Ember `[1,73,145]`, Frost `[1,85,169]`, Arc `[1,91,181]` 시전을 확인했다.
- frozen windup/recover/dash 각각에서 위치와 남은 state deadline이 정지하며 thaw 직후 미완료 상태가 유지된다.
- 돌진 캡슐 내부/측면 외부/시작 뒤/끝 외부 실제 피해, 원거리/정예 ray의 실제 travel 안/밖 피해 및 ray 사이 빈 공간을 확인했다. 원본 52검사의 walker·elite circle 경계도 통과했다. 전조의 시각 표현은 이 검증의 대상이 아니다.
- Arc death proc와 직접 분기가 같은 dedup 및 정확한6 hit budget을 공유한다. 같은 죽은 ID는 새 context로 타격해도 kill/XP를 다시 주지 않는다. 잔류 pulse3m와 chain search7m가 분리된다.
- XP450회 누적이 orb400개 상한에서 총량101475를 보존한다. event1100개는1024개 및 overflow76개로 제한되고 seq가 단조 증가한다.
- stale generation·존재하지 않는 옛 ID는 피해/보상을 발생시키지 않는다. 런 안에서 제거한 ID는 재사용하지 않는다. entity512개 상한, 실패한 정예 spawn의 재시도 권한 보존을 확인했다.

## 발견 사항: 바닥 장비 포화가 직접 지급 정예 보상까지 차단

**P2 correctness.** `chapter1/core/combat_run.gd:582`의 `_maybe_drop_item` 조기 반환은 `items.size() >= MAX_GROUND_ITEMS`를 정예에도 적용한다. 그러나 정예 보상은 뒤에서 바닥에 추가하지 않고 inventory로 직접 지급한다.

반례: 바닥 items32개, inventory0개 상태에서 실제 `_damage_enemy` 사망 전이로 정예를 처치한다. 결과는 `mode=victory`, `ground_count=32`, `inventory_count=0`, `dropped_items=0`, `picked_items=0`이다. 비어 있는 inventory에 지급할 수 있는데도 관련 없는 바닥 상한이 보상을 없앤다. 원래 `test_combat_run.gd`의 일반 상황 정예 보상 검사는 이 경계를 다루지 않는다.

재현 코드는 `independent.gd` 마지막 fixture이고 `independent-v2-execution.json` observation이 원시 결과다. 실제 정예 보상 보장을 완료 기준으로 삼는다면 해당 분기를 정예 직접 지급과 일반 바닥 드롭으로 구분하고 새 후보에서 재검증해야 한다. **동결 소스는 수정하지 않았다.** 이 결함은 정상6사례에서는 발생하지 않았고 크래시·6사례 진행 차단으로 판정하지 않는다.

Root는 이 발견을 정예 보상 완료 기준의 **승인 차단 항목**으로 지정했다. 수정 후보03을 새 evidence로 검증할 예정이며 이 문서와 원시02 반례는 그대로 보존한다.

## 부가 관찰: dash tick 문구

`dash-observation.gd`는 tick0에서 request_dash 후 ZERO입력으로12 step을 실행했다. 실제 이동은 tick1–11에서11회, 거리2.475m였고12번째 step에는 이동하지 않았다(actual exit0). `step`은 tick을 먼저 증가시키고 `_dash_until`에 `<` 비교를 하기 때문이다. 문서의12tick이12번 이동을 뜻한다면 경계 정정이 필요하다. 이 관찰은 12번째 이동을 강제하는 구현 변경 없이 원시 로그에 보존했고 root에 전달했다. 정상 pilot 수치를 바꿀 수 있어 수정 시 별도 새 후보 검증이 필요하다. 관찰용 exit0은 이 문구의 일치 판정이 아니다.

## 검증 도구 정정 기록과 증거 범위

초기 독립 fixture에서 fan gap 좌표를 `(10,1.0)`으로 잘못 골랐다. 이 점은 +0.14rad ray에서 약0.405m 떨어져 실제0.44m 위험 폭 안이다. v1의 actual1은 게임 결함이 아니라 검증 좌표 오류다. `(10,0.7)`로 수정했고 중앙 ray와 +0.14rad ray 모두에서0.44m 밖이라는 조건으로 v2가 통과했다. 최초 stdout/exit와 `independent-v1-source.gd.txt`를 보존했다. 보상 결함은 통과 수치에 숨기지 않고 observation과 별도 발견 사항으로 기록했다.

candidate02 기존 manifest는 6개 파일을 pin한다. 기존 positive 증거는 실제 exit0을 요약하고 negative 증거는 원시 tool 결과를 갖지만, 기존 normal pilot의 raw command/exit transcript는 해당 디렉터리에서 별도 파일로 발견되지 않았다. 기존 freeze summary의 exit 주장만 재인용하지 않고 이번 재실행에서 전체 명령과 실제 returncode0을 새로 보존했다.

manifest에 포함되지 않은 실제 의존성 `combat/combat_resolver.gd`, `combat/stat_block.gd`, 실행 설정, 계약 문서 및 growth 테스트의 현재 SHA256도 `verification-summary.json`에 추가했다. 이것이 과거 후보02 당시 해당 의존성까지 동결되었다는 증명은 아니다.

저장 API는 구현되지 않았고 코어에서 기본 catalog JSON을 READ하는 외에 profile 파일 접근 경로가 없다. 이번 작업에서 기존 save/profile 파일을 읽거나 쓰지 않았다. 시각·사운드·GPU·실제 사용자 조작·군중 회피·벽/내비게이션·첫 장 전체 분량은 별도 검수 영역이다. headless script 실행은 일반 main scene/화면 플레이의 검증이 아니다.

## 새 산출물

`pins-before.json`, `pins-after.json`, `*-execution.json`, `normal-results.json`, `verification-summary.json`, 재실행 wrapper와 독립 fixture를 이 디렉터리에 보존했다. 기존 source/evidence/scene/view/art 파일을 수정하지 않았다. 구현과 old save I/O, commit/push는 수행하지 않았다.
