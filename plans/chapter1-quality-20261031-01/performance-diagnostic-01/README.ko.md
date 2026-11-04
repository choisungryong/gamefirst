# 후보03 성능 진단 준비

2026-11-01, Asia/Seoul. 제품을 수정하지 않고 같은 후보03 EXE를1920×1080/Forward+로 실행하는 **비정식 진단**이다. 기본 `prepare`는 핀과 로컬 Godot CLI 도움말만 읽으며 게임/GPU를 실행하지 않는다. `run`은 root의 GPU 일정 할당 이후에만 호출한다.

`--delta-smoothing disable --disable-vsync --max-fps 0`으로 표시 주기·delta smoothing 영향을 줄이고, 기존 일반 입력/선택/장착 드라이버·seed90131을70초 실행한다. PNG·movie·HP/XP/아이템 주입은 없다. 실제 창은 root가 CUA로 확인하고 초점을 맞춰야 한다.

현재 실행본의 결과는 모든 playing 프레임0–70초의 delta p95 하나다. 원시 프레임 시간·초점 기록이 없고, 첫10초를 제외하지 않으며,60초×3회도 아니다. 숫자가 작더라도 정식60FPS 목표 통과라고 표시하지 않는다. 기존 짧은 PNG QA의 약20ms와 조건이 다르므로 단순 우열로 해석하지 않는다.

```powershell
$diagnosticPython = 'C:\Users\twins\AppData\Local\Programs\Python\Python310\python.exe'
$diagnosticTool = 'C:\Project\d2r-combat-baseline\plans\chapter1-quality-20261031-01\performance-diagnostic-01\diagnostic.py'
& $diagnosticPython -B $diagnosticTool prepare
# 아래 실행은 root의 GPU 할당 이후에만 수행한다.
& $diagnosticPython -B $diagnosticTool run
```

원본70개·코어9개·baseline51개·현재/이전EXE3개·사용자 저장2개를 전후 비교한다. 원시 stdout/stderr·정확한 argv·PID·actual exit·경고·결과 JSON을 새 경로에만 저장하고 이전 실행이나 증거를 덮지 않는다.
