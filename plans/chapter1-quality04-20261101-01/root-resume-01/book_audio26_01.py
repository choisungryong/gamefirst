from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01'
old=B/'full26/book-v22/dist';book=B/'full26/book-v23/dist';assert not book.exists();shutil.copytree(old,book)
rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v22 · 후보26','v23 · 후보26').replace('</nav>','<a href="audio26.html">실제 전투 음향 기록</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="audio26.html">후보26 전투 출력 세 구간과 공간 시안 검토</a></p>',1)
 p.write_text(s,encoding='utf-8')
body='<h1>후보26 · 실제 전투 출력 기록</h1><p class="lead">정상 획득한 후반 전투 세 구간을 실제 EXE의 게임 출력으로 기록했습니다.</p><p>각 구간 약14초/48kHz/스테레오입니다. 다른 학습 스킬도 함께 작동하므로 단일 스킬의 분리 녹음은 아닙니다. 마이크나 다른 앱 소리는 포함하지 않았습니다.</p>'
data=json.loads((B/'full26/audio/SIGNAL-REVIEW01.json').read_text(encoding='utf-8'))
for row,label in zip(data['runs'],['화염 시작 빌드','냉기 시작 빌드','번개 시작 빌드']):
 name=row['run'];shutil.copy2(B/f'full26/audio/{name}/proof/actual-game-mix.wav',book/f'scenes/audio26-{name}.wav')
 body+=f'<h2>{label}</h2><audio controls preload="metadata" style="width:100%;max-width:600px" src="scenes/audio26-{name}.wav"></audio><p>{row["duration_seconds"]:.3f}초 · 재생{row["played"]}회 · 슬롯 부족 생략{row["dropped"]}회 · 포화 표본{row["full_scale_samples"]}개</p>'
body+='<h2>판단 범위</h2><p>세 실행 모두 오류 없이 종료했고 마지막 전체 게임 상태가 독립 기준과 일치했습니다. 녹음·파형 수치는 실청취나 음향 밸런스 승인과 구분합니다. 번개 구간 생략1건의 효과 종류는 이번 자료로 알 수 없습니다. 원시 cue_counts는 순환하는 변형 번호 차이여서 효과별 재생 횟수로 사용하지 않았습니다. 원본을 보존하고 별도 해석 정정을 남겼습니다.</p>'
body+='<h2>공간 시안도 화면으로 판단</h2><p>성소 바닥의 돌 상감 이음새·얕은 음영을 별도 source 시안으로 시험 중입니다. 첫 시안은 지나친 대비와 불규칙한 끊김,두 번째는 거의 안 보이는 차이 때문에 채택하지 않았습니다. 현재 제품26에는 연결하지 않았습니다. 품질 개선이나 새 제품 완성으로 계산하지 않습니다.</p>'
body+='<p>'+' · '.join(f'<a href="{rel(B/p)}">{label}</a>' for p,label in [('full26/audio/REVIEW.ko.md','녹음 범위·정정'),('full26/audio/SIGNAL-REVIEW01.json','신호 분석·SHA'),('space27/REVIEW.ko.md','공간 시안 판단')])+'</p>'
s=(book/'candidate26.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>후보26 실제 전투 음향 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'audio26.html').write_text(s,encoding='utf-8')
missing=[];refs=0
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(book.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),ensure_ascii=False,indent=2),encoding='utf-8');assert not missing
print('BOOK23',refs,'references',flush=True)
