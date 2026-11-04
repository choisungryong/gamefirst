# 보스 체력 막대와 알림 겹침 개선

실제 제품의 보스 체력 막대는 논리 y93–102이고 임시 알림은 y80–107이어서 서로 겹쳤다. 보스 격노·회복약·장비 획득 알림이 체력 막대 뒤에 가려질 수 있었다. HUD27은 막대가 보일 때 알림을 막대 아래10px(y112)로 배치하고, 일반 전투에서는 원래 y80을 유지한다. 알림 문구·수명·게임 상태는 바꾸지 않는다.

fixture01: 정상 냉기23000tick 상태, 기존 표시 속성(y80)과 새 표시 비교.1920×1080/1440×810/1280×720의 세 알림 영역 분리·원래 겹침 재현·일반 전투 위치·만료·전체core불변 검사 모두 통과했다. import/check/GPU exit0/stderr0. 실제6PNG 중1920전후와1280후3장을 직접 검수. 조작된 알림 문구 fixture이며 자연 발생 이벤트 증거와 구분한다. stage/source/raw 보존.

후보27 패키지는 HUD27만 추가하고 assembly HUD23→27만 변경했다. core16/World22/Actor25b/Input21/FX26 유지. World27바닥·Actor26피격 연구는 미채택. 기존 후보26 이하 EXE·stage·사용자23profile와journals를 보존했다. 패키지 import/export/PCK/30sim초 headless/behavior probe 통과.

실제 패키지 boss-phase01: 정상획득 냉기 정책을21983tick까지 재구성해 처음 발생한 실제boss_phase 이벤트를 원래_consume_events로 처리. 격노 안내의 정확한 문구/가시성/막대와의분리/실제HUD27로딩/1920×1080캡처/독립전체core일치 확인,exit0/stderr0. 해당실제PNG를 직접 열어 가독성 개선 확인. 실제EXE의고정시점 GPU검수이며 정상속도수동전체·live전체·실청취·최종성능3회 승인으로 확대하지 않는다.

full27/independent-audit01의34항목 전부pass: 기존EXE,14부터27까지불변stage,기본23저장3파일,백업26assembly,새freeze,검수HUD정확바이트,30초core10상태동일,actual이벤트/로드/화면과quiet,PCK재파싱 포함. 모든 실행terminal,동일검사재실행금지.
