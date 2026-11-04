from pathlib import Path
import json,shutil,re,os,html
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full22/book-v16/dist';BOOK=B/'full23/book-v17/dist';assert not BOOK.exists();shutil.copytree(OLD,BOOK)
rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
build=read(B/'full23/build/build.json');assert read(B/'full23/runtime/default-reload02/RESULT.json')['unchanged_profile_bytes']
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v16','제작 도감 v17').replace('후보22 / 이전 항목은 본문 번호 유지','후보23 / 이전 항목은 본문 번호 유지')
 s=s.replace('</nav>','<a href="profile23.html">안내·기본 저장23</a></nav>')
 if p.name=='hostile22.html':s=s.replace('제품은 후보21 그대로이며22는 미패키징 연구입니다.','해당 연구를 후보22에 통합했습니다. 이 페이지의 전후 그림은 당시 연구 장면입니다.')
 p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate22.html')
for name,source in {'hud23-before.png':B/'hud23/fixture01/shots/before.png','hud23-after.png':B/'hud23/fixture01/shots/1920x1080-ready.png','profile23-ending.png':B/'full23/runtime/default-save02/captures/default23-ending-1.60.png','profile23-stash.png':B/'full23/runtime/default-reload02/captures/default23-ui-003.png','profile23-ring.png':B/'full23/runtime/default-reload02/captures/state-0004-run-001-inventory.png'}.items():shutil.copy2(source,BOOK/'scenes'/name)
shell=(BOOK/'roles21.html').read_text(encoding='utf-8')
def fig(name,caption):return '<figure><img loading="lazy" src="scenes/'+name+'" alt="'+html.escape(caption)+'"><figcaption>'+caption+'</figcaption></figure>'
def page(name,title,body):
 s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell);s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S).replace(' aria-current="page"','');s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1);(BOOK/(name+'.html')).write_text(s,encoding='utf-8')
page('index','행동은 두 줄로, 장비는 다음 도전으로',
 '<p class="lead">회피와 회복약 안내를 분명히 나누고, 기본 저장 경로의 보상이 재실행한 다음 도전까지 이어지는지 확인했습니다.</p>'
 +fig('hud23-after.png','후반 빌드의 두 줄 행동 안내. 정상 획득 빌드를 재구성한 표시 fixture이며 실제 수동 전체 장면이 아닙니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">개발 후보23 실행 파일</a><a href="profile23.html">기본 저장과 장비 확인</a><a href="space22.html">공간 개선22</a><a href="candidate22.html">이전22 표지</a></div>'
 +'<p>회피 준비·대기 시간과 회복약 잔량을 두 줄에 고정했습니다. 실제 EXE가 기본 user 경로에 장비34개를 저장하고, 보관함에서 고른 반지가 두 번째 재실행 뒤에도 시작 장비에 적용되는 것을 확인했습니다.22의 배경·적 탄환과 전투·성장은 유지합니다.</p>'
 +'<p class="note">첫 장 품질은 진행 중입니다. 실제 수동 전체·실청취·최종1080p3회가 남았습니다. 중앙 공간과 전투 체감도 계속 개선해야 합니다. 저장의 이 성공 경로를 모든 오류 복구 승인으로 확대하지 않습니다.</p>'
 +'<p>WASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지. Quality23 별도 저장 경로이며 이전 사용자 저장은 옮기지 않았습니다. 검수로 새로 만든23 프로필과 revision도 보존합니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('profile23','읽기 쉬운 행동 안내와 이어지는 장비',
 '<p class="lead">좁은 한 줄에 합쳐지던 회피와 회복약을 분리하고, 실제 기본 저장의 다음 도전까지 확인했습니다.</p><div class="columns">'
 +fig('hud23-before.png','전: 준비 상태는 들어가도 더 긴 회피 대기 문구에서 단어가 끊기던 안내.')
 +fig('hud23-after.png','후: 준비 또는 대기 시간 한 줄, 회복약 잔량 한 줄. 별도 표시 fixture입니다.')+'</div>'
 +'<p>1920×1080·1280×720·1280×960에서 준비·대기·회복약0의9상태가 두 줄 안에 들어갔습니다. 표시 검사에서 임시 변경한 잔량·대기 필드는 복원했고 전체 전투 상태도 같았습니다. 기존 전투·조작 규칙은 유지합니다.</p>'
 +'<h2>실제 기본 경로에 보상 저장</h2>'+fig('profile23-ending.png','실제 후보23 EXE의 보상 저장 완료. 정상 획득 빌드23830tick을 재구성한 뒤 마지막 전투를 진행한 부분 검수로, 수동 전체 완주가 아닙니다.')
 +'<p>이전 QA 경로와 달리 제품의 기본 user://chapter-one-profile-v1.json을 그대로 사용했습니다. 후보23 전용 경로에 기존 파일이 없음을 먼저 확인했습니다. 보상 장비34개·완료1·revision1 저장, 재실행 시 같은 보관함을 확인했습니다.</p>'
 +'<div class="columns">'+fig('profile23-stash.png','실제 UI에서 반지를 다음 도전에 장착한 뒤, 또 다른 새 프로세스의 보관함에서도 ◆ 선택이 유지됐습니다.')
 +fig('profile23-ring.png','재실행 후 실제 냉기 도전→I 장비창. 피해+12%, 최대 생명력-10, 회수 반경+0.7m 반지가 적용됐습니다.')+'</div>'
 +'<p>반지 선택은 revision2로 저장됐고 두 번째 재실행 전후 프로필 byte는 같았습니다. 실제 시작 화면의 생명력110/110과 장비창 효과를 확인했습니다. UI를 관찰하는 동안 피해를 받은 뒤 장비창을 열었으므로 장비창의 현재 생명력을 무피해 시험으로 쓰지 않습니다. 세 성공 실행의 종료0·오류로그0,37개 독립 감사가 통과했습니다.</p>'
 +'<p>첫 검사 보조 스크립트는 예약어 변수 때문에 로드 전에 실패했습니다. 원본과 오류 로그를 보존했고 제품 저장 실패와 구분했습니다. 검수로 만든23 프로필34개·반지 선택·완료1과 revision은 그대로 보존합니다. 이전 사용자 저장은 읽어 옮기거나 덮어쓰지 않았습니다.</p><p>'
 +' · '.join('<a href="'+rel(B/p)+'">'+t+'</a>' for p,t in [('hud23/REVIEW.ko.md','HUD 검수 범위'),('full23/runtime/DEFAULT-SAVE-REVIEW.ko.md','저장·실패·입력 기록'),('full23/runtime/default-reload02/RESULT.json','두 번째 재실행 결과'),('full23/independent-audit01/RESULT.json','37개 감사'),('full23/STATUS.ko.md','현재 상태')])+'</p>')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,v])
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(BOOK.parent/'BUILD.json').write_text(json.dumps({'html':len(list(BOOK.glob('*.html'))),'references':len(refs),'missing':missing,'browser_review':'pending'},ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing
print({'html':len(list(BOOK.glob('*.html'))),'refs':len(refs),'missing':len(missing)},flush=True)
