from pathlib import Path
import json,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks={}
checks['root27_freeze']=all(sha(R/n)==h for n,h in read(B/'full27/FINAL-SOURCE-FREEZE.json').items());checks['prior_exes']=all(sha(R/n)==h for n,h in read(B/'full27/ADOPTION.json')['preserved_exes'].items());profile=read(B/'full23/runtime/default-profile-preserved.json');checks['saved_profile3']=all(sha(Path(profile['path'])/n)==h for n,h in profile['pins'].items())
for label in ['profile-control01','profile-after01','normal-film01/control','normal-film01/after']:
 info=read(B/f'actor28/{label}/source.json');checks[label+'_source']=all(sha(Path(info['stage'])/n)==h for n,h in info['pins'].items())
p=B/'actor28/MOVIE-POSTFLIGHT01.json';assert not p.exists();p.write_text(json.dumps(dict(checks=checks,passed=all(checks.values()),scope='Preservation only; failed movie analysis01/02 frame-synchronization assumptions remain failures.'),indent=2));assert all(checks.values())
p=B/'full27/book-v26/BROWSER-REVIEW01.json';assert not p.exists();p.write_text(json.dumps(dict(pages_in_book=37,filesystem_refs=1434,filesystem_missing=0,browser_cases=4,pages_tested=['index.html','actor28-movie.html'],widths=[1440,390],main_each=True,h1_each=1,overflow=0,complete_broken_images=0,video_ready=4,video_error=None,video_durations=[4.083333,4.1],video_dimensions=[1280,720],viewport_reset_called=True,screenshot_reviewed=True,scope='New page and index only; not all37 pages newly browser-tested. Video metadata only, not full playback review.'),indent=2))
note='''# 최신 재개 — 2026-11-04 / Actor28 비용·정상속도 연속영상 / 동기분석실패 보존 / 도감v26

제품27/rootfreeze고정/Actor28미연결. actor28/normal-film01/REVIEW.ko.md 우선읽는다. 이번은구현추가없이채택전필요했던비용·연속영상증거확보로진행. CPU pair session25831 모두terminal:현재27기반정상화염2800→3400tick599표본각1회,Actor25b평균1.871573/최대4.075ms→28평균1.960958/최대4.261ms,추가평균.089386ms.양쪽core같음/224생성112재사용/after44혼합/quiet.실시간formal성능승인아님/processmax차이로성능개선주장금지.

Movie pair session1482/control8444/after28576 모두terminal exit0-stderr0/직접PID없음확인.각새stage/정상화염16000→16241tick/각4sim초/독립전체core같음/after280혼합. GodotMovieMaker60fps의연속AVI+MP4/게임audio보존.과거느린8samplemovie아니며정상재생속도연속offline영상이다. 하지만control245frames4.083333초/after246frames4.1초총한frame차이. analysis01 동프레임수assert실패,analysis02 rawframemd5마지막정지반복제외동수assert도실패.중간파일/키프레임/probe/md5/raw모두보존.게임QA종료후OS150ms오디오정리대기가있으나원인확정못함.임의절단·frame삽입으로맞추지말것.프레임완전동기전후승인아님.다음은frame→coretick명시맵을기록한새캡처와공격windup→release→recover paid방향전후연속검수.원rawRESULT scope의10sim초는helper상속문구오류로이번4sim초길이근거금지.

analysis01의1초/3초전후4PNG직접검수.관찰1초16060tick/3초16181tick·hero좌표두팔같음.전체영상직접재생·자연스러운반동최종품질승인아직. CPU/영상을제품28실제EXE/수동/실시간성능/실청취로확대금지. MOVIE-POSTFLIGHT01 root27freeze/과거EXE/기본23저장3/새4stage source핀모두pass.같은검사중복실행금지.

最新도감full27/book-v26/dist/actor28-movie.html,37HTML/1434refs/missing0. IABbrowser2새탭,index+새영상page×1440/390폭4case만신규브라우저검수(main/h1=1/overflow0/completebroken0).전체37page를새검수했다고말하지말것.2video1280×720/4.083333·4.1秒/ready4/errornull메타데이터확인,viewportreset호출/screenshot직접검수/markDeliverable.전체재생검수아님.이전v25이하보존.제품27수동전체·실청취·최종동일EXE대표3회·공간/공격최종질감남음.목표active/2·3장미착수.

---
'''
p=R/'HANDOFF.md';prior=p.read_text(encoding='utf-8');p.write_text(note+prior,encoding='utf-8');print('MOVIE/CPU POSTFLIGHT',len(checks),'checks; HANDOFF/BOOK26 saved')
