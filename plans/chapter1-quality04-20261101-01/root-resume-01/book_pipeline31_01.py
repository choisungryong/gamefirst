from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';old=B/'full29/book-v30/dist';new=B/'full30/book-v31/dist';assert not new.exists();shutil.copytree(old,new);rel=lambda p:os.path.relpath(p,new).replace('\\','/')
for p in new.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,a=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=rel(t)+(sep+a if sep else '')
  return k+'="'+v+'"'
 s=re.sub(r'(src|href)="([^"]+)"',fix,s).replace('v30 · 후보29','v31 · 후보30').replace('</nav>','<a href="candidate30.html">후보30</a><a href="workbench/index.html">캐릭터 동작 작업대</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="workbench/index.html">캐릭터 동작 작업대 열기 · PNG 등록과 프레임 연결</a></p><p><a href="candidate30.html">현재 후보30 · 실제 패키지 검수</a></p>',1)
 p.write_text(s,encoding='utf-8')
body='<h1>후보30 · 무리의 체형</h1><p class="lead">역할별 네 가지 체형 비율을 실제 제품에 연결했습니다. 기존 후보29와 사용자 저장은 보존했습니다.</p>'
for f,caption in [('full30/runtime/silhouette01/proof/after.png','초반 실제 제품 · 발견 카드와 일반 적 체형'),('full30/runtime/late-cold01/proof/after.png','후반 실제 제품 · 보스 위험원과 냉기 전투')]:body+=f'<figure><img src="{rel(B/f)}" alt="{caption}"><figcaption>{caption}</figcaption></figure>'
body+='<p>새로운 몬스터 종을 만든 변화는 아닙니다. 같은 계열의 머리·어깨·팔·키 비율을 달리해 무리 외곽의 반복을 조금 줄였습니다. 현재 공격·피격·냉기·그림자와 공유 풀을 유지합니다.</p><p>실제 후반 냉기19800→20400tick에 정상 획득 상태와 원래 controller로 진행했고, 독립 게임 상태와 같았습니다. 12체형/역할 조합이 실제 등장했고, 피격 혼합508회·224생성·그림자224ON/실제1920×1080/오류없는 종료를 확인했습니다. 전체 수동 완주·실청취·최종 성능 승인과는 별개입니다.</p><p>첫 초반 검사에서는 짧은 구간에12조합을 모두 요구한 관찰 조건 때문에 실패했습니다. 실제11조합이 나타났고 원시 실패를 보존했습니다. 후반 검사는 별도 구간·냉기 검증입니다.</p><h2>다음 캐릭터를 위한 작업대</h2><p><a href="workbench/index.html">캐릭터 동작 작업대 열기</a></p><p>보존된 주인공과 네 몹의 스프라이트로 프레임 등록·발 기준·방향·동작을 확인할 수 있습니다. 새 PNG는 행 배치를 지정해 등록 설정을 저장합니다. 같은 설정을 Godot 표시기가 읽는 첫 파이프라인이며, 현재3D제품을 자동 교체하지 않습니다.</p>'
body+='<p>'+ ' · '.join(f'<a href="{rel(B/f)}">{label}</a>' for f,label in [('full30/STATUS.ko.md','현재 상태'),('full30/build/build.json','제품 고정'),('sprite-pipeline01/COMPILER-RESULT.json','등록 검사'),('sprite-pipeline01/engine01/sprite-pipeline-gpu-result.json','Godot 표시 검사')])+'</p>'
s=(new/'candidate29.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>후보30과 캐릭터 작업대 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(new/'candidate30.html').write_text(s,encoding='utf-8')
work=new/'workbench';work.mkdir()
for name in ['index.html','workbench.css','workbench.js']:shutil.copy2(R/'tools/sprite_pipeline'/name,work/name)
catalog=[]
for role,label in [('hero','주인공'),('walker','일반 적'),('ranged','원거리 적'),('charger','돌진 적'),('elite','정예')]:catalog.append(dict(label=label+' · 보존 스프라이트',actor=os.path.relpath(B/f'sprite-pipeline01/assets/{role}-demo/actor.json',work).replace('\\','/')))
(work/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
missing=[];refs=0
for p in new.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(new)),v])
assert not missing,missing
(new.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(new.rglob('*.html'))),references=refs,missing=missing,catalog_entries=len(catalog),browser_review='pending'),indent=2));print('BOOK31',refs,'references, missing0')
