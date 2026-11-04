"""Add actual packaged-run evidence to the unfrozen v02 working book."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path('C:/Project/d2r-combat-baseline')
C2=ROOT/'plans/chapter1-c2-20261031-01'
DIST=C2/'book-v02/dist'
proof=C2/'package-candidate01'
runtime=DIST/'runtime'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['build.json','PACKAGING-REPORT.ko.md','packaged-runtime-summary.json']:
    target=runtime/name
    assert not target.exists(),target
    shutil.copy2(proof/name,target)
shutil.copy2(C2/'verification-core-03/REPORT.ko.md',runtime/'CORE03-INDEPENDENT-REPORT.ko.md')
shutil.copy2(ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-01/RUN.ko.md',runtime/'RUN.ko.md')
d=json.loads((DIST/'content.json').read_text(encoding='utf-8'))
for g in d['runtimeGallery']:
    g['note']='1920×1080 · 후보06 · 일반 입력 자동 플레이 · 코어02'
for at in [5,20,60,75]:
    src=ROOT/f'builds/chapter1/chapter1-c2-candidate-20261031-01/qa-captures/package-pilot01/frame-{at:03d}.png'
    target=runtime/f'package-frame-{at:03d}.png'
    if src.exists():
        assert not target.exists(),target
        shutil.copy2(src,target)
        d['runtimeGallery'].append({'at':at,'image':'runtime/'+target.name,'sha256':sha(target),'note':'1920×1080 · 실제 EXE 후보01 · 일반 입력 자동 플레이 · 코어03'})
for p in d['pages']:
    if p['id']=='gallery':
        p['subtitle']='후보06과 실제 EXE 후보01 ·1920×1080'
        p['lead']='코어02 화면 후보06과 코어03을 내보낸 실제 EXE 후보01의 원본 실행 표본입니다. 장면별 표기를 확인하세요. 정지 이미지와 자동 플레이는 연속 타격감·실제 음향·직접 조작 승인을 대신하지 않습니다.'
        p['bullets'].append('EXE 후보01도78.15초 실제 정예 처치 승리/813처치/3기술 명중을 기록했습니다. PNG raw fallback0으로 실제 가져온 텍스처를 확인했습니다.')
    if p['id']=='c2':
        p['table']['rows'][0][2]='독립 경계114검사 actual0 ·9pin 전후 일치'
        p['table']['rows'].insert(3,['별도 실행본 후보01','source42 / PCK78 / import·export·실제 실행 actual0','자동 일반 입력 승리78.15초·813처치; 직접 조작은 별도 기록'])
(DIST/'content.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DIST/'content.js').write_text('window.BOOK_DATA = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
app=(DIST/'app.js').read_text(encoding='utf-8')
app=app.replace('1920×1080 · 일반 입력 자동 플레이 · 코어02</p>','${esc(g.note)}</p>')
needle="    if (p.id === 'gallery') content += section("
pos=app.index(needle)
app=app[:pos]+'''    if (p.id === 'c2') content += section('실행본과 원시 검증 기록',`<p><a href="runtime/RUN.ko.md">조작·범위</a> · <a href="runtime/build.json">EXE SHA256·42source/78PCK</a> · <a href="runtime/PACKAGING-REPORT.ko.md">패키지 검증</a> · <a href="runtime/packaged-runtime-summary.json">실제 EXE 실행 수치</a> · <a href="runtime/CORE03-INDEPENDENT-REPORT.ko.md">코어03 독립 검증</a></p><p>EXE는 별도 전달하는 AshenCloister-Chapter1.exe입니다. 도감 ZIP에 실행 파일을 중복 포함하지 않습니다.</p>`);
''' +app[pos:]
(DIST/'app.js').write_text(app,encoding='utf-8')
print(json.dumps({'runtime_gallery':len(d['runtimeGallery']),'package_exe_sha256':json.loads((runtime/'build.json').read_text())['sha256']}))
