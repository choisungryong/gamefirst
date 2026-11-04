from pathlib import Path
import json,hashlib,shutil,re,os,html
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full19/book-v12/dist';BOOK=B/'full20/book-v13/dist'
assert not BOOK.exists();shutil.copytree(OLD,BOOK)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
build=read(B/'full20/build/build.json');clean=read(B/'full20/runtime/native-clean01/RESULT.json');assert all(clean['same10_as_full19'].values())
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.group(1),m.group(2)
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v12','제작 도감 v13').replace('후보19 / 이전 항목은 본문 번호 유지','후보20 / 이전 항목은 본문 번호 유지')
 s=s.replace('</nav>','<a href="experience20.html">발견·마무리20</a></nav>');p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate19.html')
for name,source in {
 'experience20-discovery.png':B/'discovery20/replay04/shots/item-003.png',
 'experience20-death.png':B/'full20/runtime/native-clean01/captures/native20-ending-1.20.png',
 'experience20-reward.png':B/'full20/runtime/native-clean01/captures/native20-ending-1.60.png',
 'experience20-reload.png':B/'full20/runtime/native-save-reload02/captures/state-0001-run-000-menu.png',
 'experience20-gear.png':B/'full20/runtime/native-save-reload02/captures/state-0002-run-001-inventory.png'}.items():shutil.copy2(source,BOOK/'scenes'/name)
shell=(BOOK/'candidate19.html').read_text(encoding='utf-8')
def fig(name,caption):return '<figure><img loading="lazy" src="scenes/'+name+'" alt="'+html.escape(caption)+'"><figcaption>'+caption+'</figcaption></figure>'
def page(name,title,body):
 s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell)
 s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S).replace(' aria-current="page"','')
 s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1);(BOOK/(name+'.html')).write_text(s,encoding='utf-8')
page('index','전리품이 다음 전투로 이어지도록',
 '<p class="lead">희귀 장비를 발견하고, 보스를 쓰러뜨리고, 저장한 장비로 다시 회랑에 들어갑니다.</p>'
 +fig('experience20-discovery.png','발견20 정상45초 소스 GPU의 실제 희귀 장비 획득. 짧은 상단 카드로 이름·부위를 알리고 I 비교·장착으로 연결합니다. 패키지 전체 플레이 사진은 아닙니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">개발 후보20 실행 파일</a><a href="experience20.html">사망·보상·재시작 화면</a><a href="candidate19.html">이전19 표지</a></div>'
 +'<p>첫 마법 장비와 부위별 첫 희귀 장비를 실제 획득 정보로 알립니다. 보스가 넘어진 뒤 남은 전투 표현이 정리되고 전리품은 남습니다. 정상 획득 장비의 저장·보관함 선택·재시작·새 도전 반영을 실제 UI로 확인했습니다.</p>'
 +'<p class="note">첫 장 품질은 계속 개선 중입니다. 원거리·돌진 동작과 공간, 수동 한 판·실청취·기본 저장 경로·최종1080p3회 검수가 남았습니다. 기존 QA 경고와 새 quiet 검수는 구분합니다.</p>'
 +'<p>WASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.20은 별도 저장 namespace이며 기존 실행과 저장을 보존합니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('experience20','발견, 쓰러짐, 다음 도전',
 '<p class="lead">짧은 발견 카드는 전투를 가리지 않고, 마지막 전투는 전리품을 읽을 수 있는 장면으로 이어집니다.</p>'
 +'<h2>실제 희귀 장비를 발견하다</h2>'+fig('experience20-discovery.png','실제 소유 UID3의 이름·희귀도·부위를 확인했습니다. 카드512×122logical/상단40% 조건, 독립 정상정책 전체core동일. 앞선 긴 카드 실패01~03도 보존했습니다.')
 +'<h2>보스가 쓰러지고 세계가 정리되다</h2><div class="columns">'+fig('experience20-death.png','실제 패키지20의 정상 획득 빌드를 보스 직전까지 재구성한 ending replay. 실제 승리후1.20초, 보스가 넘어지고 주변 적·사체·공격 잔상은 사라지며 전리품은 남습니다. 전체 수동 플레이가 아닙니다.')+fig('experience20-reward.png','같은 실제20 EXE의 승리후1.60초. 기존 실제 보상인 겨울의 심장을 보여줍니다. 지급·전투 규칙을 바꾸지 않았고19와10게임 상태가 같습니다.')+'</div>'
 +'<p>source ending02는 정상 참조 전체core동일/17edge/quiet. 실제 package native-clean01은 저장34/완료1/revision1·10상태 동일·exit0/stderr0입니다. 외부 QA 경로를 검증된 절대 물리 경로에 연결했으며 기본 user:// 저장 경로 검사와 구분합니다.</p>'
 +'<h2>선택한 장비를 다시 가져오다</h2>'+fig('experience20-reload.png','실제 EXE를 재시작해 보관함34개가 남아 있는 메뉴를 확인했습니다. UI로 반지를 선택해 다음 도전 장비로 저장했고, 두 번째 재시작에서도 선택이 유지됐습니다.')
 +fig('experience20-gear.png','두 번째 재시작에서 실제 냉기 시작 버튼→I를 눌렀습니다. 수확의 유리 반지가 실제 장비로 들어오고 최대HP110/110,피해+12%/HP-10/회수+.7m가 반영됩니다. 짧은 네이티브 입력 검사이며 수동 전체가 아닙니다.')
 +'<p class="note">첫 native-save01은 잘못된 자동 캡처 경로와 QA res:// 폴더 생성 실패가 있었고, reload01/02도 QA 디렉터리 경고로 helper는 실패했습니다. 실제 UI·파일의 저장 지속성 증거는 별도로 보존했습니다. 새 native-clean01은 새 QA 파일로 경고 없이 저장과 패키지 화면을 확인했으며 기존 실패를 덮어쓰지 않았습니다.</p>'
 +'<p><a href="'+rel(B/'full20/STATUS.ko.md')+'">상태와 남은 검수</a> · <a href="'+rel(B/'full20/independent-audit01/RESULT.json')+'">26개 출처·보존 감사</a> · <a href="'+rel(B/'full20/runtime/native-clean01/RESULT.json')+'">실제 패키지 quiet 검수</a></p>')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,ref])
  if not (p.parent/ref.split('#')[0]).resolve().is_file():missing.append([p.name,ref])
report={'pages':len(list(BOOK.glob('*.html'))),'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p) for p in BOOK.rglob('*') if p.is_file()},'scope':'Actual package20 ending/QA save and native UI, source discovery separately labeled; browser QA pending.'}
(BOOK.parent/'BUILD.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing;print(BOOK,flush=True)
