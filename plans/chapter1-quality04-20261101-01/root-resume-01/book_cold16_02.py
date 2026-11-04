from pathlib import Path
import json,hashlib,shutil,re,os,html
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full16'
OLD=BASE/'full14/book-v07/dist';BOOK=OUT/'book-v08/dist'
assert not BOOK.exists();shutil.copytree(OLD,BOOK)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return os.path.relpath(p,BOOK).replace('\\','/')
build=json.loads((OUT/'build/build.json').read_text(encoding='utf-8'))
movie=BASE/'cold16/actors-movie02/cold16-corpse-before-after-6s.mp4'
comparison=json.loads((movie.parent/'COMPARISON.json').read_text(encoding='utf-8'));assert comparison['same_full_core_start_and_end']
# Preserve source-labelled historical pages. Retarget external relative links
# against their original location, since the copied book now lives in full16.
for p in BOOK.glob('*.html'):
    s=p.read_text(encoding='utf-8')
    def repair(m):
        prefix,value=m.group(1),m.group(2)
        if value.startswith(('http:','https:','#','data:')):return m.group(0)
        raw,sep,anchor=value.partition('#')
        target=(OLD/raw).resolve()
        if not target.is_relative_to(OLD.resolve()):value=rel(target)+(sep+anchor if sep else '')
        return prefix+'="'+value+'"'
    s=re.sub(r'(src|href)="([^"]+)"',repair,s)
    s=s.replace('잿빛 회랑 제작 도감 v07 · 전체1장 후보14 · 2026-11-01','잿빛 회랑 제작 도감 v08 · 후보16 / 이전 항목은 본문 번호 유지')
    s=s.replace('</nav>','<a href="cold16.html">실전 냉기16</a></nav>')
    p.write_text(s,encoding='utf-8')
shutil.copy2(BOOK/'index.html',BOOK/'candidate14.html')
assets={
 'cold16-before.png':BASE/'cold16/actors01/before-shots/shatter-02-after15.png',
 'cold16-after.png':BASE/'cold16/actors01/after-shots/shatter-02-after15.png',
 'cold16-evolution.png':BASE/'cold16/normal01/event-captures/evolution-frost.png',
 'cold16-source-victory.png':BASE/'cold16/normal01/captures/state-0014-run-001-victory.png'}
for n,p in assets.items():assert p.is_file();shutil.copy2(p,BOOK/'scenes'/n)
shutil.copy2(movie,BOOK/'movies'/movie.name)
shell=(BOOK/'candidate14.html').read_text(encoding='utf-8')
def page(name,title,body):
    s=re.sub(r'<title>.*?</title>','<title>'+title+' · 잿빛 회랑 도감</title>',shell)
    s=re.sub(r'<main>.*?</main>','<main><h1>'+title+'</h1>'+body+'</main>',s,flags=re.S)
    s=s.replace(' aria-current="page"','')
    s=s.replace('href="'+name+'.html"','href="'+name+'.html" aria-current="page"',1)
    (BOOK/(name+'.html')).write_text(s,encoding='utf-8')
