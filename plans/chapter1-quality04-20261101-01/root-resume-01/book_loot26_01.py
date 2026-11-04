from pathlib import Path
import json,re,os,shutil
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';old=b/'full25b/book-v21/dist';book=b/'full26/book-v22/dist';assert not book.exists();shutil.copytree(old,book);rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v21 · 후보25b','v22 · 후보26').replace('</nav>','<a href="candidate26.html">현재 후보26 · 장비 이름</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><h2>현재 후보26</h2><p>바닥 장비 이름을 키우고 겹침과 가림을 줄였습니다. <a href="candidate26.html">실제 클릭 회수·녹음·측정과 남은 검수</a>를 확인하세요. 이전 번호 항목은 해당 시점의 기록입니다.</p>',1)
 p.write_text(s,encoding='utf-8')
for source,dest in [('loot26/fixture02/shots/normal-before.png','loot26-before.png'),('full26/runtime/native-loot02/proof/before.png','loot26-native-before.png'),('full26/runtime/native-loot02/proof/collected.png','loot26-native-collected.png'),('loot26/fixture02/shots/dense-1920.png','loot26-dense.png'),('full26/runtime/native-loot02/proof/actual-game-mix.wav','actual-game-mix26.wav')]:shutil.copy2(b/source,book/'scenes'/dest)
body='''<h1>후보26 · 바닥 장비 이름을 읽기 쉽게</h1><p class="lead">커진 이름,겹침 간격,원래 드롭 위치를 알려주는 연결선으로 전리품 발견을 돕습니다.</p><h2>이전 표시와 실제 제품</h2><figure><img src="scenes/loot26-before.png" alt="기본 속성으로 표시한 작은 장비 이름"><figcaption>같은 정상 획득 상태에서 이전 기본 라벨 속성을 적용한 표시fixture입니다.</figcaption></figure><figure><img src="scenes/loot26-native-before.png" alt="후보26 실제 EXE에서 읽히는 장비 이름"><figcaption>후보26 실제 EXE:불꽃의 박동의 마법봉을 화면에서 읽고 이동할 수 있습니다.</figcaption></figure><p>15논리픽셀 기준으로 글자를 조정하고,적·기둥에 가려지지 않게 그립니다. 원래8m표시 범위와 드롭·자동 회수 규칙은 유지합니다. rare/magic/common 순서로 간격을 정리하고,옮긴 이름은 원래 빛기둥에 얇은 선으로 연결합니다. Actor26 피격 연구는 이 제품에 포함하지 않았습니다.</p><h2>실제 클릭에서 발견 카드까지</h2><figure><img src="scenes/loot26-native-collected.png" alt="좌클릭 이동으로 회수한 뒤 발견 카드가 표시된 실제 제품"><figcaption>실제 좌클릭1회로UID30을 회수하고,바닥 이름과 빛기둥이 사라진 뒤 발견 카드가 나타났습니다.</figcaption></figure><p>정상 획득16143tick 체크포인트를 입력 대기 상태로 준비한 뒤,실제 마우스 클릭과 원래 이동 controller로16200tick에 회수했습니다. pilot은 꺼져 있었고 종료 오류는 없었습니다. 메뉴부터의 수동 전체 플레이 증거로 확대하지 않습니다.</p><h2>밀집 표시 확인</h2><figure><img src="scenes/loot26-dense.png" alt="12개 장비 이름을 겹치지 않게 배치한 표시fixture"><figcaption>복제12개 장비를 겹쳐 둔 표시fixture.1920×1080/1440×810/1280×720에서 이름 간격과 원래 빛기둥 위치를 확인했습니다. 자연 발생한12개 드롭 장면은 아닙니다.</figcaption></figure><h2>대표1080p 한 회</h2><p>실제 메뉴에서 정상 냉기 정책을 시작해10초 준비+60초 측정했습니다. p95 9.363ms/p99 12.459ms/최장52.959ms,33.33ms 초과5개,13734표본. 전후 실제 이미지1920×1080,보고Texture2304×1296은 그대로 기록했습니다. 측정 중 캡처·녹음은 없었습니다. RTX2070SUPER/Forward+/MSAA2/VSync off/uncapped 조건의 초반 대표 한 회이며 최종 세 회 승인이나 전체 장 성능 증거는 아닙니다.</p><h2>실제 게임 출력 녹음</h2><audio controls preload="metadata" style="width:100%;max-width:600px" src="scenes/actual-game-mix26.wav"></audio><p>클릭 회수 구간의 게임 Masterbus 출력2.688초/48kHz/stereo16bit입니다. 마이크나 다른 앱 소리는 포함하지 않았습니다. 신호 최대값2756/32768,포화 표본0. 녹음 확보와 파형 수치는 실제 청취·음향 밸런스 승인과 구분합니다.</p><h2>남은 검수와 보존</h2><p>독립 보존 감사36항목을 통과했습니다. 이전 후보와 실패·저장 기록을 모두 유지했습니다. 수동26 도전은입력 왕복 지연 중 첫 성장 선택 뒤18.9sim초/24처치 패배로 종료됐습니다. 같은 방식을 반복하지 않으며,수동 완주로 인정하지 않습니다. 실청취·최종 제품 세 회 성능·공간과 전투 최종 품질은 계속 검수합니다.</p><p>'''
body+=' · '.join('<a href="'+rel(b/p)+'">'+t+'</a>' for p,t in [('full26/STATUS.ko.md','현재 상태'),('full26/build/build.json','제품 고정'),('full26/independent-audit01/RESULT.json','보존 감사'),('loot26/REVIEW.ko.md','개선·실패·검수 범위'),('full26/runtime/native-loot02/proof/RESULT.json','실제 클릭 기록'),('full26/performance/runs/formal01/independent-audit.json','성능 원시 감사'),('full26/runtime/manual01/RESULT.json','수동 도전 결과')])+'</p>'
s=(book/'candidate25b.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>후보26 장비 이름 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'candidate26.html').write_text(s,encoding='utf-8')
refs=[];missing=[]
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,v])
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps({'html':len(list(book.glob('*.html'))),'references':len(refs),'missing':missing,'browser_review':'pending'},ensure_ascii=False,indent=2),encoding='utf-8');assert not missing;print(len(list(book.glob('*.html'))),len(refs))
