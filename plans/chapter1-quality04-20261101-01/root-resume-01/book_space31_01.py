from pathlib import Path
import shutil,re,os,json
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';N=B/'full30/book-v33/dist';assert not N.exists();shutil.copytree(B/'full30/book-v32/dist',N);rel=lambda p:os.path.relpath(p,N).replace('\\','/')
shutil.copy2(N/'index.html',N/'history-index.html')
t=(N/'candidate30.html').read_text(encoding='utf-8');body='<h1>후보31 · 기둥 아래의 깊이</h1><p class="lead">기존 석조 장식을 살리면서 바닥에 드리우는 그림자를 더했습니다.</p><p>세 구역의 기둥33개에 좁은 방향 그림자를 적용했습니다. 이동·공격·성장·드롭 규칙은 그대로입니다. 장식이 단순해졌던 입체 기둥 시안은 채택하지 않았습니다.</p>'
for tick,label in [(2800,'앞뜰'),(12600,'무너진 성가대'),(19800,'회랑의 파수왕')]:
 body+=f'<h2>{label} · 같은 전투 상태 비교</h2>'
 for mode,caption in [('before','기존 장식과 접지 그림자'),('after','기존 장식에 방향 그림자 보강')]:
  body+=f'<figure><img loading="lazy" src="{rel(B/f"space31/shadow03/shots/{tick}-{mode}.png")}" alt="{label}: {caption}"><figcaption>{caption} · 정상 냉기 획득 상태의 소스 비교 화면, 실제 패키지 전체 검수와 별개</figcaption></figure>'
body+='<h2>확인한 범위</h2><p>전후 여섯 화면을 직접 검수했습니다. 냉기 투사체·주인공·드롭 이름·보스 위험원이 구별됩니다. 후반10초 비교에서 p95는7.322→7.372ms,33ms 초과는 양쪽0이었습니다. 단회 소스 측정이며 정식 패키지 성능 승인은 남았습니다.</p><p>후보31 실행 파일의 실제 전체 냉기 전투 검수는 진행 중입니다. 수동 전체 플레이·실청취·동일 후보의 최종 성능 검수도 남아 있습니다. 기술 통과만으로 1장 품질을 완성 처리하지 않습니다.</p><p>추가 캐릭터 파이프라인 개발과 GitHub 연결은 보류했습니다. 로컬 Git으로 소스 이력을 관리하며 기존 실행 파일·증거·사용자 저장은 보존합니다.</p>'
body+='<p>'+' · '.join(f'<a href="{rel(p)}">{label}</a>' for p,label in [(Path(json.loads((B/'full31/build/build.json').read_text())['exe']),'후보31 실행 파일'),(B/'space31/REVIEW.ko.md','공간 개선 검수'),(B/'space31/cost01/COMPARISON.json','비용 비교 원문')])+' · <a href="candidate30.html">이전 후보30</a> · <a href="history-index.html">이전 도감 표지</a></p>'
t=re.sub(r'<title>.*?</title>','<title>후보31 · 기둥 아래의 깊이</title>',t);t=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S)
for name in ['index.html','candidate31.html']:(N/name).write_text(t,encoding='utf-8')
for p in N.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('v32 · 후보30','v33 · 후보31').replace('</nav>','<a href="candidate31.html">후보31 · 공간 깊이</a></nav>');p.write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='pending'),indent=2));print('BOOK33',refs)
