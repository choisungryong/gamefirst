from pathlib import Path
import json,hashlib,shutil,re,os,html
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full18/book-v11/dist';BOOK=B/'full19/book-v12/dist'
assert not BOOK.exists();shutil.copytree(OLD,BOOK)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
build=read(B/'full19/build/build.json');gpu=read(B/'full19/runtime/gpu-cold01/RESULT.json');assert all(gpu['same10_as_packaged16'].values())
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.group(1),m.group(2)
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v11','제작 도감 v12').replace('후보18 / 이전 항목은 본문 번호 유지','후보19 / 이전 항목은 본문 번호 유지')
 s=s.replace('</nav>','<a href="motion19.html">무리의 동작19</a></nav>');p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate18.html')
for name,source in {
 'motion19-field.png':B/'full19/runtime/gpu-cold01/captures/run-001-frame-090.png',
 'motion19-death.png':B/'full19/runtime/gpu-cold01/captures/victory-after-0.35.png',
 'motion19-reward.png':B/'full19/runtime/gpu-cold01/captures/victory-after-1.60.png',
 'motion19-elite.png':B/'motion19/release01/attack-shots/elite-recover-fan.png',
 'motion19-walker.png':B/'motion19/fixture02/shots/walker-paid-release.png',
 'motion19-crowd.png':B/'motion19/crowd02/rig19.png'}.items():shutil.copy2(source,BOOK/'scenes'/name)
shell=(BOOK/'candidate18.html').read_text(encoding='utf-8')
def fig(name,caption):return '<figure><img loading="lazy" src="scenes/'+name+'" alt="'+html.escape(caption)+'"><figcaption>'+caption+'</figcaption></figure>'
def page(name,title,body):
 s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell)
 s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S).replace(' aria-current="page"','')
 s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1);(BOOK/(name+'.html')).write_text(s,encoding='utf-8')
page('index','무리가 움직이는 회랑',
 '<p class="lead">일반 적과 중간 정예가 실제 골격으로 걷고, 준비하고, 공격하고, 쓰러집니다.</p>'
 +fig('motion19-field.png','후보19 실제 EXE의 정상 냉기 전체 전투 중1분29초. 일반 적의 몸체 방향·밝은 얼굴과 냉기 사체 감소를 실제 화면으로 검수했습니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">후보19 실행 파일</a><a href="motion19.html">동작·검수 화면</a><a href="candidate18.html">이전18 표지</a></div>'
 +'<p>전체 냉기 전투는6분37.7초·3451처치·파쇄840회로 완료했습니다. 기본 생명력과 실제 드롭·성장을 사용했고, 기존판과 게임 상태10개가 같습니다. 기존 영웅·최종 보스·원거리·돌진 표현은 그대로입니다.</p>'
 +'<p class="note">첫 장 품질은 진행 중입니다. 원거리·돌진 동작의 일관성, 공간 구성, 장비 발견·마무리 연출, 수동·음향·저장UI·최종 성능 검수가 남았습니다. 기술 검사 통과를 완성으로 보지 않습니다.</p>'
 +'<p>WASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.19는 별도 저장 경로를 쓰며 기존 후보와 저장을 보존합니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('motion19','준비에서 실제 공격까지',
 '<p class="lead">고정된 네 장의 이미지에 기대던 일반·중간 정예를, 실제 전투 상태와 연결한73골격 동작으로 바꿨습니다.</p>'
 +'<h2>방향과 역할을 구분</h2>'+fig('motion19-elite.png','정상 획득 빌드를 재구성한5초 연구 GPU. 중간 정예의 실제 fan release tick6521/clip .157초입니다. 일반과 다른 크기·적갈색 몸체·어깨를 사용합니다. 최종 보스는 기존 경로를 유지합니다.')
 +fig('motion19-walker.png','복사한 일반 적 한 마리의 근접 공격 fixture. 준비/마지막6틱/실제 release/빙결·사체·가림·reset16검사를 확인했으며, 정상 전체 플레이 장면으로 쓰지 않습니다.')
 +'<h2>무리가 많을 때도 비용을 줄이기</h2>'+fig('motion19-crowd.png','합성180마리 부하. 정상 전투가 이 배열로 모였다는 뜻은 아닙니다. 몸체·얼굴을 한 표면으로 합치고 일반 적의 그림자를 기존 sprite 설정과 맞췄습니다.')
 +'<p>같은 합성 조건에서 최초 골격안의 draw1187/평균17.49ms를467/14.95ms로 줄였습니다. 원본 정점·UV·bone/weight는 유지합니다. 패키지의 MSAA2·실전 전체·최종3회 성능과는 별도입니다.</p>'
 +'<h2>실제 전체 전투와 보상</h2><div class="columns">'+fig('motion19-death.png','실제19 전체 냉기 승리후.35초. 보스 죽음 진행을 세계에서 먼저 보여주고 기존 사체 제거를 유지합니다. 주변 생존 적과 투사체가 멈춰 남는 마무리는 추가 개선 대상입니다.')+fig('motion19-reward.png','같은 실제 승리후1.60초. 실제 지급된 겨울의 심장과 능력 설명입니다. 사망/보상 카드는 기존17 경로이며19 신규 연출이라고 하지 않습니다.')+'</div>'
 +'<p>전체397.7초/23862tick/3451처치/Lv12/파쇄840/냉기 처치 원인823. 실제16과10게임 상태 동일, exit0/stderr0/27PNG입니다. 스크린샷은 전부1920×1080입니다.</p>'
 +'<p class="note">성능 관찰의 engine delta와 캐시된 CPU monitor를 최종 성능으로 승인하지 않았습니다. 종료 콜백의 texture 크기와 PNG 크기 차이도 남아 있습니다. <a href="'+rel(B/'full19/runtime/gpu-cold01/REVIEW.ko.md')+'">원시값과 한계 검토</a></p>'
 +'<p><a href="'+rel(B/'full19/STATUS.ko.md')+'">상태·남은 작업</a> · <a href="'+rel(B/'full19/independent-audit01/RESULT.json')+'">23개 출처·보존 감사</a> · <a href="'+rel(B/'motion19/REVIEW.ko.md')+'">채택 제외 시안과 연구 기록</a></p>')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,ref])
  if not (p.parent/ref.split('#')[0]).resolve().is_file():missing.append([p.name,ref])
report={'pages':len(list(BOOK.glob('*.html'))),'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p) for p in BOOK.rglob('*') if p.is_file()},'scope':'Actual candidate19 full GPU and separately labeled research fixtures; browser QA pending.'}
(BOOK.parent/'BUILD.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing;print(BOOK,flush=True)
