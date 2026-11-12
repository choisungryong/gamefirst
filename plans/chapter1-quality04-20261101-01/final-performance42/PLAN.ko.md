# 후보42 최종 성능 관문 준비

2026-11-13 실행 결과 갱신: 실제 패키지 검증 후 root가 실행했다. root동결은 runtime176+project/preset2=178이며 정확한 경로 집합으로 계약을 수정했다. 최종세션 final-20261113-a에서 동일 EXE3회 p95 14.177/14.345/14.172ms, 유효성·보존·관문 모두 통과했다. 아래 '준비만/미실행'은 초기 준비 당시 기록이다. 원시와 독립재감사 집계는 sessions/final-20261113-a/three-run-summary.json에 보존한다.

2026-11-13. 준비 소스만 작성했다. 엔진·GPU·실행·bind·프로필 변경은 수행하지 않았다. Actor42 microbench 비용 감소는 실프레임 개선의 증거가 아니다. 제품42 생성·최종 패키지 문서 확인·독립 소스 검토·root 실행 GO 후에만 다음 관문을 수행한다.

## 정확한 패키지 계약

full42/package42.py 사전준비 담당자와 ID `chapter1-full-candidate-20261113-42`, runtime176(41의175+chapter_actors_quality42.gd), stage178을 확인했다. EXE는 `C:/Project/d2r-combat-baseline/builds/chapter1/chapter1-full-candidate-20261113-42/AshenCloister-Chapter1.exe`, stage는 `C:/Project/game-research/build-staging/chapter1-full-candidate-20261113-42`로 고정한다. 패키지 docs 8개, closure ID·176개 고유 의존·178 stage·실제 EXE 경로/크기/SHA, integration 종료0/시간초과없음/launch_error null, PCK·통합·보존 success를 모두 요구한다. 제품42가 없으면 bind를 거부한다. 실제 문서의 최종176/178와 flags가 다르면 소스 검토 후 계약을 명시적으로 조정하며 관문을 조용히 낮추지 않는다.

현재 root는 향후42로 채택될 예정이므로 현재 root42 freeze만 검사한다. 과거37/38/40/41은 각 불변 original stage·자체 freeze manifest·EXE로 검증한다. 41의 성공 attempt02 외 원래 attempt01 보존 manifest/stage/EXE도 확인한다. 과거 root41로 되돌리도록 요구하지 않는다. 기존37 WIP·41 원시·제품 소스는 수정하지 않는다.

Quality42 사용자 폴더가 패키지의 승인된 현재41 바이트 fork로 먼저 존재해야 한다. bind 때 현재 모든 Quality 폴더의 main 및 전체 revision journal 집합/SHA를 고정하며 과거37/38/40 외41도 포함한다. 이후 정상 사용자 진행이 발생하면 결과 무효이며 프로필 복사·복원·삭제는 하지 않는다.

## 동일 측정 조건과 원시 보존

- 같은 실제 Windows EXE·observer·프로필 바인딩으로 run-01/02/03 고정3회만 허용한다. 새 세션마다 runtime 경로도 session+run ID로 고유하다. 같은 회차 재실행·추가 run·좋은 세 회차 골라 합치기·기존 파일 덮어쓰기를 거부한다.
- 실제 native MENU에서 root CUA로 창 focus 후 **서리창 시작**을 누른다. seed90131, view/core primary frost를 최초 playing·끝과 매 프레임 실제 view 값으로 감사한다. CLI 값만으로 증명하지 않는다.
- Forward+ 실제1920×1080, scale1/MSAA2, VSync off/FPS cap0/time_scale1, normal pilot, profile-off. autostart·ignore-focus·movie·fixed FPS·측정 중 캡처/녹화/입력로그/파일출력은 금지한다. 전후 PNG/live readback만 허용한다.
- warmup10초+sample60초. Time.get_ticks_usec 단조 callback 전체 간격과 끝 경계를 넘는 전체 간격을 보존한다. 긴 interval을 삭제하지 않는다. 누락 raw·callback 누락·카운터 후퇴·render/sim 무진행·focus/설정/크기 변경·기간/분위수/SHA 불일치는 무효다.
- 각 회차 유효성과 p95≤16.67ms를 모두 요구한다. 실패/메뉴 timeout 원시는 보존한다. 실패 원인 해결 뒤 새 세션 고정3회를 사용한다. 첫70초 정상 정책 대표 부하이며 전체 장 최악 부하·하드웨어 GPU 시간·모든 프레임60FPS·수동 완주·음향·미술 승인 증거가 아니다.

41 세션 final-20261112-a의 run-01은 유효 p95 20.636ms 목표 미달, run-02는 MENU timeout으로 미실측이다. 이는 3회 통과가 아니며42 결과로 재사용하지 않는다.

## root 실행 GO 이후 순서

단독 GPU/CPU 예약, 다른 엔진·게임·대량 검사 중지, 측정 구간 CUA 스크린샷 중지 후 수행한다. 명령은 향후 절차이며 이 준비 중 실행하지 않았다.

```powershell
python -B plans/chapter1-quality04-20261101-01/final-performance42/run_performance42.py bind --session final42-01
python -B plans/chapter1-quality04-20261101-01/final-performance42/run_performance42.py run --session final42-01 --run-id run-01
# READY 이후 root CUA focus + 서리창 정상 시작. 이후 측정 종료까지 캡처/입력 없음.
# run-02, run-03도 같은 세션에서 순차 실행
python -B plans/chapter1-quality04-20261101-01/final-performance42/run_performance42.py aggregate --session final42-01 --output three-run-summary.json
```

소유 PID만 timeout 후 정리하며 기존 사용자 프로세스를 종료하지 않는다. 각 출력은 exclusive write이고 무효·목표미달은 CLI 종료1이다. Python AST/import·command/run/session 경로·복사 차이를 정적으로 확인했다. GDScript 실제 parser·제품42 final docs/flags·실제 focus/서리창 시작·원시 CSV·3회 관문은 아직 미확인이다. 동결 소스 독립 review가 다음 단계다.
