from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';old=B/'full27/book-v24/dist';book=B/'full27/book-v25/dist';assert not book.exists();shutil.copytree(old,book)
rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v24 · 후보27','v25 · 候보27').replace('候보','후보').replace('</nav>','<a href="actor28.html">피격·회복 방향28 연구</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="actor28.html">피격 반동과 공격 회복 방향 시안28</a> · 현재 제품은27입니다.</p>',1)
 p.write_text(s,encoding='utf-8')
for source,dest in [('actor28/motion02/shots/25b-south-06.png','actor28-before.png'),('actor28/motion02/shots/28-south-06.png','actor28-after.png'),('actor28/replay01/shots/live-3.0.png','actor28-normal.png'),('actor28/motion02/film01/sampled-hit-before-after.mp4','actor28-sampled.mp4')]:shutil.copy2(B/source,book/'scenes'/dest)
body='''<h1>시안28 · 피격 반동과 공격 회복 방향</h1><p class="lead">상체의 반동을 키우고 공격 후 회복까지 지불된 공격 방향을 유지합니다. 현재 제품27에는 아직 적용하지 않았습니다.</p><h2>같은 피격 시점 비교</h2><figure><img src="scenes/actor28-before.png" alt="source25b의 네 역할 기본 포즈"><figcaption>source25b,동일복제역할fixture의피격6tick시점입니다.</figcaption></figure><figure><img src="scenes/actor28-after.png" alt="상체 반동이 추가된 시안28"><figcaption>보완28은다리로컬포즈를유지하며흉곽과팔이반응합니다. 공격예고와회복·빙결정지가우선합니다.</figcaption></figure><h2>느린 샘플 비교</h2><video controls preload="metadata" style="width:100%" src="scenes/actor28-sampled.mp4"></video><p>왼쪽25b/오른쪽28.북→동→남→서각2반복입니다. 여덟시점의포즈를각0.12초보여주는의도적인느린비교이며실시간연속플레이영상이아닙니다. 음향은없습니다. 이샘플만으로최종타격감승인하지않습니다.</p><h2>정상 획득 후반 전투</h2><figure><img src="scenes/actor28-normal.png" alt="정상 획득 후반 군중 전투에서 작동하는 시안28"><figcaption>현재27source기반에Actor28만대체한별도stage입니다. 새로운28EXE검수가아닙니다.</figcaption></figure><p>정상화염16000tick부터10sim초구간에서648회피격혼합이발생했고,마지막전체게임상태가독립기준과일치했습니다. 오류없이종료했습니다. 빙결·일시정지·재사용·공격우선순위·회복방향을포함한47항목검사도통과했습니다.</p><h2>남은 검수와 실패 기록</h2><p>첫검사는종료누수경고가있었고,상세진단중고정결과파일이재기록된보존실수도문서화했습니다. 원경고로그를유지하며성공으로바꾸지않습니다. 보완fixture와GPU는quiet종료했습니다. 정상속도연속동작·회복방향전후·추가CPU비용을확인한뒤제품채택을판단합니다.</p>'''
body+='<p>'+' · '.join(f'<a href="{rel(B/p)}">{label}</a>' for p,label in [('actor28/REVIEW.ko.md','전체 검수 범위'),('actor28/FAILURE-AND-PRESERVATION.ko.md','실패·보존 한계'),('actor28/fixture02/RESULT.json','보완 검사'),('actor28/replay01/RESULT.json','정상 후반 상태'),('actor28/motion02/film01/RESULT.json','샘플 영상 명세')])+'</p>'
s=(book/'candidate27.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>피격·회복 방향28 연구 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'actor28.html').write_text(s,encoding='utf-8')
missing=[];refs=0
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(book.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),ensure_ascii=False,indent=2),encoding='utf-8');assert not missing;print('BOOK25',refs,'refs missing0')
