# candidate02 코드 품질 / anti-pattern 독립 검토

2026-10-31. 실행 검증과 구분한 소스 검토다. 동결 구현을 수정하지 않았다. 03 변경분은 별도 검증에서 검토한다.

## 코드 품질 검토

| 검토 항목 | 확인 결과 | 한계 / 후속 |
| --- | --- | --- |
| 책임 분리 | catalog 검증, 순수 growth 상태, fixed-step combat, normal-input pilot가 분리되어 있다. Resolver 재사용 경로도 좁다. | `_step_enemies` 하나가 AI 상태·전조·공격·피해 분기를 맡고 세 kind 문자열 및 상수를 직접 안다. 다음 장에서 적 유형이 늘 때 data/state 처리 분리를 검토할 만하다. 현 구간 진행 차단은 아니다. |
| 상태 일관성 | mode 우선순위는 terminal → external pause → inventory → choice → playing이다. 영구 profile에 의존하지 않는다. detached 반환과 paid context 복사 경계를 독립 테스트했다. | live dictionary는 명시적인 read-only 관례이고 언어적으로 보호되지 않는다. 표현층에서 이를 쓰면 계약 위반이다. 임의 외부 dictionary 변형을 저장 검증 기능으로 오인하면 안 된다. |
| 실패 경로 | catalog/growth configure는 검증 후 교체한다. 실제 정예 spawn 실패는 retry 권한을 유지한다. pilot output 경로는 overwrite를 거부한다. | `growth.award_xp` 반환을 pickup에서 별도 분기하지 않지만 현 코어 XP는 검증된 양수 내부 상수이므로 실패 입력을 생성하지 않는다. 외부 XP 입력 API로 확장할 때는 재검토가 필요하다. |
| 수명 / 중복 | epoch, 단조 entity ID, corpse cleanup, per-projectile hit set, Arc cast-wide hit set, proc budget이 분리되어 있다. | ID가 run restart 때 재시작하므로 표현자는 명시된 epoch 및 event reset 계약을 지켜야 한다. 이 검증은 뷰의 reset 구현을 확인하지 않았다. |
| 수치 / 자원 | raw 정수 피해는 검증된 Resolver로 전달된다. entity/projectile/orb/gear/event 상한이 있다. XP overflow는 보존한다. | 장비 바닥/소유 상한을 한 조기 return으로 묶어 정예 직접 보상을 누락하는 실제 경계 결함을 발견했다. 별도 REPORT 참조. |
| 검증 가능성 | 유한한 60Hz 코어, 분리 RNG, normal-input pilot 및 실제 exit를 갖는다. 6정상 사례 결과 전체가 재현된다. | 기존 manifest6개만으로 Resolver/Stats 의존성까지 과거 동결되었다고 입증할 수 없다. 새 후보에서는 실행 의존성을 함께 pin하는 것이 좋다. |

코드 품질 측면에서 실제 발견된 수정 필수 항목은 바닥 포화 시 정예 보상 누락이다. 개방 공간의 군중 겹침, 벽/내비게이션 부재, 제한된 냉기 파쇄는 이미 계약에 명시된 범위이고 검토자가 새로 완료를 주장하지 않는다.

## Anti-pattern 검토

| 점검 | 판정 근거 |
| --- | --- |
| 테스트 통과용 시간 승리 / 무조건 종료 | 없음. clock100초로 승리하지 않는 fixture와 실제 elite 사망 전이를 확인했다. victory 분기는 `_damage_enemy`의 elite death에서만 설정한다. |
| 정상 pilot의 결과 조작 | 없음. 원본 pilot은 HP/XP/아이템/스폰/피해/정의에 쓰지 않는다. 실제 이동·dash·offered card 선택·owned gear equip만 호출한다. 합성 fixture는 별도 script로 분리되어 있다. |
| 실패 숨기기 / exit0 강제 | 없음. 원본 combat 및 growth tests는 실패 배열로 quit1 한다. 의도 실패를 실제 exit1로 재확인했다. independent 최초 도구 오류도 삭제하지 않았다. |
| 발사 후 효과를 현재 스킬/장비에서 다시 읽기 | 없음. damage는 paid context.effects를 쓰며 효과 복사와 다음 예약 보존을 독립 실행으로 확인했다. |
| 무제한 연쇄 / 죽은 개체 재보상 | 없음. Arc 전체 dedup, 전역 hit budget, proc_depth 및 사망 guard를 실행했다. 다른 속성의 서로 다른 탄 다중 명중은 계약상 의도다. |
| 시각 이벤트가 실제 피해를 결정 | 없음. core가 먼저 수치 상태를 적용하고 events를 방출한다. event overflow가 게임 수치 자체를 되돌리지 않는다. 실제 화면 동기화는 별도 검수다. |
| 자료 조작 / 보호 자산 복사 / 기존 save side effect | 이번 소스 경로 및 검증 작업에서 없음. core catalog는 프로젝트의 독립 JSON READ를 수행하고 profile I/O 경로가 없다. 이번 작업은 외부 자산이나 원본 게임 파일에 접근하지 않았다. |
| 광범위 예외 삼키기 / 새 의존성 우회 / 신뢰하지 않는 shell | 없음. 구현은 GDScript이며, verifier subprocess는 argv 배열과 실제 returncode를 보존한다. |

이 표는 확인한 소스 경로에 대한 한정 검토다. 전체 제품/렌더러/오디오/배포물 보안 감사나 visual quality approval을 뜻하지 않는다.
