from pathlib import Path
import json,hashlib,shutil,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=read(B/'full32/ADOPTION.json');checks=dict(root32=all(sha(R/n)==h for n,h in read(B/'full32/FINAL-SOURCE-FREEZE.json').items()),previous_exes=all(sha(R/n)==h for n,h in a['preserved_exes'].items()),user23restored29=all(sha(Path(n))==h for n,h in a['user_pins'].items()))
for name in ['compare01','cost01']:
 d=read(B/'flame33'/name/'source.json');S=Path(d['stage']);checks[name+'_immutable']=all(sha(S/n)==h for n,h in d['pins'].items())
assert all(checks.values());p=B/'flame33/PRESERVATION01.json';assert not p.exists();p.write_text(json.dumps(checks,indent=2),encoding='utf-8')
p=B/'flame33/REVIEW.ko.md';assert not p.exists();p.write_text('''# 화염 몸가림33 연구 · 제품32 유지

chapter_elements_quality33.gd는FX26을상속하고기존세로불꽃만x/z.85,y.52·중심높이.52배로낮춘다. flame_bloom_quality33.gdshader는ALPHA잔연기와늦은불꽃을줄인다. 투사체·실제명중파동·피해/타격시점·불꽃발생수·성장/드롭은유지한다. 아직제품미연결/33EXE없음.

compare01/session97713 import/check/FX26/FX33 GPU모두exit0-stderr0. 정상화염획득6077tick체크포인트→6197tick,동일121개sync/전체corehash같음/각독립fullcore같음/불꽃수같음/높이중심.52배확인/root32freeze불변. 각6PNG(0·20·37·49·70·110frame),직접본것은20·37·49의전후6장이다. 원거리적의머리/팔가림이줄고화염투사체·바닥명중열기유지. 나머지6장아직직접검수아님.121개는sync샘플이며121GPU연속프레임영상이아니다. 기술승인으로전체시각품질완성주장금지.

cost01/session53496 source32 Actor32b/FX26 vs33,정상화염16000tick→원livecontroller/2초warmup+10초OS시계. p9510.548→10.846ms,p9912.430→12.416,max17.994→14.434,33ms초과0/0,draw394동일. 각독립전체core같음/끝16730tick동일. 실제1920×1080/무제한FPS/VSyncoff/ignorefocus/profileoff/측정중readback없음. 순차단회개발측정으로정식focused패키지최종3회대체금지. 모든이번GPU종료/중복실행금지.

chapter_elements_quality33b.gd는33에드롭등급위계를더하는미검수초안이다. 일반빛기둥.35m/마법.85/희귀1.5/고유1.9,등급별색/희귀+고유작은바닥halo. 생성·획득규칙은변경하지않는다. 원코어일반roll은common/magic/rare이고unique는보상경로이므로고유바닥시안을실제자연드롭으로주장하지말것. 다음은등급표시fixture및정상획득드롭·전체state/수명/이름가독성·비용검수후33/33b제품채택판단. 제품32/이전후보/사용자저장은PRESERVATION01핀보존. 추가툴·Github보류/목표active.
''',encoding='utf-8')
p=R/'HANDOFF.md';p.write_text('# 최신 · 화염33 비교·비용 종료 / 드롭33b 초안 미검수\n\nflame33/REVIEW.ko.md 먼저읽는다. 제품32와rootfreeze·EXE·이전후보·사용자23복원후/29rev2핀그대로. compare01/session97713/cost01/session53496 모두terminal exit0-stderr0. FX33은세로불꽃높이.52/잔연기낮춰원거리적상체가림감소;121sync core같음/불꽃수유지/6PNG직접검수. 후반화염p9510.548→10.846ms/draw394동일/전투state같음. 아직제품채택·33EXE없음. chapter_elements_quality33b.gd 드롭등급색·높이/희귀작은halo 초안작성했으나검사미시작. 다음은33b fixture/정상실제드롭/수명·가독성·비용확인후화염+드롭함께채택판단. 고유바닥색은지원시안일뿐자연unique드롭발생주장금지. 도감v36에연구기록. UI도구커널경로오류/최종수동·실청취·같은제품전체/focused성능미완료. 목표active/추가툴·Github보류.\n\n---\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
N=B/'full30/book-v36/dist';assert not N.exists();shutil.copytree(B/'full30/book-v35/dist',N);rel=lambda p:os.path.relpath(p,N).replace('\\','/')
t=(N/'candidate32.html').read_text(encoding='utf-8');body='<h1>화염33 · 불꽃 뒤의 적이 보이도록</h1><p class="lead">세로 불꽃을 낮춰 상체와 머리를 덜 가리는 시안입니다. 현재 제품은32를 유지합니다.</p>'
for variant,caption in [('26','기존FX26 · 상체를 덮는 세로 불꽃'),('33','FX33 시안 · 발밑의 열기와 투사체는 유지')]:body+=f'<figure><img loading="lazy" src="{rel(B/f"flame33/compare01/{variant}/frame-037.png")}" alt="{caption}"><figcaption>{caption} · 같은 정상 화염 획득 상태의 소스 전후 비교</figcaption></figure>'
body+='<p>같은121시점의전투상태와불꽃수는동일했습니다. 직접검수한전후6장에서원거리적의상체와팔이더구분됩니다. 후반화염10초개발비용p95는10.548→10.846ms였습니다. 정식패키지성능승인이나수동전투검수는아닙니다.</p><p>일반드롭은은은하게,마법·희귀장비는색과빛높이로구분하는다음시안은작성중입니다. 아직게임에채택하지않았고고유장비의자연바닥드롭을추가하지않았습니다.</p>'
body+=f'<p><a href="{rel(B/"flame33/REVIEW.ko.md")}">연구·한계·다음검수</a> · <a href="{rel(B/"flame33/cost01/COMPARISON.json")}">비용원문</a> · <a href="candidate32.html">현재제품32</a></p>'
t=re.sub(r'<title>.*?</title>','<title>화염33 · 가림 감소 연구</title>',t);t=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S);(N/'flame33.html').write_text(t,encoding='utf-8')
for p in N.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('v35 · 후보32','v36 · 후보32').replace('</nav>','<a href="flame33.html">화염33 가림 연구</a></nav>');p.write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='Not run: prior kernel assets path error'),indent=2),encoding='utf-8');print(checks,refs)
