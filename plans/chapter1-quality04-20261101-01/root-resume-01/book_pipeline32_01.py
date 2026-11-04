from pathlib import Path
import json,re,os,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';old=B/'full30/book-v31/dist';new=B/'full30/book-v32/dist';assert not new.exists();shutil.copytree(old,new);rel=lambda p:os.path.relpath(p,new).replace('\\','/')
for p in new.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('v31 · 후보30','v32 · 후보30').replace('</nav>','<a href="sprite-roles.html">등록 캐릭터 전투 연결</a></nav>')
 if p.name=='index.html':s=s.replace('<main>','<main><p><a href="sprite-roles.html">등록 캐릭터를 전투 역할에 연결하기</a></p>',1)
 p.write_text(s,encoding='utf-8')
work=new/'workbench'
for name in ['index.html','workbench.js','workbench.css']:shutil.copy2(R/'tools/sprite_pipeline'/name,work/name)
body='<h1>등록 캐릭터를 전투 역할에 연결하기</h1><p class="lead">에셋북에서 고른 외형을 기존 역할에 연결하고, 같은 제1장 전투로 확인합니다.</p><p><a href="workbench/index.html">캐릭터 동작 작업대 열기</a></p><h2>일반 적만 선택</h2>'
for f,caption in [('sprite-slots03/gpu-walker/after.png','일반 적만 보존 스프라이트로 표시 · 주인공과 다른 역할은 기존3D'),('sprite-slots04/gpu-all/after.png','주인공과 네 몹 역할을 선택한 미리보기 · 최종 보스는 기존3D 유지')]:body+=f'<figure><img src="{rel(B/f)}" alt="{caption}"><figcaption>{caption}</figcaption></figure>'
body+='<p>정상 냉기 성장2800tick 체크포인트에서 원래 정책과 controller로3400tick까지 진행했습니다. 두 선택 모두 독립 게임 상태가 같고 선택한 역할만 바뀌었습니다. 첫 화면은 상세 진단 모드의 GPU 경고가 기록된 실행이며, 두 번째 전체 역할 실행은 오류 없이 종료했습니다.</p><h2>등록에서 전투까지</h2><ol><li>작업대에서 PNG와 동작 배치를 연결하고 등록 설정을 저장합니다.</li><li>설정을 컴파일하면 actor.json·PNG·manifest.json이 새 폴더에 생깁니다.</li><li>작업대에서 actor.json과 PNG를 함께 불러옵니다. 공격 타격 프레임을 지정하고 역할 설정을 저장합니다.</li><li>별도 전투 미리보기 실행기에 역할 설정을 전달합니다. 메뉴에서 플레이하거나 정상 정책으로 짧게 확인할 수 있습니다.</li></ol><p>공격·피격·사망이 없는 에셋은 기본 전투 연결을 거부합니다. 없는 포즈나 새 AI를 자동 생성하지 않습니다. 기존 유형의 능력치·공격 규칙·드롭은 유지하며, 현재 제품30과 저장 파일을 교체하지 않습니다.</p><p>현재 연결기는 숨긴3D 리그를 호환용으로 유지하는 프로토타입입니다. 스프라이트 전용 성능 최적화나 모든 방향 공격 포즈의 품질 승인은 남아 있습니다.</p><h2>실패도 함께 보존</h2><p>첫 headless 실행은 기능 검사7개가 같아도 종료 누수 경고 때문에 실패로 보존했습니다. 별도 상세 진단에서는 재현되지 않았고, 명시적 공유 캐시 정리를 추가했습니다. 상세 GPU 진단에는 Vulkan 레이어 조회·RGB8 변환 경고가 있어 조용한 성공으로 바꾸지 않았습니다. 실제 전체 역할 GPU의 종료오류0과 별도로 기록합니다.</p>'
body+='<p>'+' · '.join(f'<a href="{rel(p)}">{label}</a>' for p,label in [(R/'tools/sprite_pipeline/README.ko.md','등록·전투 실행 방법'),(B/'sprite-slots04/gpu-all/RESULT.json','전체 역할 실제 결과'),(B/'sprite-slots03/gpu-walker/RESULT.json','일반 적 선택 결과'),(B/'sprite-slots01/FAILURE.json','첫 경고 보존')])+'</p>'
s=(new/'candidate30.html').read_text(encoding='utf-8');s=re.sub(r'<title>.*?</title>','<title>등록 캐릭터 전투 연결 · 잿빛 회랑 도감</title>',s);s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',s,flags=re.S);(new/'sprite-roles.html').write_text(s,encoding='utf-8')
missing=[];refs=0
for p in new.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(new)),v])
assert not missing,missing
(new.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(new.rglob('*.html'))),references=refs,missing=missing,browser_review='pending'),indent=2));print('BOOK32',refs,'references missing0')
