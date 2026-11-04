"""Create a new C2 book; v01 and historical documents stay byte-preserved."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path('C:/Project/d2r-combat-baseline')
C2 = ROOT/'plans/chapter1-c2-20261031-01'
OLD = ROOT/'plans/chapter1-preproduction-20261031-01/book/dist'
BOOK = C2/'book-v02'
DIST = BOOK/'dist'
BACKUP = Path('C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

assert not BOOK.exists(), 'New book ID required; preserve existing outputs'
assert not BACKUP.exists(), 'New backup ID required'
BACKUP.mkdir(parents=True)
docs = ['HANDOFF.md','IMPLEMENTATION-STATUS.ko.md']
for name in docs: shutil.copy2(ROOT/name, BACKUP/name)
old_files = {str(p.relative_to(OLD)).replace('\\','/'):sha(p) for p in OLD.rglob('*') if p.is_file()}
zip_v01 = ROOT/'plans/chapter1-preproduction-20261031-01/CHAPTER1-PRODUCTION-BOOK-20261031-01.zip'
write_json(BACKUP/'manifest.json', {'documents':{n:sha(ROOT/n) for n in docs},'book_v01':old_files,'book_v01_zip_sha256':sha(zip_v01) if zip_v01.exists() else None})
shutil.copytree(OLD,DIST)
(BOOK/'.gdignore').write_text('',encoding='utf-8')
runtime = DIST/'runtime'
runtime.mkdir()
art = runtime/'art'
art.mkdir()
ledger = json.loads((ROOT/'chapter1/art/ASSET-LEDGER.json').read_text(encoding='utf-8'))
for asset in ledger['assets']:
    src=ROOT/asset['path']
    shutil.copy2(src,art/src.name)
for name in ['ASSET-LEDGER.json','README.ko.md']:
    shutil.copy2(ROOT/'chapter1/art'/name,art/name)
for role in ['hero','walker','ranged','charger','elite']:
    shutil.copy2(ROOT/f'chapter1/art/actors/{role}.json',art/f'{role}.json')
shutil.copy2(C2/'art/ART-SUPPLY-REPORT.ko.md',runtime/'ART-SUPPLY-REPORT.ko.md')
gallery=[]
for at,label in [(5,'初期攻撃'),(20,'成長中の群衆戦'),(60,'進化・三技術'),(75,'正銳戦')]:
    src=C2/f'view-candidate06/frame-{at:03d}.png'
    if src.exists():
        target=runtime/src.name
        shutil.copy2(src,target)
        gallery.append({'at':at,'image':f'runtime/{target.name}','sha256':sha(target)})

d=json.loads((DIST/'content.json').read_text(encoding='utf-8'))
d['version']='0.2-c2-candidate'
d['status']='C2 실행 후보 통합 · 품질 관문 열림'
d['runtimeGallery']=gallery
d['runtimeArt']=[{'name':Path(a['path']).name,'image':'runtime/art/'+Path(a['path']).name,'sha256':a['sha256'],'status':a['status'],'format':a['format']} for a in ledger['assets']]
d['pages'].insert(1,{'id':'c2','short':'현재 C2 구현','title':'실제로 연결된 첫 전투','subtitle':'5–8분 1장을 향한 대표90초 후보','lead':'자동 공격·XP 선택·스킬 진화·장비 획득과 비교·정예 처치를 같은 실행 화면으로 통합했습니다. 1장 전체와 SACRATA 목표 품질은 아직 미완료입니다.','bullets':['화염·냉기·번개 중 시작 기술을 고르고, 각자 쿨다운으로 자동 시전되는 세 기술을 성장시킵니다.','추격·원거리·돌진 적과 회랑 수호자를 상대합니다. 70초 정예 등장 뒤 실제 처치가 승리 조건이며 시간만으로 승리하지 않습니다.','무기·갑옷·부적·반지 네 슬롯을 실제 드롭으로 얻어 비교·장착합니다. 주인공 체력을 장착으로 회복하지 않습니다.','소지품 일반64칸과 정예 목표 보상 전용1칸으로 총65개를 제한하며 기존 장비를 교체·삭제하지 않습니다.','새 실행은 기존 사용자 저장을 읽거나 변경하지 않습니다. C2 자체 저장 기능도 아직 없습니다.'],'media':[],'assets':['GR-001','SK-001','SK-002','SK-003','IT-001','IT-002','IT-003','IT-004'],'table':{'heads':['확인 범위','현재 결과','남은 검수'],'rows':[['코어03','기능75검사 actual0 / 의도 실패76검사 actual1','독립03 검증 결과 별도 기록'],['일반 입력 자동 플레이','6회 중5승 / 냉기 seed71은64.9초 패배','자동 입력은 손맛·난도 승인 대체 불가'],['1080p 화면 후보06','78.15초 정예 처치 /813처치, p95 약20ms','측정 교란 포함·정식 성능 통과 아님'],['표현','독자 생성2.5D PNG와3D 바닥·shader 효과','리깅3D 아님; 방향별 행동·소품·음향·연속 장면 검수 필요'],['1장 전체','아직 제작 중','연결3구역·이벤트·1장 보스·보상 보존·5–8분 전체 흐름']]}})
d['pages'].insert(2,{'id':'gallery','short':'실행 화면','title':'실행 후보의 실제 화면','subtitle':'자동 일반 입력 ·1920×1080 · 후보06','lead':'새 캐릭터와 적·군중·효과가 함께 실행된 표본입니다. 이 장면의 코어는02이며 최종 패키지03과 다릅니다. 정지 이미지와 자동 플레이는 연속 타격감·실제 음향·직접 조작 승인을 대신하지 않습니다.','bullets':['캡처는 원본 PNG를 복사했으며 크롭·후처리하지 않았습니다.','후보06은78.15초 실제 정예 처치 승리,813처치,3기술 시전/명중이 기록됐습니다.','반복 바닥·삼각 잔디·기하 소품과 군중 겹침은 확인된 표현 한계입니다.'], 'media':[],'assets':[]})
d['pages'].insert(3,{'id':'production-art','short':'실제 아트 원장','title':'현재 제작한 아트','subtitle':'독립 생성2.5D PNG · 발 기준점·가변 사각형 JSON','lead':'주인공·일반 적3종·정예를 생성하고 실제 실행에 통합했습니다. 계획상의 리깅3D 모델 제작과 동일한 결과로 기록하지 않습니다.','bullets':['각 역할은 이동4방향×4키프레임과 남쪽 공격/시전·피격·사망 각4키프레임을 갖습니다.','전용 idle과 남쪽 외 행동은 미제작입니다. 현재 대기는 이동 키프레임을 유지합니다.','PNG12개에는 런타임11개와 초기 주인공 시트 증거1개가 포함됩니다. 초기 시트는 최종 실행에 사용하지 않습니다.','원본 생성 경로·프롬프트·크기·SHA256은 원장을 따릅니다. CC0 또는 제3자 라이선스 모델로 표기하지 않습니다.'], 'media':[],'assets':['CH-001','AN-001','EN-001','EN-002','EN-003']})
for p in d['pages']:
    if p['id']=='index':
        p['subtitle']='사양0.2 · C2 실행 후보 통합'
        p['lead']='SACRATA의 표현·군중 전투와 디아블로식 장비·스킬 성장을 목표로 하는 제작 도감입니다. 현재 실행 후보의 기능·아트와 남은 품질 차이를 새 페이지에 연결했습니다.'
        p['bullets'].insert(0,'현재 C2 구현·실행 화면·실제 아트 원장 페이지를 먼저 확인하세요. 과거 기술 통과는 최종 품질 승인이 아닙니다.')
    if p['id']=='roadmap':
        p['lead']='별도 chapter1 경로에 대표 전투를 통합했습니다. C2 품질 관문은 열려 있으며 같은 품질의5–8분 1장 전체로 확대하기 전에 현재 가독성·표현·기능 결함을 해결합니다.'
        p['bullets']=['C2: 현재 구현 페이지와 실제 실행본·코어03 증거를 함께 검수합니다.','C2 품질 미달: 환경 소품·애니메이션·효과·음향·직접 입력·성능을 개선합니다.','C3–C4: 연결 구역·이벤트·정예 변형·1장 보스·보상 보존과 재도전을 통합합니다.','C5:5–8분 전체 실제 플레이·3빌드·새 제품의 성능·보존·청취를 검수합니다.','1장 품질 검수 전2·3장을 확장하지 않습니다.']

updates={
'CH-001':('2.5D 후보 통합·검수 중','주인공 PNG+JSON을 실제 화면에 통합했습니다. 성인 비율 다크 판타지 후보이며 리깅GLB는 아닙니다.','PNG 스프라이트+발 기준점JSON','runtime/art/hero.json'),
'AN-001':('제한 클립 통합·미완료','이동4방향×4키프레임,남쪽 시전/피격/사망 각4키프레임. 전용 idle·다른 방향 행동은 미제작입니다.','PNG 아틀라스+가변 사각형JSON','runtime/art/hero_actions.png'),
'GR-001':('대표 전투 통합·검수 중','XP 회수·성장3지선다·랭크/패시브/진화가 새 전투와 연결됐습니다.5–8분 전체 성장 곡선은 아직 아닙니다.','GDScript+독립JSON','chapter1/core/run_growth.gd'),
'IT-001':('C2 드롭·비교·장착 통합','C2 무기 균열의 잿불 가지: 피해/발사체 증가. 계획 명칭·최종 base pool과는 별도입니다.','런타임 아이템 사전','chapter1/core/combat_run.gd'),
'IT-002':('C2 드롭·비교·장착 통합','C2 갑옷 수호의 재옷: 최대HP/피해감소. 장착은 현재HP를 회복하지 않습니다.','런타임 아이템 사전','chapter1/core/combat_run.gd'),
'IT-003':('C2 드롭·비교·장착 통합','C2 부적 회수의 재결정: 회수 반경/주기 단축. 최종 장비 pool은 미완료입니다.','런타임 아이템 사전','chapter1/core/combat_run.gd'),
'IT-004':('C2 드롭·비교·장착 통합','C2 반지 갈래 도체 반지: 피해/연쇄/파쇄. 최종 장비 pool은 미완료입니다.','런타임 아이템 사전','chapter1/core/combat_run.gd'),
'LO-001':('C2 보상 연결·범위 제한','사망1회 보상·독립RNG·획득·UID·비교·장착을 연결했습니다. 일반64+목표보상1칸 정책. base12/affix12 최종 pool은 미완료입니다.','런타임 아이템 사전·독립RNG','chapter1/core/combat_run.gd'),
'EN-001':('추격 역할·2.5D 통합','보행 추격·근접 전조/피해·피격/사망 후보가 연결됐습니다.','PNG+JSON+코어 상태','runtime/art/walker.json'),
'EN-002':('원거리 역할·2.5D 통합','사거리·부채꼴 발사 전조·실제 탄·피격/사망 후보가 연결됐습니다.','PNG+JSON+코어 상태','runtime/art/ranged.json'),
'EN-003':('돌진 역할·2.5D 통합','돌진 전조 캡슐·돌진 피해·회복·피격/사망 후보가 연결됐습니다.','PNG+JSON+코어 상태','runtime/art/charger.json'),
'BO-001':('1장 보스 제작 대기','C2 회랑 수호자는 대표 구간의 정예입니다. 이를5–8분 1장 보스와 단계 전환의 완성으로 기록하지 않습니다.','최종 보스 제작 대기',''),
'EV-001':('C2 바닥 후보 통합','독자 생성 바닥PNG를 사용합니다. 반복 패턴·배치·시각적 밀도는 수정 필요입니다.','PNG 알베도+shader','runtime/art/cloister_ground_v01.png'),
'EV-004':('기하 대역·최종 미완료','현재 삼각형 잔디/간단 돌·안개/바닥 표현이 있으며 최종 환경 자산이 아닙니다.','절차 기하 대역','chapter1/view/cloister_world.gd'),
'EV-005':('기하 대역·최종 미완료','현재 기둥·문틀·묘비는 단순 기하입니다. 최종 환경 소품 제작은 남아 있습니다.','절차 기하 대역','chapter1/view/cloister_world.gd'),
'EV-006':('기하 대역·최종 미완료','기하 횃불과 조명 후보를 통합했습니다. 최종 연소 효과·소품·음향 검수는 남았습니다.','기하·광원 후보','chapter1/view/cloister_world.gd'),
'UI-001':('C2 HUD 통합·검수 중','생명력·XP·기술/진화·정예HP·회피 주기 HUD를 연결했습니다. 최종 아이콘·미술은 남았습니다.','Godot Control UI','chapter1/view/cloister_hud.gd'),
'UI-002':('C2 성장 선택 통합','실제 제시 카드·선행 패시브·진화 선택을 전투 정지 상태에서 처리합니다.','Godot Control UI','chapter1/view/cloister_hud.gd'),
'UI-003':('C2 획득·비교·장착 통합','획득 장비를 비교·장착할 수 있습니다. 영구 보관/저장은 아직 없습니다.','Godot Control UI','chapter1/view/cloister_hud.gd'),
'UI-004':('대표 구간 결과·재도전','정예 실제 처치 승리/실제 패배·재도전을 연결했습니다.1장 보스·영구 보상 화면 완성은 아닙니다.','Godot Control UI','chapter1/view/cloister_hud.gd'),
}
for a in d['assets']:
    if a['id'] in updates:
        a['state'],a['existing'],a['format'],a['sourcePath']=updates[a['id']]
        a['revision']='0.2 C2 후보'
    if a['id'] in ['SK-001','SK-002','SK-003']:
        a['state']='C2 실제 시전·성장·진화 통합'
        a['existing']='독립 성장 정의를 실제 자동 시전·피해·투사체/연쇄·진화와 연결했습니다. 최종 시각/음향/밸런스 검수는 남아 있습니다.'
        a['sourcePath']='chapter1/data/growth.json'
    if a['id'].startswith('FX-'):
        a['state']='C2 효과 후보 통합·검수 중'
        a['existing']='실제 코어 사건과 연결한 발사체shader·명중/파쇄/연쇄·XP/장비·전조 표현 후보가 있습니다. 최종 타격감·연속 영상·성능 검수는 남아 있습니다.'
        a['sourcePath']='chapter1/view/cloister_effects.gd'
    if a['id'].startswith('AU-'):
        a['state']='기존 합성음 재사용·최종 미완료'
        a['existing']='기존 독자 합성WAV10개와 bounded 음향 관리자를 연결했습니다. 최종 작곡/녹음·실제 청취·음악 전환은 미완료입니다.'
        a['sourcePath']='assets/expedition/audio/*.wav'
write_json(DIST/'content.json',d)
(DIST/'content.js').write_text('window.BOOK_DATA = '+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

app=(DIST/'app.js').read_text(encoding='utf-8')
app=app.replace("const storageKey = 'chapter1-production-book-notes-v1';","const storageKey = 'chapter1-production-book-notes-v2-c2';")
app=app.replace("${badge('사전 제작 기준선')}","${badge('C2 실행 후보 · 품질 검수 중')}")
start=app.index("    if (p.id === 'index') {")
end=app.index("    content += section(",start)
app=app[:start]+'''    if (p.id === 'index') {
      content += `<div class="comparison"><figure>${figure(obs(p.media[0])).replace(/^<figure[^>]*>|<\\/figure>$/g,'')}</figure><figure class="prototype"><a href="gallery.html"><img src="runtime/frame-075.png" alt="C2 후보06 실제1920×1080 정예전"></a><figcaption>${badge('C2 실제 실행 후보','waiting')}<h3>성장·장비·군중·정예가 연결된 현재 화면</h3><p>현재 후보06 표본이며 최종 패키지03과 다릅니다. 이 정지 화면은 SACRATA 목표 품질·연속 타격감·음향 승인이 아닙니다.</p><a href="c2.html">현재 구현 보기</a> · <a href="gallery.html">실행 화면 보기</a> · <a href="production-art.html">실제 아트 원장</a></figcaption></figure></div>`;
    }
    if (p.id === 'gallery') content += section('원본 실행 캡처',`<div class="reference-grid">${D.runtimeGallery.map(g=>`<figure class="reference"><a href="${esc(g.image)}" target="_blank"><img loading="lazy" src="${esc(g.image)}" alt="후보06 ${esc(g.at)}초 원본 실행 화면"></a><figcaption><h3>${esc(g.at)}초 실행 표본</h3><p>1920×1080 · 일반 입력 자동 플레이 · 코어02</p><small class="hash">SHA256 ${esc(g.sha256)}</small></figcaption></figure>`).join('')}</div>`);
    if (p.id === 'production-art') {
      content += section('출처와 제작 기록',`<p><a href="runtime/art/ASSET-LEDGER.json">전체 프롬프트·생성 원본·해시 JSON</a> · <a href="runtime/art/README.ko.md">형식과 미제작 동작</a> · <a href="runtime/ART-SUPPLY-REPORT.ko.md">제작 보고서</a></p>`);
      content += section('실제 생성 아틀라스',`<div class="reference-grid">${D.runtimeArt.map(a=>`<figure class="reference"><a href="${esc(a.image)}" target="_blank"><img loading="lazy" class="atlas" src="${esc(a.image)}" alt="독립 생성 ${esc(a.name)} 아틀라스"></a><figcaption><h3>${esc(a.name)}</h3><p>${esc(a.format)} · ${esc(a.status)}</p><small class="hash">SHA256 ${esc(a.sha256)}</small></figcaption></figure>`).join('')}</div>`);
    }
''' + app[end:]
start=app.index("    if (p.id === 'roadmap') {")
end=app.index("    if (p.id === 'quality')",start)
app=app[:start]+'''    if (p.id === 'roadmap') {
      content += section('현재 제작 증거',`<p>새 chapter1 경로에서 성장·자동 시전·군중·획득·비교·장착·정예·결과를 연결했습니다. 실제 산출물과 제한은 <a href="c2.html">현재 C2 구현</a>, <a href="gallery.html">실행 화면</a>, <a href="production-art.html">아트 원장</a>에서 확인합니다.</p><p>현재 C2 품질을 통과한 것으로 처리하지 않습니다. 직접 조작·연속 효과·환경 아트·방향별 동작·최종 음향·성능과 전체1장 구현이 남았습니다.</p>`);
    }
''' + app[end:]
(DIST/'app.js').write_text(app,encoding='utf-8')
for p in d['pages']:
    if not (DIST/(p['id']+'.html')).exists():
        base=(DIST/'index.html').read_text(encoding='utf-8')
        base=base.replace('data-page="index"',f'data-page="{p["id"]}"')
        base=base.replace('<title>1장 제작 도감 · 1장 제작 도감</title>',f'<title>{html.escape(p["title"])} · 1장 제작 도감</title>')
        (DIST/(p['id']+'.html')).write_text(base,encoding='utf-8')
for p in DIST.glob('*.html'):
    text=p.read_text(encoding='utf-8').replace('사양 0.1','사양 0.2 · C2 후보').replace('최종 모델·효과·음향의 제작과 품질 검수는 별도입니다.','현재2.5D·효과는 실행 후보이며 최종1장·아트·음향 품질 승인은 남아 있습니다.')
    p.write_text(text,encoding='utf-8')
with (DIST/'style.css').open('a',encoding='utf-8') as f:
    f.write('\n/* C2 production evidence additions. */\n.reference img.atlas{object-fit:contain;background:#142022;max-height:440px}.reference>a{display:block}.reference>a>img{width:100%;height:auto}.hash{display:block;overflow-wrap:anywhere;color:var(--muted)}\n')
write_json(BOOK/'BUILD-INPUTS.json',{'source_book':str(OLD),'source_book_manifest':old_files,'art_ledger_sha256':sha(ROOT/'chapter1/art/ASSET-LEDGER.json'),'gallery':gallery,'scope':'v02 C2 candidate documentation, not visual quality approval'})
print(json.dumps({'book':str(DIST),'pages':len(d['pages']),'assets':len(d['assets']),'gallery':len(gallery),'backup':str(BACKUP)},ensure_ascii=False))
