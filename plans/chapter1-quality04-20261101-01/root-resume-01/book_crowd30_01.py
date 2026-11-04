from pathlib import Path
import json,hashlib,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'crowd30';H=B/'root-resume-01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(O/'equivalence03/RESULT.json');assert a['passed'];checks=read(O/'PRESERVATION01.json')['checks']
for name in ['cost02','equivalence02','equivalence03']:
 d=read(O/name/'source.json');S=Path(d['stage']);checks[name+'_stage_unchanged']=all(sha(S/n)==h for n,h in d['pins'].items())
d=read(B/'full23/runtime/default-profile-preserved.json');checks['user23_preserved']=all(sha(Path(d['path'])/n)==h for n,h in d['pins'].items())
checks['root29_frozen']=all(sha(R/n)==h for n,h in read(B/'full29/FINAL-SOURCE-FREEZE.json').items());assert all(checks.values());(O/'PRESERVATION02.json').write_text(json.dumps(dict(checks=checks),indent=2))
note='''# 군중 체형30 연구 · 제품29 유지

chapter_actors_quality30/30b/30c.gd는 모두 제품 미연결이다. 30은 역할별4가지 몸 전체 비율,30b는 같은4체형의 머리/어깨/팔 비율을 더한다.30c는30b와 동일 표현을 유지하면서 뼈 인덱스와 checkout당 base array를 재사용한다. 원래29의 피격·paid회복방향·그림자·pool224/공유skin1 유지. ID/generation으로 시각변형만 선택,simulation RNG/충돌/공격/획득/성장/새 geometry 없음. 정예와 최종보스 형상 미변경.

compare01/session88103와 compare02/session92224 모두 import/check/GPU exit0-stderr0. 정상냉기2800/12600/19800tick(46.7/210/330sim초) 같은core·camera·light·pose에서 off/on,각6PNG. 모든출력core같음/생성224/skin1. compare01은12600전후2장 직접봤고 차이약해미채택. compare02는6장전부직접검수,목·어깨·팔과몸비율차이로외곽개체반복이조금줄지만같은모델계열한계와밀집중앙중첩은남음. 별도몬스터종을추가한것처럼쓰지않는다. rawpixel차이수는품질점수가아님.

fixture01/session22348 headless11검사quietpass:정상군중12role/variant전부·반복자세누적없음·modal정지·손/지팡이·hit28·원core·풀224복구·키/alias·bonebase초기화·skin1.30b범위.

mapped01/session95266 두팔29/30b 각300PNG 및60fps normal2초/공격fixture3초MP4. 정상16001~16120 모든frame/tick/coreSHA같음/전체정상core복원/quiet/8검사pass. 공격fixture는4역할각한cardinal방향뿐이며모든variant/방향연속영상승인아님. 직접본6장:29예고20/회복70,30b예고20/타격48/회복70/정상60. paid방향과역할윤곽유지확인. 전체MP4직접재생·청취승인아님. 무음offline정상재생속도자료/실시간성능또는수동증거아님.

cost01/session19442 실제source1920×1080/VSyncoff/uncapped/ignorefocus/정상화염2800checkpoint/2초warmup+10초OS시계각1회:29 p50 3.810/p95 5.913/p99 6.814/max35.330ms→30b 5.067/7.572/8.637/35.551ms. cost02/session66459 같은방식새비교:29 3.854/6.080/6.797/34.326→30c 4.815/6.952/7.900/39.797ms.각pair독립core같음/양쪽>33.33각1/drawmax300동일/quiet/각pair끝3528·3529로1tick차이.30c비용추가여전히있음.서로다른pair의차이를정밀개선율로쓰지않는다. 실제focus패키지대표3회나전체후반보증아님.

equivalence01/session2554 정상60step(2800→2860)배우5979개표본의모든bone/modelscale/staff30b=30c/modal/pool같음/6검사quietpass. 확장equivalence02/session84003는그8검사모두true에도ObjectDB종료경고stderr124로실패. stage/result/raw/FAILED-RESULT/FAILURE를그대로보존/동일출력재실행없음. extra control presenter와view를명시해제한새equivalence03/session7176 --verbose는같은8검사·5979normal+8640공격표본전부일치/exit0-stderr0. 3역할×4체형×4cardinal방향48체,180fixtureframe의windup→paid회복→modal→hit→death를비교했다. 결과scope상속문구는60normal만쓰지만attack_comparisons8640와checks가확장범위를명시한다. 이것은30c가30b표현과같다는headless근거이지사망/공격예술품질승인아님. 첫경고의정확한내부누수객체원인은확정하지않는다.

현재모든이번Godot프로세스종료직접확인. 제품29 rootfreeze/모든새stage/사용자23저장3/사용자29최신rev2저장+journal불변(PRESERVATION02).기존후보14~29·실패·도감v29이하보존.30EXE없음. 제품채택전에추가비용대비화면가치판단과실제30c패키지검수가필요하다. 다음은30c의bodyvariation을과장하지않고기존29보존하에채택여부결정/필요시새30패키지와actualGPU검수다. 공간구조깊이와최종수동전체·실청취는여전히남음. 목표active/2·3장미착수.
'''
(O/'REVIEW.ko.md').write_text(note,encoding='utf-8')
old=B/'full29/book-v29/dist';new=B/'full29/book-v30/dist';assert not new.exists();shutil.copytree(old,new);rel=lambda p:os.path.relpath(p,new).replace('\\','/')
for p in new.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('v29 · 후보29','v30 · 후보29').replace('</nav>','<a href="crowd30.html">군중 체형30 연구</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="crowd30.html">군중 체형30 연구 · 아직 제품 미연결</a></p>',1)
 p.write_text(s,encoding='utf-8')
