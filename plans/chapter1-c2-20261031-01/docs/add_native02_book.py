"""Add native candidate02 evidence without overwriting candidate01 records."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path('C:/Project/d2r-combat-baseline')
C2=ROOT/'plans/chapter1-c2-20261031-01'
DIST=C2/'book-v02/dist'
runtime=DIST/'runtime'
proof=C2/'package-candidate02'
native=ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-02/qa-captures/root-native02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for source,target in [(proof/'build.json',runtime/'build02.json'),(proof/'DELTA-REVIEW.ko.md',runtime/'DELTA-REVIEW02.ko.md'),(ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-02/RUN.ko.md',runtime/'RUN02.ko.md'),(C2/'verification-view-02/REPORT.ko.md',runtime/'VIEW02-INDEPENDENT-REPORT.ko.md')]:
    assert not target.exists(),target
    shutil.copy2(source,target)
items=[
 ('state-0001-run-000-menu.png','시작 기술 3개'),
 ('state-0003-run-001-choice.png','성장 3지선다'),
 ('state-0016-run-001-inventory.png','실제 장비 비교·장착'),
 ('run-001-frame-040.png','직접 조작 전투 · 약40초'),
 ('state-0031-run-001-defeat.png','실제 패배 · 생명력0'),
 ('state-0033-run-002-paused.png','재도전 뒤 초기화·정지')
]
new=[]
for name,title in items:
    target=runtime/('native02-'+name)
    assert not target.exists(),target
    shutil.copy2(native/name,target)
    new.append({'at':'직접 입력','title':title,'image':'runtime/'+target.name,'sha256':sha(target),'note':'1440×810 · 부모 OS 입력 · EXE 후보02 / 코어03 · 상태/시간별 자동 원본PNG'})
d=json.loads((DIST/'content.json').read_text(encoding='utf-8'))
d['runtimeGallery']=new+d['runtimeGallery']
for p in d['pages']:
    if p['id']=='gallery':
        p['subtitle']='최신 EXE 후보02 직접 조작과 보존 후보06/EXE01'
        p['lead']='처음 여섯 장은 코어03을 포함한 EXE 후보02를 부모가 OS 입력으로 직접 조작한 원본 상태/시간 캡처입니다. 뒤의 후보06·EXE01 자동 일반 입력 표본은 각기 따로 표시합니다. 연속 타격감·실제 음향·최종 품질을 이 정지 이미지로 승인하지 않습니다.'
        p['bullets'].append('후보02 직접 조작: 이동·성장/진화·4슬롯 중 무기/부적 장착·정지·실제 패배·재도전 확인. 실제 OS 정예 승리·실청취·WASD hold·별도 초점상실은 미검수입니다.')
    if p['id']=='c2':
        p['table']['rows'].append(['현재 EXE 후보02','논리키 우선·같은tick 종료HUD·실행별 캡처 수정 / source42·PCK78','부모 OS 입력: 성장·장비·정지·패배HP0·재도전 확인; OS 정예 승리는 미검수'])
        p['bullets'].append('현재 별도 실행본은 후보02입니다. 실제 OS 입력으로 성장·장비·정지·패배·재도전을 확인했습니다. 후보01 자동 승리·성능은01의 근거로 유지합니다.')
(DIST/'content.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DIST/'content.js').write_text('window.BOOK_DATA = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
app=(DIST/'app.js').read_text(encoding='utf-8')
app=app.replace('src="runtime/frame-075.png" alt="C2 후보06 실제1920×1080 정예전"','src="runtime/native02-run-001-frame-040.png" alt="최신 EXE 후보02 실제1440×810 직접 조작 전투"')
app=app.replace('현재 후보06 표본이며 최종 패키지03과 다릅니다. 이 정지 화면은 SACRATA 목표 품질·연속 타격감·음향 승인이 아닙니다.','최신 패키지 후보02의 직접 조작 전투 표본입니다. 코어03을 포함하며 최종 품질 승인이 아닙니다. 후보06 소스 실행 표본과 패키지 후보01은 실행 갤러리에 별도 보존합니다.')
app=app.replace('<h3>${esc(g.at)}초 실행 표본</h3>','<h3>${esc(g.title || String(g.at)+\'초 실행 표본\')}</h3>')
app=app.replace("if (p.id === 'c2') content += section('실행본과 원시 검증 기록',`<p>","if (p.id === 'c2') content += section('실행본과 원시 검증 기록',`<p><a href=\"runtime/RUN02.ko.md\">최신 후보02 조작·범위</a> · <a href=\"runtime/build02.json\">후보02 EXE SHA256</a> · <a href=\"runtime/DELTA-REVIEW02.ko.md\">01→02 변경 검토</a> · <a href=\"runtime/VIEW02-INDEPENDENT-REPORT.ko.md\">뷰 독립 검증</a></p><p>보존 후보01: ")
(DIST/'app.js').write_text(app,encoding='utf-8')
print(json.dumps({'gallery':len(d['runtimeGallery']),'current_package':json.loads((runtime/'build02.json').read_text())['sha256']}))
