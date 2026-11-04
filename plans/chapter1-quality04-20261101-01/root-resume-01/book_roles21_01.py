from pathlib import Path
import json,hashlib,shutil,re,os,html
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full20/book-v13/dist';BOOK=B/'full21/book-v14/dist';assert not BOOK.exists();shutil.copytree(OLD,BOOK)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
build=read(B/'full21/build/build.json');native=read(B/'full21/runtime/native-input01/RESULT.json');assert len(native['records'])==2
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.group(1),m.group(2)
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v13','제작 도감 v14').replace('후보20 / 이전 항목은 본문 번호 유지','후보21 / 이전 항목은 본문 번호 유지')
 s=s.replace('</nav>','<a href="roles21.html">조작·역할21</a></nav>');p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate20.html')
for name,source in {'roles21-zone1.png':B/'full21/runtime/native-input01/captures/zone1-click1.png','roles21-zone2.png':B/'full21/runtime/native-input01/captures/zone2-click2.png','roles21-crowd.png':B/'roles21/crowd02/roles21.png'}.items():shutil.copy2(source,BOOK/'scenes'/name)
shell=(BOOK/'candidate20.html').read_text(encoding='utf-8')
def fig(name,caption):return '<figure><img loading="lazy" src="scenes/'+name+'" alt="'+html.escape(caption)+'"><figcaption>'+caption+'</figcaption></figure>'
def page(name,title,body):
 s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell);s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S).replace(' aria-current="page"','');s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1);(BOOK/(name+'.html')).write_text(s,encoding='utf-8')
page('index','세 구역 어디서나 같은 조작',
 '<p class="lead">후반 회랑에서도 클릭한 곳으로 이동하고, 원거리와 돌진 적은 서로 다른 실루엣과 실제 동작으로 다가옵니다.</p>'
 +fig('roles21-zone2.png','실제 후보21 EXE의 세 번째 구역 클릭 검수. 정상 획득 빌드를 재구성한 장면이며 수동 전체 플레이가 아닙니다. 실제 클릭 목표와 영웅의 이동 방향을 확인했습니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">개발 후보21 실행 파일</a><a href="roles21.html">조작과 역할 검수</a><a href="candidate20.html">이전20 표지</a></div>'
 +'<p>첫 구역에만 맞춰져 있던 좌클릭 목표 제한을 열린 구역·통로 전체에 맞췄습니다. 원거리 적의 긴 지팡이와 돌진 적의 낮고 넓은 몸체를 실제 발사·돌진·회복 상태에 연결했습니다.20의 발견 카드와 보스 마무리는 유지합니다.</p>'
 +'<p class="note">첫 장 품질은 진행 중입니다. 공간 구성, 네이티브 입력 전체 한 판·실청취·기본 저장 경로·최종1080p3회 검수가 남았습니다. 기술 검사와 합성 부하를 완성 판정으로 쓰지 않습니다.</p>'
 +'<p>WASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지.21은 별도 저장 namespace이며 기존 후보와 저장을 보존합니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('roles21','후반 회랑까지 이어지는 조작',
 '<p class="lead">자동 정책이 지나가던 길과 실제 마우스가 선택하던 목표가 달랐습니다. 후반 구역의 잘못된 제한을 바로잡았습니다.</p>'
 +'<h2>클릭한 방향으로 움직이기</h2><div class="columns">'+fig('roles21-zone1.png','실제 두 번째 구역 클릭. 목표x52.20을 선택하고 영웅x45.24→47.60으로 이동했습니다. 이전 제한은x18.8로 돌아가게 했습니다.')+fig('roles21-zone2.png','실제 세 번째 구역 클릭. 목표x105.06과 선택이 같고 영웅x98.83→101.05로 이동했습니다. 이전 제한은여기서도x18.8이었습니다.')+'</div>'
 +'<p>두 장면은 정상 정책·실제 획득 성장의9000/16000tick을 재구성한 입력 fixture입니다. 물리 루프를 멈추고 실제 마우스 이벤트 뒤 제품 컨트롤러로30정상 core step을 적용했습니다. 수동 전체나 실시간 전투로 확대하지 않습니다. 엔진exit0/stderr0,14개 좌표·메뉴·복원 검사와28개 출처·보존 감사도 확인했습니다.</p>'
 +'<h2>원거리와 돌진을 구분하기</h2><p>원거리 적은 키큰 청록 몸체와 수직 지팡이, 돌진 적은 낮고 넓은 몸체와 전방 기울기를 사용합니다. 실제 dash에는 달리기, 회복에는 idle을 연결해 두 번째 타격처럼 보이던 표현을 제거했습니다. 동작·빙결·메뉴·사체 재질·지팡이·reset23검사를 통과했습니다. 전투·성장 규칙을 바꾸지 않았습니다.</p>'
 +'<h2>혼합 군중의 비용 확인</h2>'+fig('roles21-crowd.png','합성129일반/33원거리/18돌진의1080p 부하입니다. 정상 전투가 이 배열로 모였다는 뜻은 아닙니다. 지팡이를 한 표면으로 합치고 먼 적의 이동 자세 갱신을 제한했습니다.')
 +'<p>같은 조건의 최초21 평균17.85ms/p9521.35/draw599에서 최적화 후14.85ms/16.69/533으로 줄었습니다. 원20 기준은13.54ms/14.60/467입니다. OS 단조 시계·MSAA2·vsync off·uncapped·120warmup+360frame이며 정상 core·전체FX·최종3회 검수가 아닙니다.</p>'
 +'<p><a href="'+rel(B/'full21/STATUS.ko.md')+'">현재 상태와 남은 작업</a> · <a href="'+rel(B/'full21/runtime/native-input01/RESULT.json')+'">실제 입력 기록</a> · <a href="'+rel(B/'full21/independent-audit01/RESULT.json')+'">28개 감사</a> · <a href="'+rel(B/'roles21/crowd02/RESULT.json')+'">혼합 부하 원시 결과</a></p>')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,ref])
  if not (p.parent/ref.split('#')[0]).resolve().is_file():missing.append([p.name,ref])
report={'pages':len(list(BOOK.glob('*.html'))),'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p) for p in BOOK.rglob('*') if p.is_file()},'scope':'Actual package21 later-zone mouse fixtures; synthetic crowd/motion proofs separately labeled; browser QA pending.'};(BOOK.parent/'BUILD.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing;print(BOOK,flush=True)
