from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';old=B/'full26/book-v23/dist';book=B/'full27/book-v24/dist';assert not book.exists();shutil.copytree(old,book)
rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v23 · 후보26','v24 · 후보27').replace('</nav>','<a href="candidate27.html">현재 후보27 · 보스 안내</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="candidate27.html">현재 후보27: 보스 체력과 격노 안내를 함께 읽기</a></p>',1)
 p.write_text(s,encoding='utf-8')
for source,dest in [('hud27/fixture01/shots/before-1920.png','hud27-before.png'),('hud27/fixture01/shots/after-1920.png','hud27-after.png'),('full27/runtime/boss-phase01/proof/actual-boss-phase.png','hud27-actual.png')]:shutil.copy2(B/source,book/'scenes'/dest)
body='''<h1>후보27 · 격노 안내를 가리지 않게</h1><p class="lead">보스 체력 막대와 임시 전투 안내를 분리했습니다.</p><h2>같은 전투 상태에서 전후 비교</h2><figure><img src="scenes/hud27-before.png" alt="이전 y80 속성에서 격노 문구를 덮는 체력 막대"><figcaption>정상 획득 체크포인트에 기존 알림 위치를 적용한 비교 fixture입니다.</figcaption></figure><figure><img src="scenes/hud27-after.png" alt="체력 막대 아래로 분리되어 읽히는 격노 안내"><figcaption>막대 아래10논리픽셀 간격. 일반 전투 위치와 알림 수명은 유지합니다.</figcaption></figure><h2>실제 후보27 EXE</h2><figure><img src="scenes/hud27-actual.png" alt="실제 보스 격노 이벤트와 체력 막대가 분리된 후보27"><figcaption>정상 획득 냉기21983tick의 첫 실제 격노 이벤트를 원래 이벤트 처리로 표시했습니다.</figcaption></figure><p>실제1920×1080 화면에서 문구와 체력 막대를 함께 읽을 수 있습니다. 마지막 전체 게임 상태도 독립 기준과 일치했습니다. 이는 실제 패키지의 고정 시점 검수이며 수동 완주나 전체 실시간 전투·최종 성능 승인은 아닙니다.</p><h2>검증과 보존</h2><p>세 해상도에서 격노·회복약·획득 안내의 겹침을 검사했습니다. 패키징과30초 정상 정책검사,독립 보존 감사34항목이 통과했습니다. 후보26 이하·실패 기록·사용자 저장은 보존했습니다. 바닥27과 피격26 연구는 제품에 포함하지 않았습니다.</p><p>음향 실청취·최종 수동 전체·동일 최종 제품 대표 성능3회와 공간·공격 실루엣의 최종 품질은 남아 있습니다. 이전 제품의 측정과 완료 기록을 새 제품의 승인으로 바꾸지 않습니다.</p>'''
body+='<p>'+' · '.join(f'<a href="{rel(B/p)}">{label}</a>' for p,label in [('hud27/REVIEW.ko.md','수정·검수 범위'),('full27/build/build.json','제품 고정'),('full27/runtime/boss-phase01/proof/RESULT.json','실제 격노 기록'),('full27/independent-audit01/RESULT.json','보존 감사'),('full27/STATUS.ko.md','현재 상태')])+'</p>'
s=(book/'candidate26.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>후보27 보스 안내 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'candidate27.html').write_text(s,encoding='utf-8')
missing=[];refs=0
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(book.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),ensure_ascii=False,indent=2),encoding='utf-8');assert not missing
print('BOOK24',refs,'refs; missing0')
