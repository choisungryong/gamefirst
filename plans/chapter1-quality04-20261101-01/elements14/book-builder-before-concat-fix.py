from pathlib import Path
import json,hashlib,shutil,re,html
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full14';BOOK=OUT/'book-v07/dist';assert not BOOK.exists();shutil.copytree(BASE/'full13/book-v06/dist',BOOK)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=json.loads((OUT/'build/build.json').read_text(encoding='utf-8'))
extra=['chapter_elements_quality14.gd','comet_quality14.gdshader','impact_quality14.gdshader','arc_quality14.gdshader']
ledger={'candidate':14,'scope':'Own code/mesh/shader elements, not final art approval. Hero/model/environment licenses and changes inherit QUALITY13/11.','inherits':['chapter1/art/QUALITY13-LEDGER.json','chapter1/art/QUALITY11-LEDGER.json'],'sources':{('chapter1/view/'+n):sha(ROOT/'chapter1/view'/n)for n in extra},'rules':['Paid frost point centered at nose; faceted trailing body, fire/hostile branch preserved','Actual frozen_until/hp selects24targets; elites prioritized;4crystals each;48state records','Actual shatter emits6chunks per event,8events per consume/128live shards','Paid arc.targets only,64links/.20s; thin decorative side branches deal no damage','Frost/arc contact accents3perconsume/.68 and.55scale to limit duplicate white marks','Renderer does not alter run snapshot; dedupe, pause, thaw and reset verified in packaged release external probe'],'new_protected_game_asset':False,'new_external_art':False,'comparison':'plans/chapter1-quality04-20261101-01/elements14/movie05/COMPARISON.json','configured_arena':'80placed140HP/.75speed enemies; supplied evolved frost4 and arc4 at8s, hero5000HP; not earned/normal chapter','release_caps13':'plans/chapter1-quality04-20261101-01/full14/release-caps02/result.json','retained_failures':['arena01 fixture step() signature','arena02 dark ice/oversized overlapping contact stars','arena03 intermittent exit warning, release-caps01 verbose identified paused WAV/playback; probe now matches production audio.reset/real wall release','movie compose helper mistook ffmpeg info stderr for failure; encoded output exit0/ffprobe validated without re-encoding'],'open':['natural ice/fracture art direction','normal full gameplay visual reading','general/champion actors','world depth','loot/reward UX','manual full run/heard audio/formal performance']}
p=ROOT/'chapter1/art/QUALITY14-LEDGER.json';assert not p.exists();p.write_text(json.dumps(ledger,indent=2,ensure_ascii=False),encoding='utf-8');shutil.copy2(p,Path(build['exe']).parent/'credits'/p.name)
NAV=[('index','제1장'),('reference','참고 분석'),('animation','영웅 동작'),('boss','파수왕'),('elements','냉기·번개'),('environment','공간·타격'),('chapter','세 구역'),('loot','장비와 드롭'),('profile','보관함'),('validation','검증')]
def nav(key):return '<nav aria-label="제작 항목">'+''.join(f'<a href="{k}.html"'+(' aria-current="page"'if k==key else '')+'>'+v+'</a>'for k,v in NAV)+'</nav>'
footer='<footer>SACRATA 지향 군중 전투와 디아블로식 드롭·성장. 최종 품질 검수 중. <a href="../../../full13/book-v06/dist/index.html">후보13 도감 보존본</a> · <a href="../../SACRATA-COMPARISON.ko.md">남은 차이와 다음 작업</a></footer>'
def page(key,title,body):
 (BOOK/(key+'.html')).write_text(f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 잿빛 회랑 도감</title><link rel="stylesheet" href="book.css"></head><body><header><p>잿빛 회랑 제작 도감 v07 · 전체1장 후보14 · 2026-11-01</p>{nav(key)}</header><main><h1>{title}</h1>{body}</main>{footer}</body></html>',encoding='utf-8')
def fig(n,c):return f'<figure><img loading="lazy" src="scenes/{n}.png" alt="{html.escape(c)}"><figcaption>{c}</figcaption></figure>'
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('도감 v06 · 전체1장 후보13','도감 v07 · 전체1장 후보14')
 s=re.sub(r'<nav aria-label="제작 항목">.*?</nav>',nav(p.stem),s);s=re.sub(r'<footer>.*?</footer>',footer,s)
 if p.stem not in ['index','validation']:s=s.replace('</h1>','</h1><p class="note">이 항목은13 도감의 기록을 보존해 이어갑니다.14는 냉기/번개 표현을 개선했고 아래 이전 화면·영상의 후보 번호는 유지했습니다.</p>',1)
 p.write_text(s,encoding='utf-8')
for suffix,label in [('0138','frost'),('0482','arc'),('0318','shatter')]:
 for variant,source in [('before13',BASE/'elements14/arena02/before13/captures'),('after14',BASE/'elements14/arena04/captures')]:shutil.copy2(source/(variant+'-'+suffix+'.png'),BOOK/'scenes'/(label+'-'+variant+'.png'))
(BOOK/'movies').mkdir(exist_ok=True)
movie=BASE/'elements14/movie05/elements-before13-after14-13s.mp4';shutil.copy2(movie,BOOK/'movies'/movie.name);assert sha(movie)==sha(BOOK/'movies'/movie.name)
page('index','서리의 파쇄와 전류의 궤적',
 '<p class="lead">무리를 스치는 냉기창, 얼어붙은 발밑, 터지는 얼음 파편과 연결되는 번개를 다듬었습니다.</p><p class="note">후보14는 표현 개선본입니다. SACRATA 목표 품질 승인은 아닙니다. 아래 첫 화면은 지급한 성장 빌드의 비교용 배치이며 정상 한 판을 이긴 장면과 구분합니다.</p>'
 +fig('frost-after14','수정14 · 실제 core 이벤트가 발생하는 연구 배치.80적/적140HP·영웅5000HP·지급 진화 냉기4. 정상 전투의 난이도/획득 성장/성능 증거가 아닙니다.')
 +'<div class="actions"><a class="primary" href="../../../../../builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe">후보14 실행 파일</a><a href="elements.html">냉기·번개 전후 영상</a><a href="../../STATUS.ko.md">현재 상태</a></div><p>일반 실행은 WASD/방향키·좌클릭 이동, Space 회피, Q 회복약, E 의식, I 장비, Esc 정지. 별도 전용 저장을 사용합니다. 기존 저장을 가져오거나 변환하지 않습니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('elements','원소마다 다른 형태와 순간',
 '<p class="lead">푸른 선을 늘리는 대신, 냉기는 면과 파편으로, 번개는 짧고 밝은 연결 경로로 구분합니다.</p>'
 '<h2>13초 전후 비교</h2><video controls preload="metadata" poster="scenes/arc-after14.png"><source src="movies/elements-before13-after14-13s.mp4" type="video/mp4"></video><p class="subtle">왼쪽13 / 오른쪽14 · 오프라인30FPS.80배치적140HP·.75속도, 영웅5000HP, 진화 냉기4 지급·8초에 진화 번개4 추가, 성장 선택 억제. 양쪽 core 결과7항목 동일. 음향은 오른쪽만 사용했으며 실청취 승인 전입니다. 정상 한 판·획득 빌드·실제 성능으로 세지 않습니다.</p>'
 '<h2>냉기창과 빙결</h2><div class="columns">'+fig('frost-before13','기존13 · 같은 연구 배치/같은 입력의2.3초.')+fig('frost-after14','수정14 · 같은2.3초. 실제 빙결 대상에만 네 얼음 조각, 창에는 면/중심을 부여했습니다.')+'</div><p>창의 밝은 앞부분을 실제 투사체 위치에 맞추고 뒤쪽에 면을 남깁니다. 실제 빙결 중이며 살아 있는 적만 얼음 대상이 됩니다. 발밑의 조각은 작게 자라고 해빙/사망 때 사라집니다. 멀리 있는 정예가 일반 적에 밀려 표시되지 않는 경우를 막았습니다.</p>'
 '<h2>번개 경로와 겹친 명중 순간</h2><div class="columns">'+fig('arc-before13','기존13 · 연구8.03초. 흰 명중 별과 경로가 겹칩니다.')+fig('arc-after14','수정14 · 같은8.03초. 밝은 중심 경로와 더 작은 명중 별로 분리했습니다.')+'</div><p>게임이 이미 확정한 대상 사이의 경로를 사용합니다. 얇은 옆가지는 장식이며 추가 피해를 만들지 않습니다. 짧은 중심선과 청색 잔광은0.20초 안에 사라집니다. 냉기/번개의 중복 명중 별은 크기와 한 번에 나타나는 수를 낮췄습니다.</p>'
 '<h2>실제 파쇄에서만 큰 조각</h2>'+fig('shatter-after14','연구5.3초 · 실제 frozen 대상 처치의 shatter 이벤트가 원형 파쇄와 큰 파편을 만듭니다. 배치 결과에서 파쇄19회/최대동시빙결11을 관찰했습니다.')
 '<h2>제작과 한계</h2><p>새 형상/셰이더는 독자 코드로 만들었습니다. 새 원작 아트를 가져오지 않았습니다. 얼음의 자연스러운 굴절·더 날카로운 파쇄, 실제 군중에서 영웅/위험 표시의 가독성은 계속 검수합니다. 일반 적/정예 동작·공간 깊이·장비 발견/처치 보상 연출도 미완료입니다.</p><p><a href="../../../../../chapter1/art/QUALITY14-LEDGER.json">소스 해시와 제작 장부</a> · <a href="../../../elements14/movie05/COMPARISON.json">영상 조건과 동일 core 결과</a> · <a href="../../release-caps02/result.json">패키지 효과 상태 검사</a></p>')
page('validation','실제 결과와 품질 판단을 구분하다',
 '<p class="lead">이펙트가 화려해져도 피해·빙결·성장 결과를 몰래 바꾸지 않도록 확인합니다.</p><h2>패키지14</h2><p>99개 런타임 원본/101개stage/176개PCK 항목을 감사했습니다. release30초/외부7동작/전체 화염 정상 정책은21749틱/362.4833초/3185처치/Lv11 승리,stderr0입니다. 고유 보스·승리 후 사망도 유지합니다. 별도 패키지 효과 검사13개(상한·중복·정지·해빙·초기화·코어불변)도 종료0/stderr0입니다.</p><h2>GPU 비교와 영상</h2><p>연구 배치13초의 core7상태가 전후 동일합니다. GPU04에서15PNG/종료0/stderr0, 별도 오프라인30FPS 양쪽 영상도 종료0/stderr0, 합성MP4는13초/390프레임입니다. 이는 정상 한 판/실제 성능 증거와 다릅니다.</p><h2>냉기 정상 전체 실행</h2><p>실제14 패키지·기본 난이도·정상 자동 입력·저장off로 진행 중입니다. 종료 후 상태 보고서에 확정합니다. 지급 빌드 연구와 섞지 않습니다.</p><h2>보존한 실패</h2><p>첫 검사 step인자 오류, 짙은 얼음/겹친 흰별, 검사 종료의 WAV/playback 경고, ffmpeg 정보stderr를 오류로 판정한 helper를 보존했습니다. WAV경고는 검사가 제품 audio.reset과 실제시계 대기를 우회한 것으로 확인해 동일 절차로 고친 패키지02에서 조용히 통과했습니다. 일반 종료 전체의 누수0으로 확대하지 않습니다.</p><h2>아직 열려 있는 것</h2><p>수동5–8분 전체·실청취·최종1080p3회 성능, 실제 nonempty 저장 재시작·경쟁 구간, 일반/정예 동작·환경 깊이·장비/보상 UX는 미완료입니다.2·3장은 첫 장 품질 검수 뒤입니다.</p><p><a href="../../STATUS.ko.md">현재 상태</a> · <a href="../../build/build.json">빌드 정보</a></p>')
for name,source in [('STATUS.ko.md','''# 후보14 · 냉기/번개 표현, 목표 active

최신 실행은 builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe다. SHA256 5fa58077545ea3cc3c0d55bc6abbd5bc57eab32bdd78c8ccdbfa398ca28f5952,129994088bytes/runtime99/stage101/PCK176.13/과거 실행·실패·원본·사용자 저장을 보존한다. SACRATA 최종 품질 승인이 아니다.

새4파일의 독자FX는 냉기창 중심/면·실제frozen_until의반투명4얼음/실제shatter의큰파편·paidarc.targets의밝은중심/잔광과작아진냉기/번개contact다. 최대64links/24frozen×4/48records/128shards이며중복·정지·해빙·초기화·코어불변을실제패키지외부13검사로확인했다. 피해·AI·성장·드롭규칙과13보스·영웅/환경은그대로다.

패키지release30초/외부7동작/전체화염fixed60headless정상정책은21749틱/362.4833초/3185처치/Lv11,종료0/stderr0. 실제GPU냉기정상전체는runtime/gpu-cold01/에서진행중이며종료후GPU-COLD-RESULT.json으로확정한다. 이문장의진행중을전체완료로확대하지않는다. 저장off/자동정책이며수동전체·실청취·성능승인이아니다.

별도80배치적/140HP·.75speed/영웅5000HP/지급진화냉기4·8초후지급진화번개4/성장선택억제의13초연구는실제ChapterRun.step이피해/빙결/파쇄를결정한다. before13대after14의7core상태동일,빙결hit184/파쇄19/동시빙결11/48kill. GPU04의15PNG와오프라인30FPS전후영상은정상한판/획득빌드/성능증거로세지않는다. movie05 MP413초/390frames/1280×428,음향오른쪽만/실청취전.

검사첫step인자오류·짙은얼음/겹친흰별·ObjectDB경고를보존했다. release-caps01 verbose로AudioStreamWAV/PlaybackWAV객체를식별했고검사가제품audio.reset(정지voice unpause)/실제시계release대기를우회한것을확인했다. 동일절차를적용한release-caps02는13/0/actual0/stderr0이며제품14freeze/EXE는바꾸지않았다. 모든상황의누수0주장아님. moviecompose는정상ffmpeg정보stderr를helper가거절했으나actual0/완성파일을ffprobe로확인하고재인코딩없이별도확정했다. 원시helper/출력유지.

도감v07은이전13항목/화면번호를유지하고냉기·번개페이지를추가한10페이지다. 초기BUILD/진행중본문은보존하고GPU결과확정후별도revision으로갱신한다. 출처는QUALITY14-LEDGER.json→13/11장부,원작보호자산미사용. 기술검사성공을품질완료로바꾸지않는다. 다음은일반/정예동작·공간깊이·장비스크롤/고유발견·보스사망→보상리듬. 수동전체/실청취/정식성능/비어있지않은저장재시작·경쟁구간은열림.
'''),('SACRATA-COMPARISON.ko.md','''# 후보14 · 원소 형태의 개선과 남은 격차

기존 SACRATA 실제 영상 관찰/25개 유효 표본과 항목별 비교는 full11/SACRATA-COMPARISON.ko.md, 보스 개선은 full13/SACRATA-COMPARISON.ko.md에 보존했다. 이번 작업에서 원작 전 영상을 새로 연속 분석하거나 실청취한 것은 아니다.

목표는 원소가 성장할수록 큰 형태와 반응이 달라지는 군중 전투다.14는 냉기창의 면·빙결 발밑 얼음·실제 파쇄 조각, 번개의 밝은 연결 중심과 짧은 잔광으로 구분했다. 겹치는 흰 명중별은 줄였다. 연구 전후 영상은 같은 core 입력/상태에서 표현을 비교하지만 지급 성장·증강 체력을 사용하므로 실제 획득 성장/난이도/완성품질로 승인하지 않는다.

아직 일반 적·정예의 짧고 반복되는 동작, 넓은 판석과2.5D 폐허의 평면감, 장비 발견/회수와 보스 사망→보상 전환의 약한 리듬이 크다. 얼음도 더 자연스러운 면/파쇄와 실제 군중에서 위험/영웅을 가리지 않는 연출이 필요하다. 다음은 일반/정예 동작 → 공간 깊이 → 장비·보상 UX를 개선하고 수동전체·실청취·정식성능/저장 관문을 검수한다.2·3장으로 기능을 넓혀 첫 장의 품질 격차를 덮지 않는다.
''')]:
 p=OUT/name;assert not p.exists();p.write_text(source,encoding='utf-8')
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append((p.name,ref))
  if not(p.parent/ref.split('#')[0]).resolve().is_file():missing.append((p.name,ref))
report={'pages':10,'local_references':len(refs),'missing':missing,'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p)for p in BOOK.rglob('*')if p.is_file()},'scope':'Initialv07; GPU cold normal result pending; browser/video/audio/print not yet approved.'};p=BOOK.parent/'BUILD.json';p.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({'book':str(BOOK),'missing':missing,'local_refs':len(refs)}))
