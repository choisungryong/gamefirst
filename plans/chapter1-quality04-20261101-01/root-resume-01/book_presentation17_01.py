from pathlib import Path
import json,hashlib,shutil,re,os,html
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17';OLD=B/'full16/book-v08/dist';BOOK=OUT/'book-v09/dist';assert not BOOK.exists()
build=json.loads((OUT/'build/build.json').read_text(encoding='utf-8'));assert (OUT/'STATUS.ko.md').exists();shutil.copytree(OLD,BOOK)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.group(1),m.group(2)
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v08','제작 도감 v09').replace('후보16 / 이전 항목은 본문 번호 유지','후보17 / 이전 항목은 본문 번호 유지')
 s=s.replace('</nav>','<a href="experience17.html">전리품·리듬17</a></nav>');p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate16.html')
assets={
 'experience17-gear.png':B/'presentation17/review04/after17-ending-shots/equipment-unique.png',
 'experience17-reward.png':B/'presentation17/review04/after17-ending-shots/ending-2.4.png',
 'experience17-death.png':B/'presentation17/review04/after17-ending-shots/ending-1.0.png',
 'experience17-field.png':B/'presentation17/review04/after17-combat-shots/combat-2.0.png',
 'candidate16-packaged-victory.png':B/'full16/runtime/gpu-cold01/captures/state-0013-run-001-victory.png'}
for n,p in assets.items():shutil.copy2(p,BOOK/'scenes'/n)
shell=(BOOK/'candidate16.html').read_text(encoding='utf-8')
def fig(n,caption):return '<figure><img loading="lazy" src="scenes/'+n+'" alt="'+html.escape(caption)+'"><figcaption>'+caption+'</figcaption></figure>'
def page(name,title,body):
 s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell)
 s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S).replace(' aria-current="page"','')
 s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1);(BOOK/(name+'.html')).write_text(s,encoding='utf-8')
page('index','전리품을 읽고, 승리의 순간을 보다',
 '<p class="lead">같은 냉기 전투 위에서 장비 선택과 보스 보상의 흐름을 다듬습니다.</p>'
 +fig('experience17-reward.png','후보17 표현 연구: 정상 정책으로 실제 획득한 겨울의 심장을 보상창에서 펼칩니다. 보스 사망 동작을1.3초 보여준 뒤 전환합니다. near-victory core 재구성 후 짧은GPU 검수이며 전체 실시간 증거가 아닙니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">후보17 실행 파일</a><a href="experience17.html">장비·동작·공간의 변경</a><a href="candidate16.html">이전 후보16 표지</a></div>'
 +'<p class="note">첫 장의 최종 품질은 진행 중입니다. 수동 한 판·실제 음향 청취·최종1080p3회 성능·네이티브 저장UI 검수는 남아 있습니다. 현재 실행 상태는 <a href="'+rel(OUT/'STATUS.ko.md')+'">후보17 상태</a>를 따릅니다.</p>'
 +'<p>WASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지. 후보14·16 실행본과 저장을 보존하며17은 별도 저장 경로를 사용합니다.</p>'
 +'<p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('experience17','장비 선택에서 보스 보상까지',
 '<p class="lead">장비를 클릭할 때 목록이 튀지 않게 하고, 고유 효과와 승리 보상을 읽을 시간을 줍니다.</p>'
 +fig('experience17-gear.png','실제 획득34개 장비의 목록. UID 선택 전후 스크롤650 유지, 슬롯 문양·희귀도 색·겨울의 심장 고유 효과를 표시합니다. 재구성된 정상 빌드의 GPU 검수이며 지급 장비가 아닙니다.')
 +'<h2>사망 동작 뒤에 펼치는 보상</h2><div class="columns">'+fig('experience17-death.png','보스 사망 뒤 첫 구간은 세계를 가리지 않습니다. 기존73골격 사망 동작과1.125초 클립은 그대로입니다.')+fig('experience17-reward.png','1.3초 뒤 실제 보상UID의 이름·슬롯 문양·고유 설명을 보여줍니다. 드롭/저장/장비 수치를 바꾸지 않았습니다.')+'</div>'
 +'<h2>동작과 공간의 작은 보완</h2>'+fig('experience17-field.png','일반·중간 정예의 이동 프레임 위상을ID별로 분산하고 실제 예고/돌진 상태에 작은 기울기를 연결했습니다. 가장자리에는 기존 돌 질감의 입체 기단/짧은 기둥을6개배치로 그립니다. 코어 좌표·충돌은 유지합니다.')
 +'<p>기존4프레임 스프라이트의 보완입니다. 새 골격·방향별 공격 아트가 완성된 것은 아닙니다. 공간 전체의 깊이와 적 실루엣 구분은 계속 검수합니다.</p>'
 +'<h2>성공과 실패를 함께 보존</h2><p>review04에서 전투/보스 구간 전후 시작·끝 전체코어 동일, 스크롤 유지·고유설명·사망전환4검사와 GPU quiet를 확인했습니다. review01의잘못된보상필드, review02의스크롤실패/회색블록, review03의석재면표현실패도 보존했습니다. review04의baseline은 성공한review03 before16을 재사용해 동일 검사를 불필요하게 반복하지 않았습니다.</p>'
 +'<p><a href="'+rel(B/'presentation17/review04/RESULT.json')+'">짧은GPU 검수</a> · <a href="'+rel(OUT/'STATUS.ko.md')+'">현재 후보17 상태</a></p>')
p=BOOK/'cold16.html';s=p.read_text(encoding='utf-8');s=s.replace('<h2>검증 범위와 남은 품질</h2>','<h2>실제 후보16 패키지의 전체GPU</h2>'+fig('candidate16-packaged-victory.png','후보16 실제 패키지 GPU 정상 자동 정책6분37.7초/3451처치/Lv12 첫승리. 종료0/stderr0,headless10상태동일. 이번 observer통계는epoch-1/파쇄1로무효이며 source16의840회와구분합니다.')+'<p>기존GPU는이미종료됐고중복실행하지않았습니다. observer실패는 <a href="'+rel(B/'full16/runtime/gpu-cold01-review/RESULT.json')+'">원시로그검토</a>에분리했습니다.</p><h2>검증 범위와 남은 품질</h2>');p.write_text(s,encoding='utf-8')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,ref])
  if not (p.parent/ref.split('#')[0]).resolve().is_file():missing.append([p.name,ref])
report={'pages':len(list(BOOK.glob('*.html'))),'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p) for p in BOOK.rglob('*') if p.is_file()},'scope':'Actual16GPU/observer failure and17 presentation research labelled separately. Browser QA pending.'}
(BOOK.parent/'BUILD.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing;print(str(BOOK),flush=True)
