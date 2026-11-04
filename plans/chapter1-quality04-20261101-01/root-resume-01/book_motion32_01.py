from pathlib import Path
import json,hashlib,shutil,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(B/'motion32/mapped02/COMPARISON.json')['passed'];a=read(B/'full31/ADOPTION.json');checks=dict(root31=all(sha(R/n)==h for n,h in read(B/'full31/FINAL-SOURCE-FREEZE.json').items()),old_exes=all(sha(R/n)==h for n,h in a['preserved_exes'].items()),user23restored29=all(sha(Path(n))==h for n,h in a['user_pins'].items()));assert all(checks.values());p=B/'motion32/PRESERVATION01.json';assert not p.exists();p.write_text(json.dumps(checks,indent=2),encoding='utf-8')
p=B/'motion32/REVIEW.ko.md';p.write_text(p.read_text(encoding='utf-8')+'\n## mapped02 종료\n\n세션27268 import/check/32b GPU/encode종료,exit0-stderr0/8checks pass.32b300PNG와기존30c300행의모든frame/tick/coreSHA같음.32b공격20·48 두장직접검수:준비차이증가,walker회복팔벌림차이보임. 정예의준비외곽은달라졌으나실전효과/모든방향/실시간비용/정지·빙결상태검수전최종채택금지. 32b연속영상전체직접재생아님. 원32도보존. root31/이전EXEs/23복원후·29핀재확인pass. 모든이번Godotterminal.\n',encoding='utf-8')
p=R/'HANDOFF.md';p.write_text('# 최신 · 역할 동작32b 비교 종료 / 현재 제품31 유지\n\nmotion32/REVIEW.ko.md와mapped02/COMPARISON.json 읽는다. 세션71701/27268 모두terminal exit0-stderr0/각8checks.32첫안미채택,32b준비1.55배·회복실제길이보완/32b300frame core가보존30c300행과같음. 제품31/sourcefreeze/EXE/기존후보/사용자23복원후·29핀불변.32EXE없음. 다음은32b 모든방향·정지/빙결/풀상태·실전비용·연속시각검수후채택판단. 같은mapped/GPU중복실행금지. 도감v34에미연결연구기록,브라우저미검수(도구커널경로오류지속). 원목표active/Github·추가툴보류.\n\n---\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
N=B/'full30/book-v34/dist';assert not N.exists();shutil.copytree(B/'full30/book-v33/dist',N);rel=lambda p:os.path.relpath(p,N).replace('\\','/')
t=(N/'candidate31.html').read_text(encoding='utf-8');body='<h1>역할 동작32 · 준비와 회복</h1><p class="lead">제품31을 유지하면서 일반 적·정예의 공격 준비 자세를 비교했습니다.</p><p>첫 시안은 회복 변화가 약해 채택하지 않았습니다. 두 번째 안은 근접의 한팔 비틀기, 돌진의 낮은 상체, 원거리의 뒤로 당긴 지팡이, 정예의 양팔 자세를 더 분명하게 합니다. 실제 공격 시점·판정·이동·드롭은 유지합니다.</p>'
for f,c in [('motion32/mapped01/30c/attack-020.png','기존30c 준비 자세'),('motion32/mapped02/32b/attack-020.png','32b 준비 자세'),('motion32/mapped01/30c/attack-048.png','기존30c 타격 후'),('motion32/mapped02/32b/attack-048.png','32b 타격 후')]:body+=f'<figure><img loading="lazy" src="{rel(B/f)}" alt="{c}"><figcaption>{c} · 복사한 공격 장면, 네 역할이 각각 한 방향을 향한 비교 fixture</figcaption></figure>'
body+='<p>정상 전투120프레임과 공격180프레임에서 매 프레임의 전투 상태가 같았습니다. 32b는 기존 baseline 기록을 재사용해 같은 검사를 중복 실행하지 않았습니다. 현재 제품에 연결하지 않았으며, 모든 방향·정지·빙결·실시간 비용 검수가 남았습니다. 무음 영상 생성과 실제 재생·실청취는 구분합니다.</p>'
body+=f'<p><a href="{rel(B/"motion32/REVIEW.ko.md")}">검수 기록과 한계</a> · <a href="{rel(B/"motion32/mapped02/COMPARISON.json")}">비교 원문</a> · <a href="candidate31.html">현재 제품31</a></p>'
t=re.sub(r'<title>.*?</title>','<title>역할 동작32 연구 · 잿빛 회랑</title>',t);t=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S);(N/'motion32.html').write_text(t,encoding='utf-8')
for p in N.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('v33 · 후보31','v34 · 후보31').replace('</nav>','<a href="motion32.html">역할 동작32 연구</a></nav>');p.write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='Not run; prior kernel assets path error'),indent=2),encoding='utf-8');print(checks,refs)
