# 후보32 현황 · 2026-11-05

제품은 Core16/World31d/Actor32b/HUD27/Input21/FX26. 일반 적·중간 정예의 역할별 상체 준비와 회복 동작을 추가했다. 공격의 실제 시점·판정·방향·성장·드롭은 유지한다. EXE SHA 8bf1dd10436b84b04b7108e23940d9d271f245e23997834e8b727981cdb4b10e /130082400bytes/runtime132-stage134-PCK241. package세션23184 exit0/import-export-PCK-30sim초headless-releasebehavior통과.

- mapped01/02 정상120+공격180frame 비교에서 전체frame/tick/corehash동일.32첫안회복이약해미채택/원시와소스보존.32b채택.
- directions01/session93698 headless·GPU exit0-stderr0,16검사pass:4역할×4방향 mid-windup/mid-recover에서상체만변함/하체동일/20회반복누적없음/지팡이손추적/정지·빙결자세유지/전체core복원/풀224유지. 전후4PNG전부직접검수. 모든역할4방향연속전체영상승인은아님.
- cost01/session80559 source30c/32b순차각2초warmup+10초OS시계/후반정상냉기19800체크포인트. p95 7.357→7.831ms,p99 8.395→8.899,max11.647→12.612,33ms초과0/0,draw333동일.실제1920×1080/무제한FPS/VSyncoff/ignorefocus/profileoff/측정중캡처없음.각독립전체core같음.정식focused최종3회아님.
- 실제EXE elite01/session59752 check/GPU exit0-stderr0. 주입없이정상화염성장에서처음만난비최종정예준비6077tick부터원livecontroller6377tick까지300tick.실제공격발동193pose표본/독립전체core동일/profileoff. windup/release/recover/end 4PNG직접검수. 준비와회복차이가읽히고위험원·주인공표식유지. 타격순간화염plume이몸일부를가리는가독성한계남음.

이전31전체GPU완주는31증거그대로이며32전체완주로승격하지않는다.32최종수동전체·실청취·최종focused1080p성능미완료.브라우저/WindowsUI도구커널경로오류로새기본입력/실제브라우저검수미실행. 추가파이프라인·GitHub보류. 모든이번Godot종료/기존검사중복실행금지. 기존후보및사용자23복원후/29rev2사본·핀보존확인(PRESERVATION01).

다음실질품질작업은화염타격연출의몸가림감소와장비발견·보스보상의시각강조. 같은제품으로남은실제전체·성능·입력·청취검수필요. 최종목표active/2·3장미착수.
