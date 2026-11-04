from pathlib import Path
import json,hashlib,shutil,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full32';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=read(O/'ADOPTION.json');S=Path(read(O/'build/closure.json')['stage']);checks=dict(root32=all(sha(R/n)==h for n,h in read(O/'FINAL-SOURCE-FREEZE.json').items()),stage32=all(sha(S/n)==h for n,h in read(O/'build/staging-manifest.json').items()),previous_exes=all(sha(R/n)==h for n,h in a['preserved_exes'].items()),user23restored29=all(sha(Path(n))==h for n,h in a['user_pins'].items()));assert all(checks.values());p=O/'PRESERVATION01.json';assert not p.exists();p.write_text(json.dumps(checks,indent=2),encoding='utf-8')
note='''# 후보32 현황 · 2026-11-05

제품은 Core16/World31d/Actor32b/HUD27/Input21/FX26. 일반 적·중간 정예의 역할별 상체 준비와 회복 동작을 추가했다. 공격의 실제 시점·판정·방향·성장·드롭은 유지한다. EXE SHA 8bf1dd10436b84b04b7108e23940d9d271f245e23997834e8b727981cdb4b10e /130082400bytes/runtime132-stage134-PCK241. package세션23184 exit0/import-export-PCK-30sim초headless-releasebehavior통과.

- mapped01/02 정상120+공격180frame 비교에서 전체frame/tick/corehash동일.32첫안회복이약해미채택/원시와소스보존.32b채택.
- directions01/session93698 headless·GPU exit0-stderr0,16검사pass:4역할×4방향 mid-windup/mid-recover에서상체만변함/하체동일/20회반복누적없음/지팡이손추적/정지·빙결자세유지/전체core복원/풀224유지. 전후4PNG전부직접검수. 모든역할4방향연속전체영상승인은아님.
- cost01/session80559 source30c/32b순차각2초warmup+10초OS시계/후반정상냉기19800체크포인트. p95 7.357→7.831ms,p99 8.395→8.899,max11.647→12.612,33ms초과0/0,draw333동일.실제1920×1080/무제한FPS/VSyncoff/ignorefocus/profileoff/측정중캡처없음.각독립전체core같음.정식focused최종3회아님.
- 실제EXE elite01/session59752 check/GPU exit0-stderr0. 주입없이정상화염성장에서처음만난비최종정예준비6077tick부터원livecontroller6377tick까지300tick.실제공격발동193pose표본/독립전체core동일/profileoff. windup/release/recover/end 4PNG직접검수. 준비와회복차이가읽히고위험원·주인공표식유지. 타격순간화염plume이몸일부를가리는가독성한계남음.

이전31전체GPU완주는31증거그대로이며32전체완주로승격하지않는다.32최종수동전체·실청취·최종focused1080p성능미완료.브라우저/WindowsUI도구커널경로오류로새기본입력/실제브라우저검수미실행. 추가파이프라인·GitHub보류. 모든이번Godot종료/기존검사중복실행금지. 기존후보및사용자23복원후/29rev2사본·핀보존확인(PRESERVATION01).

다음실질품질작업은화염타격연출의몸가림감소와장비발견·보스보상의시각강조. 같은제품으로남은실제전체·성능·입력·청취검수필요. 최종목표active/2·3장미착수.
'''
p=O/'STATUS.ko.md';assert not p.exists();p.write_text(note,encoding='utf-8')
p=B/'motion32/REVIEW.ko.md';p.write_text(p.read_text(encoding='utf-8')+'\n## 방향·비용·제품32 채택\n\nfull32/STATUS.ko.md 참조. directions01 headless/GPU 16검사·4PNG직접검수;cost01 후반p957.357→7.831ms/draw333동일/전체core같음. 제품32생성후실제정예6077→6377tick/4PNG/quiet·원core같음.32b는기술적호환성과준비·회복읽힘을근거로채택했으나화염타격가림·최종품질/수동/실청취/최종성능남음. 이전32약한안/실패·증거미삭제.\n',encoding='utf-8')
p=R/'HANDOFF.md';p.write_text('# 최신 · 후보32 패키지·실제 정예 검수 종료\n\nfull32/STATUS.ko.md 먼저읽는다. 제품32 EXE SHA8bf1dd10436b84b04b7108e23940d9d271f245e23997834e8b727981cdb4b10e. Core16/World31d/Actor32b/HUD27/Input21/FX26/runtime132-stage134-PCK241. package23184/directions93698/cost80559/actualelite59752 모두terminal exit0-stderr0. 실제정상획득첫정예6077→6377tick/독립전체core같음/4PNG직접검수. directions4역할×4방향16검사pass/4PNG전부검수. 비용p957.357→7.831ms. 원31전체승리는31범위그대로/32전체아님. 기존EXEs·사용자23복원후/29rev2·source/stage32핀보존. 다음은화염명중plume의몸가림감소·장비/보스보상의시각강조및같은제품최종전체/수동/청취/focused성능. 브라우저·WindowsUI커널경로오류유지/추가툴·Github보류/목표active. 같은완료검사중복실행금지.\n\n---\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
N=B/'full30/book-v35/dist';assert not N.exists();shutil.copytree(B/'full30/book-v34/dist',N);rel=lambda p:os.path.relpath(p,N).replace('\\','/')
t=(N/'candidate31.html').read_text(encoding='utf-8');body='<h1>후보32 · 공격을 준비하고 돌아오는 몸</h1><p class="lead">일반 적과 중간 정예의 준비·회복 자세를 역할별로 구분했습니다.</p><p>근접은 한팔을 들어 비틀고, 돌진은 상체를 낮추며, 원거리는 지팡이를 뒤로 당기고, 정예는 양팔을 크게 씁니다. 기존 공격 판정과 실제 시점·성장·드롭은 유지합니다.</p>'
for f,c in [('full32/runtime/elite01/proof/windup.png','실제 정예 · 공격 준비'),('full32/runtime/elite01/proof/release.png','실제 정예 · 공격 발동'),('full32/runtime/elite01/proof/recover.png','실제 정예 · 공격 후 회복')]:body+=f'<figure><img loading="lazy" src="{rel(B/f)}" alt="{c}"><figcaption>{c} · 정상 화염 성장으로 만난 첫 정예, 후보32 실제 실행 파일</figcaption></figure>'
body+='<h2>읽히는 변화와 남은 가림</h2><p>공격 준비와 타격 후의 자세가 달라졌습니다. 타격 순간에는 화염 연출이 몸 일부와 겹쳐 가독성을 더 개선해야 합니다. 네 역할의 네 방향 비교에서 하체·정지·빙결 자세와 지팡이 손 위치를 유지했습니다.</p><p>실제 정예 전투6077→6377tick의 전체 전투 상태가 독립 재구성과 같았습니다. 후반10초 소스 비용 비교 p95는7.357→7.831ms였습니다. 단회 개발 측정이며 정식 최종 성능 승인은 아닙니다.</p><p>이전 후보31의6분38초 전체 완주는31의 기록입니다. 후보32의 전체 수동 플레이·실청취·최종 성능 검수는 남아 있습니다. 현재 도감도 브라우저 도구 초기화 오류로 새 화면 검수를 하지 못했습니다.</p>'
body+='<p>'+' · '.join(f'<a href="{rel(p)}">{l}</a>' for p,l in [(Path(read(O/'build/build.json')['exe']),'후보32 실행 파일'),(O/'STATUS.ko.md','제품32 상태'),(O/'runtime/elite01/proof/RESULT.json','실제 정예 검수'),(B/'motion32/directions01/gpu/RESULT.json','방향·정지·빙결 검사')])+' · <a href="motion32.html">연구 시안 보존</a> · <a href="candidate31.html">이전 후보31</a></p>'
t=re.sub(r'<title>.*?</title>','<title>후보32 · 공격 준비와 회복</title>',t);t=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S)
for name in ['index.html','candidate32.html']:(N/name).write_text(t,encoding='utf-8')
for p in N.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('v34 · 후보31','v35 · 후보32').replace('</nav>','<a href="candidate32.html">후보32 · 준비와 회복</a></nav>');p.write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='Not run: kernel assets path error remains'),indent=2),encoding='utf-8');print(checks,refs)
