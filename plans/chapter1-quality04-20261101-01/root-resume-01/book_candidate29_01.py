from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';old=B/'full28/book-v27/dist';book=B/'full29/book-v28/dist';assert not book.exists();shutil.copytree(old,book)
rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v27 · 후보28','v28 · 후보29').replace('</nav>','<a href="candidate29.html">현재 후보29 · 바닥에 닿는 그림자</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="candidate29.html">현재 후보29: 일반 적의 방향성 그림자로 접지감 보완</a></p>',1)
 p.write_text(s,encoding='utf-8')
for source,dest in [('space29/shadow01/shots/16000-before.png','shadow29-before.png'),('space29/shadow01/shots/16000-after.png','shadow29-after.png'),('full29/runtime/shadow01/proof/after.png','actual29-after.png')]:shutil.copy2(B/source,book/'scenes'/dest)
body='''<h1>후보29 · 바닥에 닿는 그림자</h1><p class="lead">기존 달빛 아래에서 일반 적과 중간 정예의 몸이 실제 방향성 그림자를 드리웁니다.</p><h2>같은 전투 상태에서 비교</h2><figure><img src="scenes/shadow29-before.png" alt="방향성 그림자가 꺼진 기존 일반 적"><figcaption>같은정상획득16000tick·카메라·빛·재질의이전표시입니다.</figcaption></figure><figure><img src="scenes/shadow29-after.png" alt="발밑과 몸 뒤 그림자가 생긴 새 표시"><figcaption>기존moon과동일model을사용해바닥에붙어선느낌을보완했습니다. 같은씬에서model그림자설정만전환한source비교입니다.</figcaption></figure><p>새조명·메시·충돌을추가하지않았습니다. 피격반동·공격회복방향·드롭과전투규칙은유지합니다. SSAO만켠시안은전투화면차이가작아채택하지않았으며,바닥상감27도여전히미채택입니다.</p><h2>실제 후보29</h2><figure><img src="scenes/actual29-after.png" alt="실제 후보29 EXE의 일반 적 그림자와 정상 전투"><figcaption>실제EXE/PCK의정상획득체크포인트후원래live정책과controller로진행했습니다.</figcaption></figure><p>활성·대기중인model mesh224개의그림자ON과OFF0을확인했습니다. 실제1920×1080/3400tick/독립전체게임상태동일/오류없는종료입니다. 112번재사용후에도설정이유지됐습니다.</p><h2>개발용 비용 비교</h2><p>2초준비+10초OS시계표본의각1회source검사에서p95 5.800→5.927ms/p99 6.558→6.821ms,최장35.785→37.147ms,33.33ms초과는각1회였습니다. 최대drawcall245→300. 두실행모두독립게임상태가같았습니다. 시작2929tick/끝3528·3529의1tick차이가있으며,최종집중된패키지대표성능3회로확대하지않습니다.</p><h2>전체 장 검수 진행</h2><p>후보29의냉기정상정책첫장전체GPU검사를시작했습니다. 실행과원시로그를추적하고있으며,종료결과가확인되기전완료로표시하지않습니다. 다른GPU검사를동시에실행하지않습니다. 수동완주·실청취·최종대표성능3회·전체후반공간과보상최종질감검수도남아있습니다.</p><p>독립보존감사39항목을통과했습니다. 후보28이하·실패증거·사용자저장은보존했습니다.</p>'''
body+='<p>'+' · '.join(f'<a href="{rel(B/p)}">{label}</a>' for p,label in [('full29/STATUS.ko.md','현재 상태'),('full29/build/build.json','제품 고정'),('space29/cost01/COMPARISON.json','비용 원시 비교'),('space29/shadow01/RESULT.json','같은 상태 전후'),('full29/runtime/shadow01/proof/RESULT.json','실제 제품 기록'),('full29/independent-audit01/RESULT.json','보존 감사')])+'</p>'
body=body.replace('112번재사용후에도설정이유지됐습니다.','풀에서112번꺼내사용한뒤에도설정이유지됐습니다. 이계수는첫사용도포함합니다.')
s=(book/'candidate28.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>후보29 바닥에 닿는 그림자 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'candidate29.html').write_text(s,encoding='utf-8')
refs=0;missing=[]
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(book.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),indent=2));assert not missing;print('BOOK28',refs,'refs missing0')
