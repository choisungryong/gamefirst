# Phase 0 문서·소스 발견 결과

2026-11-07. 두 discovery 작업의 사실 보고를 root가 통합했다. 이 문서는 새 미술/효과가 이미 구현됐다는 증거가 아니다.

## 기준선과 참고 범위

- 활성 후보37: chapter1/chapter_one_view.gd:2–8의 Core37/World37c/HUD36/Actor36/FX36. root 기본 씬은 보존된 Baseline이며 제품은 ChapterOne이다.
- 최신 영상 분석: plans/chapter1-preproduction-20261031-01/SACRATA-ANALYSIS.ko.md. 대표 런의 시작·장비·성장·정예·드롭·보스·종료를 장면별 관찰했다. 전체 순간의 연속 시청·직접 조작·음향·내부 규칙 분석은 아니다. 이 문서의 당시 ‘기존 제품 한계’ 표는 현재37에 그대로 적용하지 않는다.
- 과거 소범위 관찰: C:/Project/ashen-sanctum/SACRATA-VIDEO-REVIEW.ko.md. 초기 관찰과 대표 품질 장면 우선 원칙을 참고한다.
- 공식 [SACRATA Steam 소개](https://store.steampowered.com/app/3201450/SACRATA/?l=english)는 캐릭터 매력을 소개한다. 특정 획득/성적 장면이나 내부 구현을 확인한 근거는 아니다.
- 성인 매력 원요청: plans/chapter1-quality04-20261101-01/ART-DIRECTION-ATTRACTION.ko.md. 성인 의상/실루엣·의식 초상·후속 성인 서큐버스는 아직 제작 계획이다.

## 기존 UI 인터페이스: 복사 가능한 실제 계약

- cloister_hud.gd:3–11의 start/choice/equipment/close_equipment/equip_item/pause_toggle/retry/mute_toggle/motion_toggle 신호.
- chapter_hud.gd:3–10의 stash_show/stash_equip/stash_salvage/save_retry 및 profile_state/profile_note.
- chapter_view.gd:49–69의 setup/신호 연결; chapter_one_view.gd:43–65의 저장/키 처리.
- cloister_hud.gd:125–156의 스타일·라벨·바·버튼; :158–195의 표시 갱신; :237–239의 실제 token/card 선택.
- chapter_hud_quality17.gd:57–96의 장비 비교/스크롤; quality20:12–68의 중복 제거 알림 큐; quality27의 보스바 아래 toast; quality35의4개 자체 SVG 아이콘; quality36의 최신 속성 설명.
- chapter_run_stun36.gd:301–313의 실제 구역/목표/연결. 상세 미니맵이나 게임패드 전체 입력은 구현돼 있지 않다.

## 허용된 API와 공식 추가 확인

기존 경로에서 확인한 CanvasLayer, Control, Container 계열, Label/Button/ProgressBar, StyleBoxFlat, Theme/SystemFont, Texture2D와 _draw를 우선 사용한다. 테마 변경은 기존 add_theme_*_override 패턴을 복사한다.

추가 포커스/전환은 [Godot4.5 Control](https://docs.godotengine.org/en/4.5/classes/class_control.html), [포커스 안내](https://docs.godotengine.org/en/4.5/tutorials/ui/gui_navigation.html), [Tween](https://docs.godotengine.org/en/4.5/classes/class_tween.html)을 읽고 구현한다. 실제 API는 Control.grab_focus(), focus_neighbor_* 및 Node.create_tween()/Tween.tween_property()다. UI 입력을 소비하는 기존 mouse_filter와 accept_event 계약을 유지한다. 테마 항목을 일반 Object property처럼 set하지 않는다. UI 내비게이션 액션을 전투 이동으로 재사용하지 않는다.

## 효과·소리·모델의 현재 사실

chapter_view.gd:239–254의 표현 이벤트, quality36.gd의 실제 arc segments 및 stunned_until, quality33b의 희귀도 beam/halo는 이미 연결돼 있다. 기존풀상한은 초기 경계이며 성능 승인 수치가 아니다.

combat_audio.gd는 Kenney CC0 가공19variant/13voice와 우선순위를 사용한다. growth/의식은 equip 소리를 재사용하고, 확인한 경로에는 완성된 적응형 음악이나 전용 보스 경고가 없다. 실제 청취는 이번 discovery에서 하지 않았다.

현재 mage는 출처/파생 동작이 있는 CC BY-SA3.0 자산, chained demon은 CC BY3.0 자산이다. 원화·텍스처·3D·리그·애니메이션의 제작 상태와 출처를 따로 기록한다.

## 남는 불확실성

SACRATA의 모든 효과·선택 연출을 새로 관찰한 것은 아니다. 추가 대상은 장면/타임코드와 관찰 항목을 먼저 정해 확인한다. 현재37도 최종 성능·사용자 재미·실청취 완료가 아니다. 사용자 플레이 도중에는 자동 입력·강제 종료·저장 기준 회귀를 하지 않는다.