def fig(n,text):return '<figure><img loading="lazy" src="scenes/'+n+'" alt="'+html.escape(text)+'"><figcaption>'+text+'</figcaption></figure>'
page('index','처치가 실제 파쇄로 이어지는 냉기',
 '<p class="lead">진화 냉기로 무리를 쓰러뜨리면 주변 적에게 파편 피해가 이어지고, 사체 대신 얼음 파편이 남습니다.</p>'
 +'<p class="note">후보16은 개발 중인 별도 실행본입니다. 세 주력의 패키지 정상 자동 진행은5–8분 안에 승리했습니다. 최종 SACRATA 품질·수동 한 판·실청취·정식 성능 승인은 아직 열려 있습니다.</p>'
 +fig('cold16-after.png','동일 cold16 규칙·시드의 정상 정책54초 재구성 후 짧은 GPU 비교. 냉기로 죽은 일반 적의 사체가 사라져 무리 사이 바닥이 보입니다. 오프라인/부분 증거이며 전체 수동 플레이가 아닙니다.')
 +'<div class="actions"><a class="primary" href="'+rel(Path(build['exe']))+'">후보16 실행 파일</a><a href="cold16.html">냉기 규칙과 전후 영상</a><a href="candidate14.html">이전 후보14 표지</a></div>'
 +'<p>일반 실행은 WASD/방향키·좌클릭 이동, Space 회피, Q 회복약, E 의식, I 장비, Esc 정지입니다. 별도 후보16 저장 경로를 사용합니다.</p>'
 +'<p>새 전체 패키지 GPU 검증 결과는 <a href="'+rel(OUT/'STATUS.ko.md')+'">현재 상태</a>에 기록합니다. 이전 source16의 첫 승리는6분37.7초·3451처치·파쇄840회이며 이후 재시작 로그와 구분했습니다.</p>'
 +'<p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('cold16','냉기 처치, 파편 피해, 사체 소멸',
 '<p class="lead">14의 실제 한 판에서 파쇄0회였던 문제를 규칙과 화면 양쪽에서 고칩니다.</p>'
 +'<h2>일반 적이 얼기 전에 죽었던 문제</h2><p>기본 HP12·18인 일반 적은 진화 냉기28피해에 바로 죽었습니다. 기존 빙결 누적 후 사망 조건은 실전에서 거의 충족되지 않았습니다.15의 장식 잔해만으로는 주변 피해가 생기지 않아16에서 실제 규칙을 바꿨습니다.</p>'
 +'<h2>진화 냉기의 실제 파쇄</h2><p>진화 냉기의 직접 처치도 반경3.5m의 파쇄를 만듭니다. 기존 최대 대상 수와 타격 예산 안에서 일반 적50%·정예25% 피해를 적용하며 정수 올림을 사용합니다. 부가 파편은 다시 연쇄하지 않습니다. 비진화 냉기의 기존 빙결 파쇄와 화염·번개 규칙은 보존합니다.</p>'
 +fig('cold16-evolution.png','별도 source16 GPU 정상 런의 실제 획득 진화 선택창.3.5m·50%·정예25%를 표시하며 설명과 버튼을 확인했습니다. 후보16 최종 패키지 화면과 구분합니다.')
 +'<h2>갈색 사체 더미에서 얼음 파편으로</h2><video controls preload="metadata" poster="scenes/cold16-after.png"><source src="movies/'+movie.name+'" type="video/mp4"></video>'
 +'<p class="subtle">6초 전후 영상: 양쪽 모두 cold16 동일 규칙/seed90131/정상 정책·기본HP·획득 빌드.54초까지 코어 재구성 후8초 오프라인30FPS, 앞1초 제외. 전후 전체 시작/종료 코어 동일, 음향은 오른쪽만이며 실청취 승인 전입니다.14대16 게임 규칙 비교·실시간 성능·전체 한 판으로 세지 않습니다.</p>'
 +'<div class="columns">'+fig('cold16-before.png','수정 전: 정상 냉기 처치 후 약1.25초 남는 갈색 사체가 무리 아래 큰 덩어리로 겹칩니다.')+fig('cold16-after.png','수정 후 같은 순간: 실제 냉기로 처치된 일반 적만 약0.22초에 사라집니다. 실제 파쇄 조각은0.48초 남고 살아 있는 적과 주황 위험 표시는 유지됩니다.')+'</div>'
 +'<h2>검증 범위와 남은 품질</h2><p>원본/16 규칙의 독립 검사27개와 세 주력 페이싱, 실제 source GPU 냉기 첫 승리를 확인했습니다. 사체 처리 비교8검사는 코어 불변·정지/선택/장비 중 색상과 나이 유지·승리 후 소멸·재생 중복·초기화를 포함합니다. 같은 규칙 전후 영상도 별도 결과를 남깁니다.</p>'
 +'<p>일반 적/중간 정예의 반복 동작과 실루엣, 공간 깊이, 고유 장비 발견, 보스 죽음에서 보상으로 넘어가는 리듬을 계속 다듬습니다. 수동5–8분 전체, 실제 음향 청취, 최종1080p3회 성능과 네이티브 저장 UI 검수가 남아 있습니다.</p>'
 +'<p><a href="'+rel(BASE/'cold16/DESIGN.ko.md')+'">설계</a> · <a href="'+rel(BASE/'cold16/actors01/RESULT.json')+'">짧은 GPU 비교8검사</a> · <a href="'+rel(movie.parent/'COMPARISON.json')+'">영상 조건</a> · <a href="'+rel(OUT/'STATUS.ko.md')+'">현재 후보16 상태</a></p>')
missing=[];refs=[]
for p in BOOK.glob('*.html'):
    for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
        if ref.startswith(('http:','https:','#','data:')):continue
        refs.append([p.name,ref])
        if not(p.parent/ref.split('#')[0]).resolve().is_file():missing.append([p.name,ref])
report={'pages':len(list(BOOK.glob('*.html'))),'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p) for p in BOOK.rglob('*') if p.is_file()},'scope':'v08 static build, inherited historical pages keep original source labels. Browser/video/audio/print validation pending.'}
(BOOK.parent/'BUILD.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert not missing,missing
print(str(BOOK),flush=True)
