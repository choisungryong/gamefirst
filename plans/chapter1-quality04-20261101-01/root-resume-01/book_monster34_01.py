from pathlib import Path
import json,hashlib,shutil,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();d=read(B/'monster34/cost01/source.json');assert all(sha(Path(d['stage'])/n)==h for n,h in d['pins'].items());assert all(sha(R/n)==h for n,h in read(B/'full33/FINAL-SOURCE-FREEZE.json').items())
p=B/'monster34/REVIEW.ko.md';p.write_text(p.read_text(encoding='utf-8')+'\n## cost01 종료\n\nsession24248 양쪽GPU exit0-stderr0/COMPARISON완료. 정상화염16000checkpoint/2초warmup+10초OS시계각1회/실제1920×1080/uncapped/VSyncoff/ignorefocus/profileoff/측정중readback없음.32b→34b p9510.101→10.548ms,p9911.217→12.352,max12.769→13.950,33ms초과0/0,drawmax384→546. 시작16128/16129로1tick차이/끝둘다16729각독립전체core같음. draw추가비용있음/정식focused패키지3회대체금지.34b after1080PNG직접검수,뼈·도끼근접형과기존원거리·돌진형상구분/주인공표식·위험원·이름읽힘. 모든이번Godot종료/같은검사재실행금지. 다음은새walker4방향과사망화면및패키지검수.현재제품33유지/34EXE없음.\n',encoding='utf-8')
p=R/'HANDOFF.md';p.write_text('# 최신 · 해골34b GPU비교·회귀·비용 종료 / 제품33 유지\n\nmonster34/REVIEW.ko.md 최신부분과cost01/COMPARISON.json 읽는다. session24248 terminal양쪽quiet/모든이번Godot종료. source32b→34b p9510.101→10.548ms/p9911.217→12.352/draw384→546/전체core같음/1080새after화면직접검수. mapped03(41423) 새34b300framequiet·전체core같음,regression01 headless16checksquiet. 실패mapped01indent/GPU미시작·mapped02 native material-null571는원시보존/성공승격금지.34b meshbase선행분리로boot+mapped03+costquiet이나내부원인확정금지. 제품33·원freeze·기존EXEs/사용자23복원후·29rev2유지. 현재34게임EXE없음. 다음은해골walker4방향·사망화면/필요시실제패키지후채택.도감v38 연구페이지와비교영상/1080화면추가/실제브라우저미검수(커널경로오류). UI복구질문답대기/그동안품질작업계속.목표active/최종수동·실청취·focused성능/품질미완료.추가툴·Github보류.\n\n---\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
N=B/'full30/book-v38/dist';assert not N.exists();shutil.copytree(B/'full30/book-v37/dist',N);rel=lambda p:os.path.relpath(p,N).replace('\\','/')
t=(N/'candidate33.html').read_text(encoding='utf-8');body='<h1>근접 적34 · 도끼를 든 해골</h1><p class="lead">같은 계열의 몸이 반복되던 무리에서 일반 근접 적을 다른 골격과 저작된 동작으로 구분하는 연구입니다. 현재 제품은33입니다.</p>'
body+=f'<figure><img loading="lazy" src="{rel(B/"monster34/cost01/34b/after.png")}" alt="해골 근접 적과 기존 원거리·돌진 적이 함께 있는 실제1080p 소스 연구 화면"><figcaption>정상 성장 화염 빌드의1080p 화면 · 제품34 실행 파일이나 수동 플레이 검수가 아닙니다.</figcaption></figure>'
body+='<h2>같은 전투의 전후</h2>'
for path,caption in [('monster34/mapped02/32b/normal-060.png','기존 근접 적'),('monster34/mapped03/34b/normal-060.png','해골 근접 적 시안')]:body+=f'<figure><img loading="lazy" src="{rel(B/path)}" alt="{caption}"><figcaption>{caption} · 같은 프레임의 전투 상태를 유지한 소스 비교</figcaption></figure>'
body+='<h2>도끼 공격의 준비와 회복</h2>'
body+=f'<video controls preload="metadata" playsinline style="width:100%;max-width:960px" src="{rel(B/"monster34/mapped03/34b/attack.mp4")}"></video><p>네 역할을 각각 한 방향으로 배치한 무음3초 공격 장면입니다. 원래 판정 시점에 도끼 동작을 맞추는 시안이며, 모든 방향·실제 패키지·수동 플레이 승인은 남았습니다.</p>'
body+='<p>정상120프레임과 공격180프레임의 전투 상태는 기존과 같았습니다. 빙결·정지 자세 유지, 피격 시 하체 보존, 사망 반복 방지와 표시 풀 재사용 검사를 통과했습니다. 10초 단회 비용 비교 p95는10.101→10.548ms,draw 수는384→546으로 추가 비용이 있습니다. 최종 성능 검수와는 구분합니다.</p><p>첫 비교는 관찰기 들여쓰기 오류로 중단됐고, 첫 해골 실행은 렌더러 material-null 오류 때문에 실패로 보존했습니다. 모델을 없애기 전 렌더 메시 연결을 분리한 수정본은 짧은 진단·연속 비교·비용 검사에서 오류 없이 종료했습니다. 기존 실패를 성공으로 바꾸지 않았습니다.</p>'
body+=f'<p><a href="{rel(B/"monster34/REVIEW.ko.md")}">검수 기록과 남은 작업</a> · <a href="{rel(R/"chapter1/art/skeleton_outlaw/v02/ATTRIBUTION.ko.md")}">CC0 KevDev 출처·변환 기록</a> · <a href="candidate33.html">현재 제품33</a></p>'
t=re.sub(r'<title>.*?</title>','<title>근접 적34 · 해골 동작 연구</title>',t);t=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S);(N/'monster34.html').write_text(t,encoding='utf-8')
for name in ['index.html','candidate33.html','monster34.html']:
 p=N/name;s=p.read_text(encoding='utf-8').replace('v37 · 후보33','v38 · 후보33').replace('</nav>','<a href="monster34.html">근접 적34 연구</a></nav>');p.write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='Not run; prior kernel assets path error'),indent=2),encoding='utf-8');print('BOOK38',refs)
