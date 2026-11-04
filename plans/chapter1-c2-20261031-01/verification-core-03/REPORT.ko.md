# C2 core candidate03 독립 검증

2026-10-31. 새 검증 디렉터리에서 동결 구현을 수정하지 않고 실행했다. **candidate02의 바닥 포화 정예 보상 결함은 수정됐고, 회피의 12회 이동·18미래step 무적 경계도 명세와 일치한다.** 기능/경계 fixture는 통과했지만 정상 자동 입력 6회 중 냉기 seed71은 실제 패배한다. C2 밸런스·표현·재미·1장 완성 승인이 아니다.

동결 source-manifest SHA256은 `ca434d321d2ddc21a9d422c0d24e3bb8feb1f760adcedf137464ebd833aa8515`, combat_run.gd는 `a3a4d62e70779af99fb4e76c16e4222ae20062df91775326431bba3ce68286d7`다. Resolver/Stats·growth·전투·테스트·계약을 포함한 9개 파일의 현재 및 보관 사본이 검증 전후 모두 manifest와 일치했다. 원본 project 설정까지 이 manifest에 포함되는 것은 아니다. 전체 실행본/뷰/자산은 패키지 검증에서 별도로 pin해야 한다.

| 실제 실행 | actual exit | 결과 |
| --- | ---: | --- |
| 원본 test_combat_run.gd | 0 | 75검사, 실패 없음 |
| 같은 테스트 --prove-failure | 1 | 76검사, 의도 실패1 |
| 독립 경계 independent.gd | 0 | 114검사, 실패 없음 |
| 원본 normal-input pilot 3주력×2seed | 1 | success:false, 승리5/패배1 |

명령 argv·cwd·stdout·stderr·실제 returncode는 각 `*-execution.json`에 보존했다. wrapper의 exit0은 위의 **예상된 exit 조합과 pin 불변을 확인했다는 뜻**이며 normal pilot이 모두 성공했다는 뜻이 아니다. 새 파일이 이미 있으면 wrapper가 덮어쓰기를 거부한다. source와 candidate02의 원시 증거를 변경하지 않았다.

## 독립 경계 검증

- 바닥32개 상태에서 소유0/63/64개인 정예를 실제 `_damage_enemy` 사망 전이로 처치했다. 결과 소유1/64/65개, 직접 지급1회, 바닥32개 유지, victory를 확인했다.
- 기존 소유 객체/UID와 장착 UID가 그대로 유지된다. 새 보상은 unique UID와 rare/collected 상태, snapshot의 `elite_reward_uid`를 갖는다. 시체 재타격과 중복 지급 호출이 전체 snapshot을 바꾸지 않는다.
- 승리 뒤 public `open_inventory → compare_item → equip → close_inventory`로 실제 보상을 비교·장착하고 victory로 돌아왔다. 별도의 회수 버튼이나 외부 Array 삭제를 전제로 하지 않는다.
- 일반 pickup은64개에서 정예 예비 칸을 소모하지 않는다. 합성된 소유65개 상태에서도66번째 할당은 없다. 합성65개/보상UID0은 정상 API로 도달한 상태를 뜻하지 않으며, 이 검사는 상한 검사용이다.
- tick0 회피 후 13개 미래step의 x좌표는 `0.225, 0.450, …, 2.700, 2.700m`다. 12번 이동 후 멈춘다. step1–18에서 각 피해 시도가 무시되고 step19에는1HP 피해가 적용된다. tick179 요청은 거부되고 tick180에는 다음 회피를 요청할 수 있다.
- 이전 독립 검증의 발사 snapshot/예약 주기, legal unlock과 기술별 독립 시전, freeze windup/recover/dash, charger capsule·fan 실제 피해 경계, Arc dedup/proc budget, XP merge·event/entity 상한·generation 경계도 새 후보에 대해 다시 실행했다. 이들은 합성 fixture이며 일반 플레이로 표시하지 않는다.

## 정상 입력 재현

