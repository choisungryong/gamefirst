from pathlib import Path
import json,shutil,re,os,html
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OLD=B/'full21/book-v15/dist';BOOK=B/'full22/book-v16/dist';assert not BOOK.exists();shutil.copytree(OLD,BOOK)
rel=lambda p:os.path.relpath(p,BOOK).replace('\\','/')
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
build=read(B/'full22/build/build.json');assert read(B/'full22/runtime/visual01/RESULT.json')['same_complete_core']
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def repair(m):
  prefix,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');target=(OLD/raw).resolve()
  if not target.is_relative_to(OLD.resolve()):v=rel(target)+(sep+anchor if sep else '')
  return prefix+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',repair,s).replace('제작 도감 v15','제작 도감 v16').replace('후보21 / 이전 항목은 본문 번호 유지','후보22 / 이전 항목은 본문 번호 유지')
 s=s.replace('</nav>','<a href="space22.html">석조 공간22</a></nav>')
 if p.name=='hostile22.html':s=s.replace('제품은 후보21 그대로이며22는 미패키징 연구입니다.','해당 연구를 후보22에 통합했습니다. 이 페이지의 전후 그림은 당시 연구 장면입니다.')
 p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate21.html')
for name,source in {'space22-before.png':B/'space22/compare02/shots/18-zone2-z-17.png','space22-after.png':B/'space22/compare04/shots/22-zone2-z-17.png','space22-garden.png':B/'space22/compare04/shots/22-zone0-z-17.png','space22-battle.png':B/'full22/runtime/visual01/captures/live-3.0.png'}.items():shutil.copy2(source,BOOK/'scenes'/name)
shell=(BOOK/'roles21.html').read_text(encoding='utf-8')
def fig(name,caption):return '<figure><img loading="lazy" src="scenes/'+name+'" alt="'+html.escape(caption)+'"><figcaption>'+caption+'</figcaption></figure>'
def page(name,title,body):
 s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell);s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S).replace(' aria-current="page"','');s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1);(BOOK/(name+'.html')).write_text(s,encoding='utf-8')
page('index','전투 뒤로 이어지는 석조 회랑',
 '<p class="lead">두께가 있는 아치와 무너진 돌 사이로 세 구역의 배경을 구분하고, 날아오는 적 탄환은 밝은 중심과 꼬리로 읽습니다.</p>'
 +fig('space22-after.png','성소 외곽의 실제 두께 석조 아치. 이 그림은 배우 없는 고정 카메라 배경 연구이며 실제 플레이 화면이 아닙니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">개발 후보22 실행 파일</a><a href="space22.html">공간의 전후 비교</a><a href="hostile22.html">적 탄환 개선</a><a href="candidate21.html">이전21 표지</a></div>'
 +'<p>앞뜰은 중앙이 무너진 아치, 예배당은 한쪽이 끊긴 아치, 성소는 온전한 아치를 사용합니다. 새 구조물은 이동 영역 밖에 놓고 기존 전투·성장·조작은 유지했습니다.</p>'
 +'<p class="note">첫 장 품질은 진행 중입니다. 수동 전체·실청취·기본 저장 경로·최종1080p3회 검수가 남았고, 넓은 중앙 공간과 하단 안내의 줄바꿈도 개선할 여지가 있습니다. 기술 통과와 부분 재생을 완성 판정으로 쓰지 않습니다.</p>'
 +'<p>WASD/좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지. 별도 Quality22 저장 경로이며 기존 후보와 저장을 보존합니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('space22','배경 구조에 두께와 빈 공간 더하기',
 '<p class="lead">그림의 윤곽 뒤로 실제 석재 면과 그림자가 이어지도록 배경을 바꿨습니다.</p><div class="columns">'
 +fig('space22-before.png','전18: 성소의 평면 아치와 반복 기초석. compare02의 기존 기준 화면을 재사용했습니다.')
 +fig('space22-after.png','후22: 실제 두께·열린 아치·석재 면·그림자. 동일 카메라의 배경 전용 시안이며 배우와 플레이는 없습니다.')+'</div>'
 +fig('space22-garden.png','앞뜰은 아치 중앙을 무너뜨려 성소와 다른 보존 상태를 보여줍니다. 새 석재206개는 모두 합법 이동 영역 밖에 있습니다.')
 +'<p>정적 배치2개로 새 석재를 묶고 기존 북쪽 기초석의 중복을 제거했습니다. 새 메시와 배치는 자체 코드이며 기존 바닥 이미지를 재질로 재사용했습니다. 초기02·03은 기술 통과 뒤에도 어두운 면·중복 배치·뒤집힌 앞면 때문에 화면 실패로 기록했습니다.04에서 바깥 법선과 시계방향 앞면을 맞췄고 세 구역·두 위치의6개 화면을 직접 확인했습니다.</p>'
 +'<h2>실제 패키지의 전투와 구분하기</h2>'+fig('space22-battle.png','실제 후보22 EXE의 후반 파쇄·적 탄환 장면. 정상 획득 빌드16000tick을 재구성한 뒤6sim초를 재생했습니다. 이 카메라에서는 북쪽 아치의 자세한 형태를 검수하지 않습니다.')
 +'<p>실제 EXE의 World22/FX22 로딩, 원시 로그 오류0, 독립 정상 정책과 종료 전체 전투 상태 동일을 확인했습니다. 소스 GPU도16000→16600tick 부분 재생을 검수했습니다.30sim초 headless는21과10개 상태가 같고 독립 보존 감사30개가 통과했습니다. 전체 수동·음향·저장 지속성·최종 성능 승인은 별도입니다.</p>'
 +'<p>다음은 회피·회복약 안내의 부자연스러운 줄바꿈과 중앙 공간 구성을 개선하고 실제 전체 조작 검수를 이어가는 것입니다.</p><p>'
 +' · '.join('<a href="'+rel(B/p)+'">'+t+'</a>' for p,t in [('space22/REVIEW.ko.md','실패와 수정 기록'),('space22/compare04/RESULT.json','배경 원시 결과'),('full22/runtime/visual01/RESULT.json','실제 EXE 부분 재생'),('full22/independent-audit01/RESULT.json','30개 보존 감사'),('full22/STATUS.ko.md','현재 상태')])+'</p>')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs.append([p.name,v])
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
(BOOK.parent/'BUILD.json').write_text(json.dumps({'html':len(list(BOOK.glob('*.html'))),'references':len(refs),'missing':missing,'browser_review':'pending'},ensure_ascii=False,indent=2),encoding='utf-8');assert not missing,missing
print({'html':len(list(BOOK.glob('*.html'))),'refs':len(refs),'missing':len(missing)},flush=True)
