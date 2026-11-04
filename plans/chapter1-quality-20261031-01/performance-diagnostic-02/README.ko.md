# 후보03 비정식 성능 진단02

2026-11-01, Asia/Seoul. 진단01의 uncapped 실행은 기존15000프레임 상한에 도달했다. 원시와 정정 문서는 보존하고, 같은 EXE/같은 일반 입력70초에 **120FPS 제한**을 걸어 전체 playing 구간이 상한 안에 들어가는지 한 번 확인한다. 제품은 바꾸지 않는다.

1920×1080/Forward+·delta smoothing 해제·VSync 해제·max-fps120·seed90131·기존 normal pilot·application quit70초다. PNG/movie/HP·XP·아이템·처치 주입은 없다. 표본 개수15000미만·game elapsed70·실제 종료를 반드시 확인해야 한다.

`diagnostic.py prepare`는 핀만 읽는다. root가 GPU를 할당한 후 `launch`를 부르면 숨긴 Python helper가 실제 EXE를 실행하고 즉시 PID를 반환한다. root가 CUA로 실제 창을 관찰/초점 확인한다. helper는 stdout/stderr·실제 exit·전후 핀·상한 도달 여부를 새 경로에 기록한다. `run`은 helper 내부용이다.

120FPS 제한은 약8.33ms의 프레임 pacing을 도입한다. 출력은 원시GPU 시간이나 원시단조시각이 아닌 엔진 delta의 p95다. 첫10초 제외·60초×3회·전체 프레임 초점 기록·최대180적 부하가 없으므로 **정식60FPS 통과가 아니다.** 기존 PNG QA 약20ms나 진단01의1.389ms와 직접 비교해서 개선율을 계산하지 않는다.
