from pathlib import Path
import json,hashlib,shutil,re,os,html
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full17b/book-v10/dist';BOOK=B/'full18/book-v11/dist';assert not BOOK.exists();shutil.copytree(OLD,BOOK)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
build=read(B/'full18/build/build.json');matrix=read(B/'full18/runtime/ground-matrix01/RESULT.json');assert matrix['all_new_floor_covers'] and len(matrix['cases'])==36
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.group(1),m.group(2)
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v10','제작 도감 v11').replace('후보17b / 원본17·이전 항목은 본문 번호 유지','후보18 / 이전 항목은 본문 번호 유지')
 s=s.replace('</nav>','<a href="ground18.html">경계 바닥18</a></nav>');p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate17b.html')
assets={
 'ground18-before.png':B/'full17b/runtime/boundary01/captures/boundary-z19.png',
 'ground18-after.png':B/'full18/runtime/ground-matrix01/shots/same17b-boundary-z19.png',
 'ground18-wide.png':B/'full18/runtime/ground-matrix01/shots/1920x540-zone2-x1-z1.png',
 'ground18-corner.png':B/'full18/runtime/ground-matrix01/shots/1440x810-zone0-x-1-z-1.png'}
for n,p in assets.items():shutil.copy2(p,BOOK/'scenes'/n)
shell=(BOOK/'candidate17b.html').read_text(encoding='utf-8')
def fig(n,text):return '<figure><img loading="lazy" src="scenes/'+n+'" alt="'+html.escape(text)+'"><figcaption>'+text+'</figcaption></figure>'
def page(name,title,body):
 s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell)
 s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S).replace(' aria-current="page"','')
 s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1);(BOOK/(name+'.html')).write_text(s,encoding='utf-8')
page('index','경계에서도 끊기지 않는 회랑',
 '<p class="lead">보행 경계로 가거나 넓은 화면을 사용해도 바닥 끝과 빈 배경이 드러나지 않게 고쳤습니다.</p>'
 +fig('ground18-after.png','후보18 실제 패키지 GPU. 영웅을 (-4,19)에 직접 놓은 경계 검수이며, 정상 한 판 장면은 아닙니다. 이전17b에서 보이던 왼쪽 아래 빈 삼각 영역이 흙바닥으로 이어집니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">후보18 실행 파일</a><a href="ground18.html">수정 전후와 넓은 화면</a><a href="candidate17b.html">이전17b 표지</a></div>'
 +'<p>냉기 파쇄·사체 소멸과 장비·보상 표현은17b를 이어받습니다. 바닥의 크기와 중심만 현재 시야에 맞추며 전투·충돌 규칙은 유지합니다.</p>'
 +'<p class="note">첫 장의 최종 품질은 진행 중입니다. 일반·중간 정예의 풍부한 동작, 자연스러운 공간 구성, 수동 한 판·실청취·저장UI·최종 성능 검수가 남아 있습니다. <a href="'+rel(B/'full18/STATUS.ko.md')+'">후보18 상태와 검수 범위</a></p>'
 +'<p>WASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지. 기존 실행본과 저장은 보존하며18은 별도 저장 경로를 사용합니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('ground18','시야가 바닥을 벗어나던 경계',
 '<p class="lead">캐릭터는 움직일 수 있는 범위 안에 있었지만, 기울어진 카메라의 시야는 기존 바닥보다 멀리 닿았습니다.</p>'
 +'<h2>빈 삼각 영역을 바닥으로 잇기</h2><div class="columns">'+fig('ground18-before.png','수정 전17b 실제 패키지: 보행 경계 z19에서 왼쪽 아래에 바닥 평면의 끝과 빈 배경이 드러납니다. 기존 PNG를 보존해 사용했고 같은 검사를 다시 실행하지 않았습니다.')+fig('ground18-after.png','수정 후18 실제 패키지: 같은 영웅 위치·카메라 방향에서 바닥이 화면 끝까지 이어집니다.18 행렬은 화면비 검증을 위해 UI content-scale을 끄므로 전후 전체 UI 픽셀 동일 비교가 아닙니다.')+'</div>'
 +'<h2>시야와 보행 범위를 함께 계산</h2><p>현재 화면의 네 모서리를 바닥에 투영하고, 세 구역의 전체 보행 가능 카메라 위치와3m 여유를 더합니다. 화면 크기나 카메라 크기가 바뀔 때만 갱신합니다. 기존 PlaneMesh 한 개와 월드 좌표 셰이더를 그대로 쓰므로 전투 구역의 바닥 무늬와 충돌은 유지됩니다.</p>'
 +'<h2>16:9·4:3·32:9에서 확인</h2>'+fig('ground18-wide.png','1920×540 실제 패키지 GPU 경계 fixture. 넓은 화면에서도 바닥이 이어집니다. 영웅 직접 배치이며 정상 한 판·실시간 성능 증거가 아닙니다.')
 +fig('ground18-corner.png','1440×810 구역0의 바깥 모서리 검수. 빈 배경은 제거했지만 바깥 흙바닥의 자연스러운 공간 구성은 계속 개선합니다.')
 +'<p>3구역 × 4모서리 × 3화면비 =36개 경우를 소스 stage와 실제18 EXE에서 각각 검사했습니다. 새 바닥은 모두 시야를 덮고, 같은 카메라 투영에 기존160×70 영역을 적용하면36개 모두 일부가 밖으로 나갑니다. 양쪽 결과 행이 같고 코어 상태는 그대로이며 surface는1개입니다. 각 실행13PNG·exit0/stderr0입니다.</p>'
 +'<p>전체 정상 냉기 GPU의6분37.7초·3451처치·파쇄840은 변경 없는 코어/표현의 원17 결과입니다.18 전체 런으로 확대하지 않습니다.18은 새 패키지 출처 감사·30초 정상 정책·경계GPU를 별도로 확인했습니다.</p>'
 +'<p><a href="'+rel(B/'full18/runtime/ground-matrix01/RESULT.json')+'">실제 패키지36개 결과</a> · <a href="'+rel(B/'full18/independent-audit01/RESULT.json')+'">보존·출처 감사</a> · <a href="'+rel(B/'full18/STATUS.ko.md')+'">현재 상태</a></p>')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,ref])
  if not (p.parent/ref.split('#')[0]).resolve().is_file():missing.append([p.name,ref])
report={'pages':len(list(BOOK.glob('*.html'))),'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p) for p in BOOK.rglob('*') if p.is_file()},'scope':'18 packaged edge coverage,17b before frame and historical17 fullGPU separately labelled. Browser QA pending.'};(BOOK.parent/'BUILD.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing;print(str(BOOK),flush=True)
