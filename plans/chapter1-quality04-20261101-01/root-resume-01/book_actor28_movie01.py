from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';old=B/'full27/book-v25/dist';book=B/'full27/book-v26/dist';assert not book.exists();shutil.copytree(old,book)
rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v25 · 후보27','v26 · 후보27').replace('</nav>','<a href="actor28-movie.html">연속 전투28 · 비용</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="actor28-movie.html">시안28의 연속 전투 영상과 비용·동기 한계</a></p>',1)
 p.write_text(s,encoding='utf-8')
for variant in ['control','after']:shutil.copy2(B/f'actor28/normal-film01/{variant}/normal-speed.mp4',book/f'scenes/actor28-normal-{variant}.mp4')
body='''<h1>시안28 · 정상 속도 연속 전투와 비용</h1><p class="lead">각 연속 영상은 정상 성장한 같은 구간을 보여줍니다. 현재 제품은27이며 시안28은 미연결입니다.</p><h2>기존 Actor25b</h2><video controls preload="metadata" style="width:100%" src="scenes/actor28-normal-control.mp4"></video><h2>피격 반동 시안28</h2><video controls preload="metadata" style="width:100%" src="scenes/actor28-normal-after.mp4"></video><p>정상 획득 화염16000tick부터4sim초를 연속60fps로 기록했습니다. 두 게임 종료 상태는16241tick로 같고 각각 독립 기준과도 일치했습니다. 시안에서280회 피격 혼합이 발생했습니다. 앞선 느린 샘플 포즈 영상과 달리 연속 렌더이며,오프라인 기록이므로 실시간 성능이나 수동 플레이 증거는 아닙니다.</p><h2>정확한 동기 비교로 인정하지 않은 부분</h2><p>원본 프레임 수는245/246으로 한 장 다릅니다. 동일 프레임 수 가정과 마지막 동일 이미지 반복 제외 가정은 모두 실패했고 기록을 보존했습니다. 종료 후 오디오 정리 대기 구간이 원인일 가능성은 있으나,그 구간만의 차이라고 증명하지 못했습니다. 임의로 영상을 잘라 맞추지 않았습니다. 각 정상속도 영상으로만 제시하며,전체 재생·프레임 동기·타격감 최종 승인으로 확대하지 않습니다.</p><h2>같은 구간의 CPU 비용</h2><p>정상 화염2800→3400tick/599표본각1회에서 배우 처리 평균1.872→1.961ms,추가약0.089ms였습니다. 최대4.075→4.261ms,양쪽 게임 상태 동일/오류없는 종료입니다. 이는개발용CPU귀속계측이며최종1080p프레임페이싱승인이아닙니다.</p><h2>다음 검수</h2><p>프레임과core tick를명시적으로연결한연속기록,공격예고→타격→회복방향전후,정상속도반동의시각판단을이어갑니다. 기존제품·실패원시·사용자저장은보존했습니다.</p>'''
body+='<p>'+' · '.join(f'<a href="{rel(B/p)}">{label}</a>' for p,label in [('actor28/normal-film01/REVIEW.ko.md','영상·실패·판단 범위'),('actor28/CPU-COMPARISON01.json','CPU 원시 비교'),('actor28/normal-film01/SCOPE.json','연속 기록 명세')])+'</p>'
s=(book/'actor28.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>시안28 연속 전투·비용 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'actor28-movie.html').write_text(s,encoding='utf-8')
refs=0;missing=[]
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(book.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),indent=2));assert not missing;print('BOOK26',refs,'refs missing0')