| 주력 | seed | 실제 결과 | 초 | 처치 | 최대 동시 생존 |
| --- | ---: | --- | ---: | ---: | ---: |
| Ember | 71 | victory | 80.1167 | 808 | 94 |
| Ember | 907 | victory | 77.5167 | 788 | 80 |
| Frost | 71 | **defeat** | **64.9** | **237** | **179** |
| Frost | 907 | victory | 88.85 | 952 | 179 |
| Arc | 71 | victory | 88.4333 | 983 | 155 |
| Arc | 907 | victory | 75.1333 | 783 | 179 |

기존 author03 results.json과 이번 normal-results.json은 CPU 소요 시간인 `cpu_wall_us`만 제외하면 전체 구조가 같다. 냉기 seed71은 HP0, 레벨10/XP299, 주력 진화와3기술, 획득 장비6개 상태에서 정예 등장 전에 패배했다. event overflow는0이다. 이 실패를 삭제하거나 seed를 바꾸지 않았다.

원본 pilot은 이동·회피·실제 제시된 카드 선택·소유 장비 장착만 호출한다. HP/XP/item/spawn/kill/정의 주입은 없다. 자동 입력도 패배할 수 있으므로 이 결과만으로 코드 결함이나 모든 사용자에게 불가능한 빌드라고 단정하지 않는다. 동시에 6사례 완주 성공 또는 냉기 밸런스 승인을 주장할 수 없다. 실제 조작·가독성·군중 압박/냉기 성장 리듬의 후속 검토가 필요하다.

## 코드 품질·anti-pattern 검토

검토 범위는 보존된02→03 diff와 현재 core 의존성·normal pilot, 이전 독립 fixture 경계다. 별도 `static-scan.json`에 검색 argv와 원시 결과를 보존했다.

| 확인 항목 | 결과 |
| --- | --- |
| 정예 직접 지급과 일반 바닥 상한 분리 | 정예는 전용 UID guard와 총65 상한을 사용한다. 일반 드롭/회수는64 상한을 유지한다. 소유 장비 교체/삭제가 없다. |
| 보상1회·재시작 수명 | `_elite_reward_uid`는 새 런에서0으로 초기화되고 지급 시 기록된다. 기존 사망/terminal guard와 함께 중복을 막는다. |
| 명세와 실제 회피 경계 | step 선증가를 반영해 이동은 `<=`, 무적 만료는 요청tick+19다. 독립 미래step 실행으로 확인했다. |
| 정상 pilot 성공 조작 | 없음. 원본 pilot hash는 고정이며 failure를 actual1로 그대로 반환한다. |
| 시간만 지나서 승리 | 새 변경에 없음. 정예 사망 전이가 victory를 결정한다. |
| paid-context·시각/수치 경계 | 변경하지 않았다. 발사 후 변경 불변과 proc 상한 회귀를 다시 확인했다. |
| 기존 save/profile I/O | core에서 catalog JSON READ 이외의 파일 접근, user://, profile write 경로를 찾지 못했다. pilot WRITE는 명시된 새 결과 JSON뿐이다. 이번 검증은 기존 사용자 저장 파일을 열거나 쓰지 않았다. |
| 실패 숨김·증거 덮어쓰기 | intentional1과 normal1 모두 보존했다. 새 wrapper는 출력 기존 존재를 거부한다. |

추가 진행 차단 결함은 발견하지 못했다. live Dictionary가 언어적으로 불변이 아닌 read-only 계약이라는 점, 적 AI를 한 함수의 kind 분기로 확장하는 구조, 실제 군중 local separation/벽/내비게이션 부재는 앞선 보고서의 한계로 유지한다. 이 검토는 뷰/자산/내보낸 실행본의 독립 검증을 대체하지 않는다.

아트·연속 영상·실제 음향 청취·OS 입력·GPU 성능·사용자 재미·5–8분 장 전체는 이번 headless 검증의 대상이 아니다. 커밋/업로드/원작 자산 접근이나 기존 증거 수정은 하지 않았다.
