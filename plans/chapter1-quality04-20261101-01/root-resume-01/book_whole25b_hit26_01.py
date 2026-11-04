from pathlib import Path
import json,re,shutil,os
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';old=b/'full25b/book-v20/dist';book=b/'full25b/book-v21/dist';assert not book.exists();shutil.copytree(old,book);rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v20 · 후보25b','v21 · 후보25b').replace('</nav>','<a href="whole25b.html">전체 전투25b</a><a href="hit26.html">피격 동작26 연구</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><h2>전체 전투와 다음 타격 반응</h2><p><a href="whole25b.html">후보25b 실제 전체 전투</a>에서 보스 보상까지 표시 수명을 확인했습니다. <a href="hit26.html">26 피격 동작</a>은 별도 미채택 시안입니다.</p>',1)
 p.write_text(s,encoding='utf-8')
def page(name,title,body):
 s=(book/'candidate25b.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/name).write_text(s,encoding='utf-8')
def links(entries):return '<p>'+' · '.join('<a href="'+rel(b/p)+'">'+t+'</a>' for p,t in entries)+'</p>'
for source,dest in [('full25b/runtime/gpu-cold01/captures/run-001-frame-270.png','whole25b-late.png'),('full25b/runtime/gpu-cold01/captures/victory-after-0.35.png','whole25b-death035.png'),('full25b/runtime/gpu-cold01/captures/victory-after-0.90.png','whole25b-death090.png'),('full25b/runtime/gpu-cold01/captures/victory-after-1.60.png','whole25b-reward.png'),('hit26/compare01/shots/south-before.png','hit26-before.png'),('hit26/compare01/shots/south-after.png','hit26-after.png'),('hit26/replay01/shots/live-3.0.png','hit26-normal.png')]:shutil.copy2(b/source,book/'scenes'/dest)
body='''<h1>후보25b · 보스 보상까지 전체 전투</h1><p class="lead">재사용한 일반 적 표시가 세 구역을 거쳐 마지막 보상까지 정상적으로 유지되는지 확인했습니다.</p><figure><img src="scenes/whole25b-late.png" alt="실제 후보25b 후반 냉기 전투"><figcaption>실제25b 패키지의 재의 성소 후반 장면입니다.</figcaption></figure><h2>6분37.7초의 게임 진행</h2><p>처음부터 정상 냉기90131 자동 정책·기본HP·정상 획득·저장 비활성으로 실행했습니다.23862tick/3451처치/레벨12/34장비에서 첫 승리했습니다. 보상·장비를 포함한10상태가 기존16 패키지의 전체 냉기 기준과 일치했습니다. 파쇄840회,냉기 사망 원인823회도 확인했습니다. 이 시간은 시뮬레이션 시간이며 외부 벽시계 시간을 대신하지 않습니다.</p><h2>추가 생성 없이 끝까지</h2><p>224개 일반 적 표시 노드로3461회 재사용했습니다.794개의 반 초 간격 core-tick 표본에서 소유 관계와entity key 불일치가 없고,보관 개수는224개 이내였습니다. 종료exit0/stderr0. 표본 밖의 모든 프레임을 검사했다는 뜻은 아닙니다.</p><h2>쓰러짐에서 고유 보상으로</h2><figure><img src="scenes/whole25b-death035.png" alt="사망 후0.35초 보스와 사라지는 주변 무리"><figcaption>사망 후0.35초:주변 무리가 물러나며 보스 동작을 드러냅니다.</figcaption></figure><figure><img src="scenes/whole25b-death090.png" alt="사망 후0.90초 기울며 쓰러지는 보스"><figcaption>0.90초:보스 붕괴 동작이 이어집니다.</figcaption></figure><figure><img src="scenes/whole25b-reward.png" alt="1.60초 후 겨울의 심장 보상 모달"><figcaption>1.60초:고유 장비 겨울의 심장과 다음 도전 안내가 나타납니다.</figcaption></figure><h2>검수의 범위</h2><p>캡처27개를 보존했고,중간·후반과 위 사망 후 세 장을 직접 확인했습니다. 자동 전체 검사이며 수동 전체 플레이·실제 음향 청취·최종 성능 세 회 승인으로 확대하지 않습니다. 캡처와focus무시를 포함해 대표formal성능검사와도 구분합니다. 바닥 장비 이름이 작게 읽히는 문제는 추가 개선 대상입니다.</p>'''
body+=links([('full25b/runtime/WHOLE-COLD-REVIEW.ko.md','검수와 남은 차이'),('full25b/runtime/gpu-cold01/RESULT.json','전체 결과'),('full25b/runtime/gpu-cold01/gpu-launch.json','실제 실행 조건'),('full25b/runtime/gpu-cold01/gpu-execution.json','종료 원시 기록'),('full25b/runtime/gpu-cold01/PRESERVATION.json','보존 확인')]);page('whole25b.html','후보25b 전체 전투',body)
body='''<h1>미채택26 · 걸음을 유지하는 피격 반응</h1><p class="lead">몸이 맞았다는 신호를 상체에 더하면서,다리 보행과 공격 예고를 유지하는 시안입니다.</p><h2>같은 시안에서 새 혼합을 끄고 켜기</h2><figure><img src="scenes/hit26-before.png" alt="상체 피격 혼합을 끈 네 역할 근접 비교"><figcaption>혼합OFF:walker/ranged/charger/중간 정예의 같은 방향·피격 나이입니다.</figcaption></figure><figure><img src="scenes/hit26-after.png" alt="상체 피격 혼합을 켠 네 역할 근접 비교"><figcaption>혼합ON:머리와 가슴에 짧은 반응이 생깁니다. 다리 포즈는 유지합니다. 별도25bEXE와의 비교가 아닌26표시기의 기능off/on 근접fixture입니다.</figcaption></figure><p>기존 모델의hit애니메이션 상체9bone을0.2초 동안 최대.55로 혼합합니다.13개의 초기 캐시를 이용하며공격 예고·돌진·회복·사망이 우선합니다. 빙결과 일시정지에는 완성된 표시 포즈를 그대로 유지하고,지팡이도 새 손 위치를 따릅니다.</p><h2>정상 화염 후반 일부 구간</h2><figure><img src="scenes/hit26-normal.png" alt="시안26 정상 화염 후반 부분 재생"><figcaption>정상 획득16000tick 재구성 뒤10sim초 부분 재생:648회 피격 혼합,전체 core 독립 기준 일치,quiet. 실제 제품·수동·전체·성능 승인 자료는 아닙니다.</figcaption></figure><h2>확인한 것과 남은 판단</h2><p>43개 헤드리스 표시 검사와네 방향의8개 근접 이미지,정상 화염 구간4개 이미지를 확인했습니다. 같은 화염2800→3400tick fixed60 CPU계측에서 배우 평균1.83→1.91ms/최대4.21→4.27ms였습니다. 이 값은 실시간 프레임 간격이 아닙니다. 반응 강도는 아직 작아연속 동작과 타격감 판단이 더 필요합니다. 제품은25b 그대로이며26 EXE는 없습니다.</p>'''
body+=links([('hit26/REVIEW.ko.md','시안 설명과 범위'),('hit26/fixture02/RESULT.json','43개 표시 검사'),('hit26/compare01/RESULT.json','근접 비교 상태'),('hit26/replay01/RESULT.json','정상 일부 구간'),('hit26/CPU-COMPARISON01.json','CPU 부분 대조')]);page('hit26.html','미채택26 피격 동작',body)
refs=[];missing=[]
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,v])
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps({'html':len(list(book.glob('*.html'))),'references':len(refs),'missing':missing,'browser_review':'pending'},ensure_ascii=False,indent=2),encoding='utf-8');assert not missing;print(len(list(book.glob('*.html'))),len(refs))