body='<h1>군중 체형30 연구</h1><p class="lead">키와 어깨·머리·팔 비율로 같은 무리의 반복을 덜어내는 시안입니다. 현재 제품은 후보29를 유지합니다.</p><h2>같은 전투에서 비교</h2>'
for f,caption in [('compare02/shots/2800-before.png','이전29 · 같은 정상냉기2800tick'),('compare02/shots/2800-after.png','체형30b · 같은 적과 카메라, 전투규칙'),('compare02/shots/19800-after.png','330초 보스전 · 위험원과 보스 윤곽은 유지')]:body+=f'<figure><img src="{rel(O/f)}" alt="{caption}"><figcaption>{caption}</figcaption></figure>'
body+='<p>역할마다 4가지 체형 비율을 사용합니다. 같은 모델 계열의 한계와 밀집 중앙의 겹침은 남습니다. 새 몬스터 종을 추가한 결과는 아닙니다.</p><h2>공격과 회복</h2>'
for f,caption in [('29/attack.mp4','기존29 · 네 역할의 공격fixture'),('30b/attack.mp4','체형30b · 같은frame/tick/core의 공격fixture')]:body+=f'<figure><video controls preload="metadata" src="{rel(O/"mapped01"/f)}"></video><figcaption>{caption}</figcaption></figure>'
body+='<p>60fps로 인코딩한 무음 3초 offline 자료입니다. 각 역할당 한 방향만 담았습니다. 전체 영상 재생·청취나 수동 검수 완료를 뜻하지 않습니다.</p><h2>표현을 유지하며 비용 줄이기</h2><p>30c는 30b의 같은 변형을 유지하고 반복 조회와 임시 할당을 줄였습니다. 정상 배우5979표본과 3역할×4체형×4방향의 공격·피격·사망8640표본에서 뼈·모델·지팡이 상태가 같았습니다.</p><p>새 10초 source 비교에서 기존29 p95 6.080ms,30c 6.952ms였습니다. 최장39.797ms 지연과 추가 비용은 남습니다. 제품의 대표 성능3회를 대체하지 않습니다.</p><p>확장 검사 첫 실행은 종료 누수 경고로 실패했고 원시 자료를 보존했습니다. 검사 장면을 명시 해제한 새 진단은 오류 없이 종료했습니다. 이 차이를 숨기거나 첫 실행을 성공으로 바꾸지 않습니다.</p>'
body+='<p>'+' · '.join(f'<a href="{rel(O/f)}">{label}</a>' for f,label in [('REVIEW.ko.md','범위와 한계'),('cost02/COMPARISON.json','개발 비용 비교'),('equivalence03/RESULT.json','표현 동등성'),('equivalence02/FAILURE.json','보존한 실패'),('PRESERVATION02.json','보존 감사')])+'</p>'
s=(new/'candidate29.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>군중 체형30 연구 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(new/'crowd30.html').write_text(s,encoding='utf-8')
missing=[];refs=0
for p in new.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
assert not missing
(new.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(new.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),indent=2))
head='# 최신 군중 체형30 연구 · 제품29 유지\n\n먼저 plans/chapter1-quality04-20261101-01/crowd30/REVIEW.ko.md를 읽는다. '+note.split('\n\n',1)[1]+'\n도감v30 생성/40HTML/'+str(refs)+'참조/누락0,브라우저 검수pending.\n\n---\n'
p=R/'HANDOFF.md';p.write_text(head+p.read_text(encoding='utf-8'),encoding='utf-8');print('REVIEW PRESERVATION HANDOFF BOOK30',refs)
