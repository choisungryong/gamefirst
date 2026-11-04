# HUD·화염 경계 수정 v02

2026-11-01, Asia/Seoul. 통합 preview02에서 발견된 기술명 세로 잘림과 화염 billboard의 사각형 경계를 대상으로 두 파일만 수정했다. 기존 v01 보고서·33개 사본·실패 증거와 v02 수정 전 두 파일은 보존했다. 중단 전 이미 작성된 두 수정의 상태를 이어받아 검증했고 추가 제품 파일을 바꾸지 않았다.

`cloister_hud.gd`의 기술명 Label은 폭140px·높이46px 이상을 예약하고 자동 줄바꿈을 끈다. 이름/랭크의 의도한 줄바꿈만 사용한다. 긴 문자열에 대한 마지막 방어로 clip/ellipsis를 설정하지만, 현재 세 진화명과 랭크는 검사한 해상도에서 모두 전체 폭으로 들어갔다.

`flame_bloom.gdshader`는 네 UV 가장자리 전에 알파와 발광이 함께0으로 사라지는 support를 사용한다. dome·noise·폭이 좁아지는 tongue와 별도 hot core를 곱하며 quad 전체를 덮는 고정 주황 에너지를 제거했다. 이것은 소스 변경 설명이다. **실제 GPU 컴파일·렌더된 실루엣과 연속 전투의 가독성 통과를 뜻하지 않는다.**

## 검증과 재현

`attempt04-raw/`에 정확한 argv·실제 exit·UTF-8 stdout/stderr 원본 바이트와 JSON을 보존했다. fixture는 전투가 없는 별도 SubViewport에 실제 HUD를 붙이고, 표시 경계 검사용으로 세 기술을 모두 랭크4·진화 상태로 지정한다. 이는 일반 플레이의 성장/승리 증거가 아니다.

- 현재 HUD:1440×810·1920×1080·1600×900에서99검사/actual exit0/failures[]/stderr 없음. 각 기술명2줄 모두 표시되고, 폭255–415px·높이47px로76px짜리 하단 프레임과 viewport 안에 들어간다. 가장 긴 현재 줄은94px다. HP/XP/상태/회피도 viewport 안에 있다. HUD sync 전후 전체 코어 snapshot은 같다.
- 의도 실패:100검사/actual exit1, 실패는 intentional negative 하나다.
- 같은 fixture로 보존한 v01 HUD 로드:99검사/actual exit1. 기술명 폭1px·20–22줄·571px 높이 하단 프레임으로 세 해상도 모두 화면 밖으로 내려가는 원래 문제를 재현한다. 검사 자체가 실제 잘림을 잡는다는 근거다.

Font.get_string_size와 Control.get_global_rect 형식은 [Godot4.5 Font 문서](https://docs.godotengine.org/en/4.5/classes/class_font.html#class-font-method-get-string-size), [Control 문서](https://docs.godotengine.org/en/4.5/classes/class_control.html#class-control-method-get-global-rect)의 예를 따른다.

최초 fixture는 Variant 타입 추론 parse error로 세 실행이 모두 실패했다. 해당 fixture/명령 결과는 v02 루트와 `test_layout-parse-failed.gd`에 남겼다. 타입을 명시한 attempt02는99/100/99 결과를 냈고 JSON 자체는 UTF-8이었지만 바깥 콘솔의 한글 표시가 깨져 보였다. 원본 바이트를 남기려던 attempt03의 CP949 가정은 decode error를 냈고 그대로 보존했다. attempt04는 원본 바이트를 먼저 저장하고 strict UTF-8로 해석해 같은 결과와 정상 한글을 확인했다. 앞선 기록을 유효 통과로 합치지 않는다.

`FREEZE.json`/`source-manifest.json`은 v01 소유33파일 중 두 파일만 바뀌고 나머지31개·코어03의9pin·기존 baseline51이 일치함을 확인한다. 두 변경 파일의 새 사본은 `source/`에 있다. GPU는 실행하지 않았다. 화면·연속 영상·실청취·독립 검토·최종 패키지 감사는 별도 후속 관문이다. 커밋·업로드·저장 변경은 없다.
