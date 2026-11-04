from pathlib import Path
import re,os,json,shutil
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';old=b/'full24/book-v19/dist';book=b/'full25b/book-v20/dist';assert not book.exists();shutil.copytree(old,book);rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v19 · 후보24','v20 · 후보25b').replace('</nav>','<a href="candidate25b.html">현재 후보25b</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><h2>최신 후보25b</h2><p>일반 적 표시 재사용과 실제 릴리스 검수는 <a href="candidate25b.html">후보25b 현황</a>을 확인하세요. 아래 후보24 항목은 이전 시점 기록입니다.</p>',1)
 p.write_text(s,encoding='utf-8')
shutil.copy2(b/'full25b/performance/runs/formal01/postflight.png',book/'scenes/candidate25b-post.png')
body='''<h1>후보25b · 무리 생성 때의 끊김 줄이기</h1><p class="lead">기존 냉기 파쇄·역할 동작·보상 리듬을 유지하며 반복 생성 비용을 줄였습니다.</p><figure><img src="scenes/candidate25b-post.png" alt="후보25b 실제 EXE의 측정 종료 뒤 군중 전투"><figcaption>후보25b 실제 패키지,1080p 측정이 끝난 뒤 화면입니다.</figcaption></figure><h2>보존과 변경</h2><p>메뉴 전에 일반 적 표시 노드224개를 준비하고, 게임 상태에서 사라진 적의 노드만 종류별로 재사용합니다. 남아 있는 사체·정예·최종 보스는 기존 수명을 유지합니다. core16/World22/FX22/HUD23/Input21과 모든 과거 후보·저장을 보존했습니다.</p><h2>실제 제품의 대표 측정 한 회</h2><table><tr><th>제품</th><th>p95 ms</th><th>p99 ms</th><th>최장 ms</th><th>33.33ms 초과</th></tr><tr><td>24</td><td>9.182</td><td>13.678</td><td>109.208</td><td>55</td></tr><tr><td>25b</td><td>9.282</td><td>12.575</td><td>56.330</td><td>6</td></tr></table><p>각 실제EXE 한 회/RTX2070SUPER/정상 냉기90131 정책/실제 메뉴 시작/focus활성/Forward+/MSAA2/VSync off/uncapped/10초 준비+60초 OS 단조 프레임 간격입니다.25b는13978표본,실제 전후1920×1080,재사용399회/누적생성224개/종료stderr0을 확인했습니다. 측정 중 이미지 읽기나PNG저장은 하지 않았습니다. source 대조도 별도 보존했습니다.</p><p>보고 Texture 크기2304×1296은 원시 기록 그대로입니다. release의 static_memory_bytes=0은 메모리 사용0이라는 뜻이 아니며 메모리 증거로 쓰지 않습니다. 준비 비용은 별도 headless 표시setup 계측에서 추가약.69초/정적메모리약20–24MB였습니다. 전체 시작시간이나 프로세스working set 측정은 아닙니다.</p><h2>실패를 남기고 릴리스에서 수정</h2><p>후보25는 보관 함수를assert안에서 호출해 릴리스에서 호출이 생략되고 고아 표시 노드가 남았습니다. 실패EXE·stage·원시 로그를 보존했습니다.25b는 동작을assert밖에서 실행하고 새 패키지 종료 검사와 실제 재사용을 확인했습니다. source검사 성공이release성공을 보장하지 않았던 사례입니다.</p><h2>남은 검수</h2><p>현재 수치는 초반 대표 한 회이며 최종 세 회 승인이 아닙니다. 전체 전투의 재사용 수명,정상 속도 수동 전체,실제 음향 청취,중앙 공간과 전투·보상 최종 품질은 계속 검수합니다. 기술 검사로 최종 완성을 대신하지 않습니다.</p><p>'''
body+=' · '.join('<a href="'+rel(b/p)+'">'+t+'</a>' for p,t in [('full25b/STATUS.ko.md','현재 상태'),('full25b/build/build.json','패키지 고정'),('full25/FAILURE.ko.md','릴리스 실패'),('pool25/REVIEW.ko.md','연구·비용·검사 범위'),('pool25/fixed-fixture01/RESULT.json','수정본50검사'),('pool25/source-performance/MATCHED-COMPARISON01.json','source대조'),('full25b/performance/runs/formal01/independent-audit.json','실제 제품 원시 감사')])+'</p>'
s=(book/'candidate24.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>현재 후보25b · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'candidate25b.html').write_text(s,encoding='utf-8')
refs=[];missing=[]
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,v])
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps({'html':len(list(book.glob('*.html'))),'references':len(refs),'missing':missing,'browser_review':'pending'},ensure_ascii=False,indent=2),encoding='utf-8');assert not missing;print(len(refs))
