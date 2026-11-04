from pathlib import Path
import hashlib,shutil,json,re,html
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full13/book-v06';BOOK=OUT/'dist'
assert not OUT.exists();shutil.copytree(BASE/'full11/book-v05/dist',BOOK)
build=json.loads((BASE/'full13/build/build.json').read_text(encoding='utf-8'))
NAV=[('index','제1장'),('reference','참고 분석'),('animation','영웅 동작'),('boss','파수왕'),('environment','공간·타격'),('chapter','세 구역'),('loot','장비와 드롭'),('profile','보관함'),('validation','검증')]
def nav(key):return '<nav aria-label="제작 항목">'+''.join(f'<a href="{k}.html"'+(' aria-current="page"'if k==key else '')+'>'+v+'</a>'for k,v in NAV)+'</nav>'
footer='<footer>목표: SACRATA 지향 군중 전투와 디아블로식 드롭·성장. 최종 품질 검수 중. <a href="../../../full11/book-v05/dist/index.html">후보11 도감 보존본</a> · <a href="../../SACRATA-COMPARISON.ko.md">현재 비교/다음 작업</a></footer>'
def page(key,title,body):
 (BOOK/(key+'.html')).write_text(f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 잿빛 회랑 도감</title><link rel="stylesheet" href="book.css"></head><body><header><p>잿빛 회랑 제작 도감 v06 · 전체1장 후보13 · 2026-11-01</p>{nav(key)}</header><main><h1>{title}</h1>{body}</main>{footer}</body></html>',encoding='utf-8')
def figure(name,caption):return f'<figure><img loading="lazy" src="scenes/{name}.png" alt="{html.escape(caption)}"><figcaption>{caption}</figcaption></figure>'
for p in BOOK.glob('*.html'):
 s=p.read_text(encoding='utf-8').replace('도감 v05 · 전체1장 후보11','도감 v06 · 전체1장 후보13')
 s=re.sub(r'<nav aria-label="제작 항목">.*?</nav>',nav(p.stem),s)
 s=re.sub(r'<footer>.*?</footer>',footer,s)
 if p.stem in ['animation','environment','chapter','loot','profile']:
  s=s.replace('</h1>','</h1><p class="note">이 항목은 후보11 도감의 기록을 이어받았습니다. 후보13은 아래 영웅·일반 적·환경·장비 규칙을 유지하며, 최종 보스의 외형과 표현만 새로 연결했습니다. 이전 화면/영상은 원래 후보 번호로 표시합니다.</p>',1)
 p.write_text(s,encoding='utf-8')
gpu=BASE/'boss-research12/gpu09/captures'
for n in ['front_clear5m','front_close','death-00','death-20','death-40','death-79']:
 shutil.copy2(gpu/(n+'.png'),BOOK/'scenes'/('warden-'+n+'.png'))
fixture=BASE/'boss-research12/fixture03/captures'
for n in ['circle-1','fan-1','closeup-1','walk-1']:
 shutil.copy2(fixture/(n+'.png'),BOOK/'scenes'/('warden-'+n+'.png'))
page('index','회랑 끝에서 만나는 사슬 파수왕',
 '<p class="lead">최종 보스에 고유한 몸과 여덟 동작을 연결했습니다. 영웅의 시야와 사망 순간까지 확인하며 첫 장의 전투를 다듬습니다.</p>'
 '<p class="note">후보13은 보스 표현 개선본입니다. SACRATA 목표 품질 승인은 아닙니다. 일반 적·정예의 동작, 냉기/번개 형태, 공간 깊이와 보상 연출을 계속 개선합니다.</p>'
 +figure('warden-front_clear5m','현재13 표현 · GPU09 배치 검사. 실제 보스전을 이긴 장면이 아닙니다. 영웅 앞5m에서 불필요하게 투명해지지 않는지 확인했습니다.')
 +'<div class="result"><p><strong>73골격 · 8클립</strong>최종 보스 고유 표현</p><p><strong>두 공격</strong>전조·실제 공격·회복·빙결 연결</p><p><strong>5–8분</strong>첫 장 목표 · 전체 패키지 재검수 중</p></div>'
 +'<div class="actions"><a class="primary" href="../../../../../builds/chapter1/chapter1-full-candidate-20261101-13/AshenCloister-Chapter1.exe">후보13 실행 파일</a><a href="boss.html">보스 제작과 검수</a><a href="../../../../../builds/chapter1/chapter1-full-candidate-20261101-13/RUN.ko.md">조작 안내</a></div>'
 +'<p>WASD/방향키·좌클릭 이동, Space 회피, Q 회복약, E 의식, I 장비, Esc 정지. 후보13의 전용 저장은 기존 실행본의 저장을 읽거나 변환하지 않습니다.</p><p class="subtle">EXE SHA256 '+build['sha256']+'</p>')
page('boss','무게와 전조가 있는 파수왕',
 '<p class="lead">같은 정예 이미지를 확대하던 최종 보스에 사슬·가면·긴 팔의 독립 실루엣을 부여했습니다.</p>'
 +figure('warden-closeup-1','재질05/Fixture03 확대 검사. 피부·가면·사슬은 같은 원본 diffuse를 사용하되 광택·명도를 나눴습니다. 정상 보스전이 아닌 배치 화면입니다.')
 +'<h2>연결한 동작</h2><div class="table-scroll"><table><thead><tr><th>상태</th><th>표현</th><th>게임과 연결</th></tr></thead><tbody><tr><td>대기·이동</td><td>호흡과 무게 이동, 거리 기반 보행</td><td>실제 이동 거리로 보행 위상 계산</td></tr><tr><td>근접·부채 전조</td><td>서로 다른 팔의 큰 자세</td><td>54틱 전조의 마지막8틱에서 공격 자세로 전환</td></tr><tr><td>공격·회복</td><td>내려치기 / 팔을 펼치는 부채 공격</td><td>실제 enemy_attack 이벤트의 release, 빙결 중 유지·해빙 후 연속 재개</td></tr><tr><td>피격·빙결</td><td>작은 상체 반동과 차가운 색</td><td>실제 명중·frozen_until만 반영</td></tr><tr><td>사망</td><td>무릎과 상체가 무너지는 동작</td><td>승리로 전투 틱이 멈춰도 표현 시간이 끝까지 진행</td></tr></tbody></table></div>'
 +'<div class="columns">'+figure('warden-circle-1','자체 제작 근접 전조 · Fixture03 배치 검사.')+figure('warden-fan-1','자체 제작 부채 전조 · Fixture03 배치 검사.')+'</div>'
 +'<h2>가림 문제를 다시 고치다</h2><p>후보12의 큰 고정 경계 상자는 빈 공간이 영웅과 겹쳐도 보스 전체를 흐리게 했습니다. 13은 현재 몸통·머리·팔의 화면상 겹침을 사용합니다. 보스가 영웅보다 앞에 있고 실제로 가릴 때만56%로 흐려집니다. 일반 적의 기존32% 처리는 유지합니다.</p><div class="columns">'
 +figure('warden-front_clear5m','GPU09 · 앞5m, 불투명100%.')+figure('warden-front_close','GPU09 · 실제 겹침, 보스56%.')+'</div>'
 +'<h2>전투가 끝난 뒤에도 쓰러지도록</h2><div class="columns">'+figure('warden-death-00','GPU09 · 전투 틱4 고정, 사망 시작.')+figure('warden-death-79','GPU09 · 같은 전투 틱4, 표현1.33초 후. 합성 terminal-state 검사이며 실제 승리 화면은 아닙니다.')+'</div>'
 +'<h2>원본·파생물·보류 시도</h2><p>공개 원 모델은 <a href="https://opengameart.org/content/chained-demon">Mophs의 Chained Demon</a>입니다. 제공 대안 중 <a href="https://creativecommons.org/licenses/by/3.0/">CC BY3.0</a>을 선택했습니다. 초과 가중치4개 보정, PBR 재질 분리, 자체 FK 여덟 클립과 RootMotion을 추가했습니다. D2/SACRATA 원작 자산을 사용하지 않았습니다.</p><p>Glutton Demon은 지나치게 둥근 방향이라 보류했습니다. Skeleton Outlaw의14개 원본 모션은 변환·검토했으나 아직 게임에 채택하지 않았습니다. 첫 베이크의12m 오차, 잘못된 GPU08 카메라, 후보12의 과도한 투명화도 원시 증거와 함께 보존합니다.</p><p><a href="../../../../../chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md">상세 출처와 변경</a> · <a href="../../STATUS.ko.md">현재 검수 상태</a></p><p class="note">이 모델은 비교 후보입니다. 공격의 무게·자연스러운 보행·사망 실루엣, 일반 적과의 미술 통일성은 아직 최종 승인 전입니다.</p>')
# Keep the previous observations and reference image; amend only the changed row.
p=BOOK/'reference.html';s=p.read_text(encoding='utf-8')
s=s.replace('<td>역할별 행동과 보스2단계 유지</td><td>정예/보스 고유 리그·공격/죽음이 최우선</td>','<td>최종 보스73골격/8클립·실제 공격/빙결/죽음 연결</td><td>일반 적·정예 동작과 미술 통일성, 최종 보스의 무게 개선</td>')
s=s.replace('<h1>목표와 남은 차이를 같은 표에</h1>','<h1>목표와 남은 차이를 같은 표에</h1><p class="note">기존 실제 SACRATA 영상 관찰과 후보11 비교를 보존했습니다. 이번13은 최종 보스 항목만 진전됐습니다. 이번 작업에서 원작 영상을 새로 연속 분석했다고 주장하지 않습니다.</p>')
p.write_text(s,encoding='utf-8')
page('validation','통과한 검사와 아직 부족한 품질',
 '<p class="lead">실행 성공과 목표 품질은 별도로 판단합니다. 원본·실패·이전 실행을 남겨 개선 여부를 되짚습니다.</p>'
 '<h2>후보13 패키지</h2><p>엄격한95개 런타임 원본/97개 stage/171개 PCK 항목을 감사했습니다. 새 보스 모델과 출처MD가 패키지 안에 있으며 이전 Baseline 자산·검사·연구 파일은 포함하지 않습니다. release30초 진행/외부7동작 및 전체 정상 입력 완료를 검사했습니다.</p>'
 '<p>패키지 headless/fixed60 전체 진행은21749틱/362.4833초/3185처치/Lv11입니다. 실제73골격/8클립이 로드되고, 승리 후 사망 재생 완료 로그도 확인했습니다. 실제GPU 전체 실행 결과는 별도 보고서로 확정합니다.</p>'
 '<h2>보스 표현 검사</h2><p>배치/terminal-state11개, 실제 ChapterRun.step 빙결·해빙8개를 검사했습니다. 별도GPU09의8PNG에서 화면 안 보스/영웅,5m 불투명·근접 겹침·사망 끝 자세를 확인했습니다. 검사용 배치는 실제 한 판 완료로 세지 않습니다.</p>'
 '<h2>보존한 실패</h2><p>모션02의 베이크 오차, fixture01의 형 추론 오류, GPU08의 잘못된 카메라, 후보12의 유령처럼 흐린 보스와 승리 틱 사망 정지를 보존했습니다. 후보12가 기능 검사에 통과했어도 시각 승인을 하지 않았습니다.</p>'
 '<h2>열려 있는 관문</h2><p>일반 적·정예 동작, 냉기/번개 큰 형태, 바닥/건축 깊이, 장비 목록 스크롤과 고유 발견 연출, 실제 nonempty 저장 재시작·경쟁 구간, 수동5–8분 한 판·실청취·최종1080p3회 성능은 미완료입니다. 자동 입력·캡처·고정FPS 영상은 이를 대신하지 않습니다.</p>'
 '<p><a href="../../STATUS.ko.md">현재 상태 보고서</a> · <a href="../../build/full-release-proof.json">패키지 전체 진행/사망 증거</a> · <a href="../../build/build.json">빌드 해시</a> · <a href="../../../../../chapter1/art/QUALITY13-LEDGER.json">제작 장부</a></p>')
files={str(p.relative_to(BOOK)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in BOOK.rglob('*')if p.is_file()}
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  target=(p.parent/ref.split('#')[0]).resolve();refs.append((p.name,ref))
  if not target.is_file():missing.append((p.name,ref))
report={'pages':len(list(BOOK.glob('*.html'))),'local_reference_count':len(refs),'missing_at_initial_build':missing,'files':files,'scope':'Initialv06. Previous11 pages/images/video retain original labels. GPU13 full result and final reports may still be pending; no visual/browser/performance approval.'}
(OUT/'BUILD.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({'book':str(BOOK),'pages':report['pages'],'missing':missing},ensure_ascii=False))
