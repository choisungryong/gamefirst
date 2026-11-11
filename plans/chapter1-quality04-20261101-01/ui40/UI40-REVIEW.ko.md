# UI40 소스 품질·금지 패턴 검토

2026-11-11. 신규 HUD40 한 파일과 DESIGN/STATUS, 기존 HUD38→36→17→chapter_hud→cloister_hud 상속 경로를 검토했다. 기존47개 fixture 검사를 다시 실행하지 않았다.

**판정: 발견한 초기 승리 포커스 결함 수정 후 통과.** root가 이미 확인한14개 실제 Forward+ fixture 캡처의 시각 판단과 별도로 소스·입력 경로를 확인한 결과다. 제품 패키지 통합·최종 성능·실제 수동 승리 승인을 뜻하지 않는다.

## 검토한 경로

- 보관함 필터는 새 배열에 보유 record 참조를 모아 정렬한다. profile_state.items와 실제 장비를 변경하지 않는다. 슬롯/등급/정렬 후 선택은 storage_id로 찾고, 필터 결과에 없는 선택은 첫 record로 옮긴다. 빈 결과에는 동작 버튼을 만들지 않는다.
- 장착/해체 버튼은 실제 선택 record의 storage_id를 기존 신호에 전달한다. 현재 장착 여부도 equipped의 storage_id와 비교한다. 장비 uid와 혼동하거나 저장을 직접 쓰지 않는다.
- 선택 변경은 기존 목록 스크롤을 저장하고 새 ScrollContainer에 이연 복원한다. 필터 변경만 scroll reset을 요청하며 해체 이후 사라진 선택은 다음 목록에서 재선택한다. 버튼과 필터는 상속 포커스 순환에 포함된다.
- 결과 화면은 실제 inventory/equipped/pending_rewards/성장/tick/kills/profile_note를 읽고, 시작 장비가 보유 수에 포함됨을 표시한다. 실제 _elite_reward_uid가 보유 목록에 있을 때만 파수왕 보상을 보여준다. 저장 완료 문구를 자체로 만들지 않는다. 저장 재확인·보관함·장비 확인·재도전은 기존 신호를 사용한다.
- 경로는 실제 ZONE_NAMES/seals/objective의 zone/entered/destination/boss_phase를 읽는다. 세 구역과 동쪽 이동 안내는 현재 ZONES=[(0,0),(48,0),(96,0)] 및 기존 objective 안내와 일치한다. 상세 지형이나 적 위치를 꾸며 표시하지 않는다.
- _build_result40은 inherited modal 구성을 정리한 뒤 content box 하나로 교체한다. 상속 부모가 기대하는 초기 구조를 먼저 구성한 뒤 바꾸며, 이후 포커스 요청은 현재 모달을 탐색하므로 제거한 버튼을 잡지 않는다.

## 발견·수정·좁은 확인

HUD17은 첫 승리 화면을1.3초 숨긴다. 기존 HUD38/UI40의 초기 이연 포커스는 숨겨진 overlay에서 반환하고, 나중에 visible만 켜질 때 모달 signature는 바뀌지 않아 새 포커스 요청이 없었다. probe03은 victory_age=1.5를 미리 설정했으므로 이 초기 경로를 포함하지 않았다.

root 승인으로 HUD40.sync에 overlay의 이전 visible을 기록하고, 승리 화면의 false→true 표시 전환에서만 `_focus_modal38.call_deferred()`를 요청하도록 최소 수정했다. 기존 지연·코어·저장·HUD38 파일은 변경하지 않았다. 변경 전 소스는 `reveal-focus01/chapter_hud_quality40.before.gd`에 보존했다.

신규 `ui40_reveal_focus_probe.gd`로 기존 별도 preview stage에서 실제 Forward+ UI를 짧게 실행했다. 결과 `reveal-focus01/RESULT.json`:6개 모두 통과, 실행 종료0·stderr 없음. 최초 승리 hidden, content box1개, 지연 후 visible, 실제 포커스 할당, Tab 모달 내 이동, 화면 저장을 확인했다. root 프로필 접근·저장·보상 호출·실제 승리는 없는 명시적 종료 상태 fixture다.

원시는 `reveal-focus01/execution.json`, `victory-revealed-1280x720.png`다. 화면에서도 결과 버튼의 포커스 테두리를 확인했다. 종료 후 Godot/Ashen 프로세스 없음과 GPU 반납을 확인했다.
