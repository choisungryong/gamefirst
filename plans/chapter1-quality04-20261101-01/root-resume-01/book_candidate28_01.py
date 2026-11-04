from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';old=B/'full27/book-v26/dist';book=B/'full28/book-v27/dist';assert not book.exists();shutil.copytree(old,book)
rel=lambda p:os.path.relpath(p,book).replace('\\','/')
for p in book.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v26 · 후보27','v27 · 후보28').replace('</nav>','<a href="candidate28.html">현재 후보28 · 피격과 공격 방향</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="candidate28.html">현재 후보28: 피격 반동과 공격 회복 방향 개선</a></p>',1)
 p.write_text(s,encoding='utf-8')
for source,dest in [('actor28/mapped02/25b/attack-070.png','recover28-before.png'),('actor28/mapped02/28/attack-070.png','recover28-after.png'),('actor28/mapped02/25b/attack.mp4','recover28-before.mp4'),('actor28/mapped02/28/attack.mp4','recover28-after.mp4'),('actor28/mapped02/28/normal.mp4','normal28-mapped.mp4'),('full28/runtime/hit01/proof/after.png','actual28-after.png')]:shutil.copy2(B/source,book/'scenes'/dest)
body='''<h1>후보28 · 피격 반동과 공격 방향</h1><p class="lead">맞은 몸의 반동을 더 분명하게 만들고,공격이 끝날 때까지 몸이 공격 방향을 유지하게 했습니다.</p><h2>공격 후 엉뚱한 방향으로 돌아서던 표시 수정</h2><figure><img src="scenes/recover28-before.png" alt="공격 후 회복 중 오래된 이동 방향으로 돌아선 이전 표시"><figcaption>같은4역할·시점의이전Actor25b입니다. 회복중이동방향과공격방향이다른조건을명시적으로구성했습니다.</figcaption></figure><figure><img src="scenes/recover28-after.png" alt="회복 중 지불된 공격 방향을 유지하는 후보28"><figcaption>같은조건의Actor28. 공격예고방향은같고,회복구간에는실제공격방향을유지합니다. 피해판정·공격시간·이동규칙은변경하지않았습니다.</figcaption></figure><h2>프레임과 게임 틱이 대응하는 연속 기록</h2><p>아래공격전후영상은각180연속프레임/60fps/3초입니다. 정상전투120프레임까지합친각300개프레임의phase·번호·게임틱·전체core해시가모두같습니다. 시작·종료대기프레임을임의로잘라맞춘영상이아닙니다. PNG원본을각각직접기록해순서대로인코딩했습니다.</p><video controls preload="metadata" style="width:100%" src="scenes/recover28-before.mp4"></video><p>이전표시:회복중오래된이동방향으로돌아섭니다.</p><video controls preload="metadata" style="width:100%" src="scenes/recover28-after.mp4"></video><p>새표시:회복중공격방향유지. 네역할각하나씩서로다른방향을바라보는복제표시fixture입니다. 모든역할의모든방향조합을전부검수했다는뜻은아닙니다.</p><h2>피격 반동과 실제 제품</h2><video controls preload="metadata" style="width:100%" src="scenes/normal28-mapped.mp4"></video><p>정상획득화염16001→16120tick의연속120프레임/60fps/2초source기록입니다. 상체9bone의짧은피격동작과흉곽반동을혼합하고,다리로컬포즈·공격우선순위·빙결/메뉴정지는유지합니다. 무음이며실시간성능·수동플레이증거와구분합니다.</p><figure><img src="scenes/actual28-after.png" alt="실제 후보28 EXE의 정상 성장 전투 화면"><figcaption>실제후보28EXE/PCK에서정상획득체크포인트후원래정책·controller로진행한화면입니다.</figcaption></figure><h2>채택 근거와 남은 검수</h2><p>47동작검사,프레임별core동일,네방향회복검사,실제EXE의피격발생·독립전체core동일·오류없는종료를확인했습니다. 같은구간CPU배우처리평균은1.872→1.961ms,추가약0.089ms였습니다. 현재28은새Actor만추가하고HUD27/World22/FX26와규칙은유지합니다. 바닥27시안은미채택입니다.</p><p>첫mapped01은검사용이벤트kind필드누락으로실패했고원시자료를보존했습니다. mapped02는새경로에서보완한성공자료입니다. 이전MovieMaker프레임차이·초기누수경고·결과파일재기록실수도지우지않았습니다. 수동전체·실청취·동일최종제품대표성능3회·공간과전투최종질감승인은아직남아있습니다.</p>'''
body+='<p>'+' · '.join(f'<a href="{rel(B/p)}">{label}</a>' for p,label in [('full28/STATUS.ko.md','현재 상태'),('full28/build/build.json','제품 고정'),('actor28/mapped02/COMPARISON.json','프레임별 상태 비교'),('actor28/mapped02/FACING-AUDIT01.json','공격 방향 검사'),('full28/runtime/hit01/proof/RESULT.json','실제 제품 기록'),('full28/independent-audit01/RESULT.json','독립 보존 감사')])+'</p>'
s=(book/'candidate27.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>후보28 피격과 공격 방향 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(book/'candidate28.html').write_text(s,encoding='utf-8')
refs=0;missing=[]
for p in book.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(book.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(book.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),indent=2));assert not missing;print('BOOK27',refs,'refs missing0')
