from pathlib import Path
import json,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={};checks['product27_freeze']=all(sha(R/n)==h for n,h in read(B/'full27/FINAL-SOURCE-FREEZE.json').items());checks['all_prior_exes']=all(sha(R/n)==h for n,h in read(B/'full27/ADOPTION.json')['preserved_exes'].items());profile=read(B/'full23/runtime/default-profile-preserved.json');checks['saved_profile3']=all(sha(Path(profile['path'])/n)==h for n,h in profile['pins'].items())
for name in ['fixture01','fixture02','replay01']:
 info=read(B/f'actor28/{name}/source.json');checks[name+'_source_preserved']=all(sha(Path(info['stage'])/n)==h for n,h in info['pins'].items())
checks['fixture02_checks47']=len(read(B/'actor28/fixture02/RESULT.json')['checks'])==47 and all(read(B/'actor28/fixture02/RESULT.json')['checks'].values());checks['replay_core']=read(B/'actor28/replay01/RESULT.json')['same_complete_core']
out=B/'actor28/POSTFLIGHT01.json';assert not out.exists();out.write_text(json.dumps(dict(checks=checks,passed=all(checks.values()),scope='Preservation and development evidence only. First fixture01 raw result overwritten by diagnosis is explicitly excluded; see failure record.'),indent=2));assert all(checks.values())
browser=B/'full27/book-v25/BROWSER-REVIEW01.json';assert not browser.exists();browser.write_text(json.dumps(dict(pages=36,cases=72,widths=[1440,390],main_each=True,h1_each=1,overflow=0,complete_broken_images=0,lazy_pending_cases=23,viewport_reset=True,screenshot_reviewed=True,video=dict(duration=7.8,width=1920,height=540,ready=4,error=None),scope='Actual IAB new tab. File refs1360/missing0. Video metadata only; not playback/normal-speed continuous motion approval. Lazy images below viewport not all forced.'),indent=2))
note='''# 최신 재개 — 2026-11-04 / 제품27 유지 · Actor28 미연결 보완시안·도감v25

현재제품27/rootfreeze불변. 먼저actor28/REVIEW.ko.md와FAILURE-AND-PRESERVATION.ko.md를읽는다. 기존26피격source복사한새Actor28은상체9bone/13캐시/.2초최대.85혼합+Spine1반동최대.238rad,회복동안paid attack_direction표시유지. 다리로컬포즈/core좌표/공격규칙불변. 아직제품미연결/28EXE없음. World27바닥역시미채택.

fixture01 session87159는47항목true에도ObjectDB종료경고stderr124로실패.상세verbose진단은경고없이끝났지만같은stage결과파일을재기록한보존실수발생;첫RESULT원바이트미보존/원경고·source/log보존/상세사고문서따름. 첫실행quiet성공으로승격금지. 같은고정출력재실행금지.

motion01 session17618:첫28+source25b복제4역할4방향8시점64PNG/quiet/원core복원.4장직접검수했으나약한반응미채택.보완fixture02 session35854 새stage/47checks모두pass/headlessquiet.추가흉곽반동·freeze/4modal/공격우선/하체동일/지팡이손/회복방향/재사용/만료/원core복원. motion02 session1978 새28+25b동일64PNG/quiet/원core복원.7장직접검수,반동읽히지만최종승인아님. film01 7.8초1920×540MP4는8개hit시점각.12초홀드/북동남서각2반복/왼25b오른28/무음의느린샘플자료,실시간연속영상이아님. 영상전체직접재생검수아직안함.

replay01 준비14143 terminal/GPU미시작후별도GPU59871/PID7856 terminal exit0-stderr0.현재27source기반+Actor28만대체/정상화염16000→16600tick10sim초fixed60/648혼합/독립전체core동일/224생성195재사용끝173.4PNG중live-3.0 한장직접검수. 실제28EXE/manual/real-time performance/fullchapter증거아님. POSTFLIGHT01 제품27freeze·기존EXE·기본23저장3·세시안stage source핀모두불변. 모든이번프로세스terminal,동일검사중복금지.

最新도감full27/book-v25/dist/actor28.html,36HTML/1360refs/missing0. IABbrowser2 새탭/36×1440/390폭72cases main/h1=1/overflow0/completebroken0/lazypending23구분,viewportreset/screenshot직접검수/markDeliverable. video ready4/errornull/7.8秒/1920×540은메타데이터확인만. 이전v24이하모두보존.

다음실질작업: 공격windup→release→recover의paid방향대기존이동방향전후연속검수,보완피격정상속도짧은연속영상(현재느린sample을대체증거로쓰지말것),추가CPU비용확인후채택판단. 현재27의수동전체·실청취·최종동일EXE성능3회·공간깊이/공격실루엣최종질감미완료. 과거수동입력왕복지연실패동일방식반복금지. 목표active/2·3장미착수.

---
'''
p=R/'HANDOFF.md';prior=p.read_text(encoding='utf-8');p.write_text(note+prior,encoding='utf-8');print('ACTOR28 POSTFLIGHT + BOOK25 + HANDOFF SAVED',len(checks),'checks')
