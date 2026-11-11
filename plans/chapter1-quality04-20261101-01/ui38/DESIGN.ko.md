# UI38 — 금기 서약의 회랑

구현 방향: 생명만 붉은 인장으로 강조하고, 중앙 전투 공간은 비운다. 탄화 석재 #17191B / 석재 #34393A / 황동 #AA8D58 / 상아 #E7DFC9 / 생명 #B83F51. 기존 한국어 고딕 본문과 명조 제목을 유지한다. 기존37과 다른 새 HUD 상속 파일만 추가했다.

배치: 상단 왼쪽 실제 목표, 상단 오른쪽 장비·정지·음소거. 하단 생명 인장 / 실제 생명·레벨·XP / 세 속성 / 실제 회피·회복약. 기존 마나가 없으므로 새 자원을 만들지 않는다. 카드와 비교 화면은 석재·황동 표면과 동일 버튼 상태를 사용한다. 희귀도 색과 속성 색은 기존 계약을 유지한다.

입력: 공식 Godot4.5 Control 문서 https://docs.godotengine.org/en/4.5/classes/class_control.html 의 grab_focus, focus_next, focus_previous를 사용한다. 모달 첫 버튼으로 deferred focus, Tab/ShiftTab은 모달 내부 순환. 닫힘 후 유효한 이전 컨트롤 포커스를 복원한다. 버튼 normal/hover/pressed/disabled와 별도 투명 focus 윤곽선을 정의했다. 상속36의 choice token/id, compare_item, 장착, 스크롤 복원, discovery queue, boss/toast 위치, 보관함·저장 신호는 유지한다.

검증 전 상태: 원본37·EXE·프로필·root assembly 변경 없음. 별도 preview stage에서 프로필을 구성하지 않는 UI 단독 실제 코어 probe로 먼저720/1080 렌더링과 버튼 입력을 확인한다. 이 문서는 시각 승인이나 전체게임 성능/플레이 완료 증거가 아니다.
