# C2 패키지 후보01 · 표현/패키징 코드 품질 검토

2026-10-31. 구현 담당과 다른 검토자가 `chapter1/chapter_view.gd`, `chapter1/view/*`, 재사용 음향 helper, 신규 builder 및 실제 패키지 증거를 검토했다. 코어03 기능 검증은 별도 독립 보고서를 따른다. 이 검토 중 런타임 소스는 수정하지 않았다.

**결과: 현재 후보를 실행·조작 검수하는 데 추가 차단 결함을 발견하지 않았다. C2 표현·재미·성능 품질 승인은 열려 있다.**

| 항목 | 확인한 근거 | 범위/한계 |
| --- | --- | --- |
| 책임 분리 | 시뮬레이션은 `CombatRun.step`과 공개 입력 API에 있고, 배우·효과·HUD는 읽기/사건 소비를 담당한다. 뷰가 hero/enemy HP·XP·드롭을 직접 변경하는 경로를 발견하지 못했다. | 공개 Dictionary는 관례상 읽기 전용이다. 언어 수준 강제는 아니다. |
| 모달과 입력 | 월드 좌클릭은 `playing`의 unhandled input만 받고 UI overlay가 입력을 받는다. I/Esc는 명시 API로 장비/정지를 바꾸며, focus loss는 기본 정지한다. choice·inventory·paused의 실제 우선순위는 코어가 정한다. | 실제 OS 입력·버튼 위치·focus loss·중첩 모달 확인은 부모의 별도 native QA 영역이다. 소스 검토로 통과 처리하지 않았다. |
| 자원 로딩 | PNG의 FileAccess 존재 여부에만 의존하지 않고 ResourceLoader import remap을 사용한다. 실제 EXE READY에 5개 역할 모두 4방향과 cast/hit/death가 있고 raw PNG fallback이 없다. | 미래의 잘못된 atlas JSON은 조용히 기하 대역으로 갈 수 있다. 이 후보의 정확한 자원은 검증됐으며, 후속 제작에서는 누락을 명시 오류로 처리하는 개선이 가능하다. |
| 런 재시작 | 배우의 enemy/event 상태, effects의 seq·debris·stroke·아이템 노드, 오디오 cue dedup, HUD 선택이 reset되고 view event cursor도 새 런에서 초기화된다. | 실제 재도전 중 입력/화면 검수는 native QA에서 확인한다. |
| 수명과 상한 | 탄384·XP400·파편1200·impact96·shadow513·stroke96, 기본 음향16 voices 등 표현 상한이 있다. enemy actor는 core가 보유하는 ID만 남긴다. | 매 프레임 새 ImmediateMesh 3개를 만들고 일부 배우 노드를 생성/해제한다. bounded라는 사실이 빠르다는 뜻은 아니며, 1080p p95 20ms의 원인을 이 검토만으로 이 경로에 귀속하지 않는다. |
| 전조와 효과 | line은 캡슐 폭/길이, fan은 실제 paid ray capsule들을 포함하는 보수적인 hull을 표시한다. 12각형 샘플 반경은 외접하도록 확장되어 있다. FX는 피해를 결정하지 않는다. | fan은 ray 사이 안전 공간까지 포함하는 보수 표시다. 최종 위험 가독성과 영상상의 일치 검수는 별도다. |
| 패키징 | 소스42개만 외부 staging으로 복사하고 staging의 project/preset만 바꿨다. 원래 project·export 설정을 수정하지 않았다. 실제 PCK78개 checksum/동적 자원 closure 감사가 성공했다. | builder의 보존 guard는 Python assert를 사용하므로 일반 Python 실행을 전제로 한다. 이번 명령에는 최적화 옵션이 없고 guard가 실행됐다. 재사용 도구로 확장할 때 명시 예외 검사로 강화할 수 있다. |
| 종료 | QA timer 종료의 actual0 및 오류/경고 없는 Godot log를 확인했다. audio stop 후 server release 대기가 있다. | 정상 OS 닫기 종료는 부모 native run의 실제 exit/log로 확인해야 한다. 합성음 실제 청취 승인은 하지 않았다. |

패키지 pilot은 명시된 정상 입력 driver와 focus 무시 QA 옵션을 사용한다. HP/XP/아이템/스폰/피해 주입 없이 78.15초 정예 처치, 813처치, 세 기술과 주력 진화를 기록했다. 이 한 번의 승리를 코어03 6사례 전부 승리로 바꾸어 보고하지 않는다. 코어03은 정상6회 중5승·냉기 seed71 패배를 보존한 상태다.

품질 잔여: 삼각형 풀·단순 기둥/박스 소품·바닥 반복, 4키프레임과 남쪽 전용 행동, 임시 합성음, 직접 청취·연속 영상 및 전체 5–8분 장 구성 미완료. 실제 1080p pilot p95는20ms로 목표16.67ms에 미달한다. PNG 동기 저장과 driver가 측정을 교란하므로 정식 GPU 판정으로 삼지 않는다.
