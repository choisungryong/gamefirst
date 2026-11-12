# 최종 성능41 독립 소스 검토

2026-11-12. **발견한 두 결함 보강 후 소스 단계 통과.** 실제 제품41 GDScript parser와 측정3회는 아직 수행하지 않았으므로 성능 통과가 아니다.

## 실제 결함과 수정

1. 회차 출력 경로가 세션과 무관한 quality41-run-01 형식이라, 실패 원시를 보존한 새 세션도 같은 디렉터리 때문에 시작할 수 없었다. 런타임 경로와 독립 감사의 기대 경로에 불변 session 이름을 포함했다. 기존 경로를 지우거나 덮어쓰지 않는다.
2. 명령 인수의 primary=frost만 확인하면 실제 메뉴에서 다른 기술을 눌러도 view.start_run이 primary를 바꿀 수 있었다. 관측기에 첫 playing/종료 시 실제 view 시드·primary와 코어 growth primary를 기록하고, 매 프레임 view 시드·primary의 동일성을 확인했다. Python 독립 감사는 두 시점 seed90131/서리창 및 코어 primary와 빈 오류 목록을 요구한다. 성장 snapshot은 시작·종료 때만 읽는다.

수정 파일은 run_performance41.py, frame_probe_render41.gd, PLAN.ko.md다. performance41_observer.gd와 제품·프로필에는 수정하지 않았다.

## 유지한 관문

- full41의 정확한 build ID/175개 명시 의존/실제 EXE 크기·SHA와 통합·PCK·최종 보존 성공을 요구한다. 과거37/38/40은 자기 스테이지·manifest·EXE로 검사하며 현재 root를 과거 버전으로 되돌리지 않는다.
- 바인딩 시 현재 Quality 프로필 본문·모든 journal 집합/SHA와 관측기 두 소스를 고정한다. 세 회차와 집계에서 동일성을 재확인하며 정상 사용자 진행이 생기면 무효로 멈춘다. 저장 복원·삭제는 없다.
- 같은 세션의 run-01/02/03만 집계하고 기존 회차 출력/감사 파일을 덮어쓰지 않는다. 잘된 회차만 골라 섞지 않는다.
- 실제 Forward+1080p, scale1/MSAA2/VSync off/FPS0/time_scale1 조건이다. 메뉴에서 실제 native 시작을 기다린다. autostart/ignore-focus/고정FPS/movie/측정 중 캡처·로그·파일 출력은 금지한다.
- warmup10초 이후 sample60초의 전체 단조 callback 간격과 최종 경계 전체 간격을 보존한다. 긴 프레임을 제외하지 않으며 경계 손실·샘플 부족·누락 callback·카운터 후퇴·렌더/시뮬레이션 무진행·focus/크기 변경·raw SHA/분위수 불일치를 독립 감사에서 거부한다.
- 무효 또는 목표 p95 미달은 CLI 종료1이다. 이는 첫70초 정상 pilot 대표 부하이며 전체 장의 최악 부하·수동 승리·실청취·모든 프레임60FPS를 증명하지 않는다.

Python AST/import 및 서로 다른 세션의 런타임 출력 경로 분리를 정적으로 확인했다. 최종 GDScript parser/제품41 계약 일치/실제 창 focus·서리창 시작/CSV·3회 결과는 root의 실행 GO 후에 확인해야 한다.
