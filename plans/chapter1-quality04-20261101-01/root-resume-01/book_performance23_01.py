from pathlib import Path
import json,shutil,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full23/book-v17/dist';BOOK=B/'full23/book-v18/dist';assert not BOOK.exists();shutil.copytree(OLD,BOOK)
rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v17','제작 도감 v18').replace('</nav>','<a href="performance23.html">성능·긴 프레임23</a></nav>')
 if p.name=='index.html':
  s=s.replace('실제 수동 전체·실청취·최종1080p3회가 남았습니다.','실제 수동 전체·실청취가 남았습니다. 현재23의 대표1080p 세 회 기준은 통과했지만 긴 프레임을 추가 개선 중입니다.')
  s=s.replace('</main>','<h2>대표 성능과 남은 끊김</h2><p>같은 후보23의 세 회 측정은 p95 기준을 충족했습니다. 약54초의 긴 프레임을 추적해 반복 메시 생성 비용도 줄이는 별도24 시안을 만들었습니다.</p><p><a href="performance23.html">실제 크기·원시 기록·미연결 시안 보기</a></p></main>')
 p.write_text(s,encoding='utf-8')
shutil.copy2(B/'full23/performance/runs/formal03/postflight.png',BOOK/'scenes/performance23-post.png')
data=json.loads((B/'full23/performance/THREE-RUNS.json').read_text());assert data['target_met_all_three']
table='<table style="width:100%;font-variant-numeric:tabular-nums"><thead><tr><th>회</th><th>p95 ms</th><th>p99 ms</th><th>최장 ms</th></tr></thead><tbody>'
for i,a in enumerate(data['audits'],1):table+='<tr><td>%02d</td><td>%.3f</td><td>%.3f</td><td>%.3f</td></tr>'%(i,a['p95_ms'],a['p99_ms'],a['worst_ms'])
table+='</tbody></table>'
body='<h1>대표 성능 통과와 남은 긴 프레임</h1><p class="lead">평균적인 흐름과 순간적인 끊김을 따로 확인합니다.</p>'+table
body+='<p>실제 후보23 EXE·RTX2070SUPER·Forward+·MSAA2·VSync off·uncapped·정상 냉기90131 정책입니다. 메뉴에서 실제 클릭으로 시작해10초 준비 뒤60초의 OS 단조 시간 프레임 간격을 수집했습니다. 세 회 모두 유효하고 p95≤16.67ms입니다. 긴 프레임도 제외하지 않았습니다. 전체7분 모든 구간·모든 기기·매 프레임60FPS·수동 플레이 승인으로 확대하지 않습니다.</p>'
body+='<figure><img src="scenes/performance23-post.png" alt="실제 측정 완료 뒤의 정상 전투"><figcaption>세 번째 측정이 끝난 뒤의 실제1920×1080 readback입니다. 준비·표본 구간 안에서는 이미지 읽기나 PNG 캡처를 하지 않았습니다.</figcaption></figure>'
body+='<h2>보고된 크기와 실제 이미지 크기</h2><p>같은 살아있는 프레임에서 창과 실제 Image readback은1920×1080인데 Texture2D.get_size는2304×1296이었습니다. 이전 크기 불일치 무효 기록은 유지합니다. 새 계약은 측정 전후 실제 이미지와PNG 크기, 매 프레임 창·논리 뷰포트·스케일·MSAA 불변을 함께 확인합니다. 원시 열 texture_reported는2304×1296을 그대로 보존합니다. 매 프레임 readback을 한 것처럼 주장하지 않습니다.</p>'
body+='<h2>70–81ms 순간 지연 줄이기</h2><p>약54초의 긴 프레임이 세 회에서 반복됐습니다. 별도 소스 계측에서 같은 불변 모델 경로가 인스턴스ID마다 재합성돼 캐시가96→174개로 늘어나는 것을 찾았습니다. 미연결 Actor24 시안은 불변 메시만 공유하고 재질·골격·포즈는 배우별로 유지합니다. 같은10sim초 계측에서 actor callback 최장이170.7→56.9ms로 줄고, 전체 전투 상태는 같았습니다. 이 값은 fixed60 계측이며 위 실제 프레임 표와 직접 비교하지 않습니다.</p>'
body+='<p>메시 배열 일치·독립 재질/골격·빙결·회복·초기화 등45검사가 통과했습니다. 제품은 여전히23이며24 EXE는 없습니다. 실제 화면 확인 뒤 채택하며 새 제품 성능은 다시 검수해야 합니다. 수동23 도전은18.9초 패배로 남겨 두었고 자동 정책 측정으로 수동 성공을 대신하지 않았습니다.</p><p>'
body+=' · '.join('<a href="'+rel(B/p)+'">'+t+'</a>' for p,t in [('full23/performance/REVIEW.ko.md','세 회 결과와 범위'),('full23/performance/CONTRACT.ko.md','크기·측정 계약'),('full23/performance/THREE-RUNS.json','독립 세 회 집계'),('full23/performance/LONG-FRAMES.json','긴 프레임 원시 행'),('spike24/REVIEW.ko.md','미연결24 연구'),('full23/runtime/manual01/REVIEW.ko.md','수동 도전 실패')])+'</p>'
shell=(BOOK/'profile23.html').read_text(encoding='utf-8');shell=re.sub(r'<title>.*?</title>','<title>대표 성능과 긴 프레임 · 잿빛 회랑 도감</title>',shell);shell=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',shell,flags=re.S).replace(' aria-current="page"','');(BOOK/'performance23.html').write_text(shell,encoding='utf-8')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,v])
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(BOOK.parent/'BUILD.json').write_text(json.dumps({'html':len(list(BOOK.glob('*.html'))),'references':len(refs),'missing':missing,'browser_review':'pending'},ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing
print({'html':len(list(BOOK.glob('*.html'))),'refs':len(refs),'missing':len(missing)},flush=True)
