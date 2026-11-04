from pathlib import Path
import json,re,shutil,html,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent
BOOK=ROOT/'plans/chapter1-quality04-20261101-01/full09/book-v04/dist'
assert not BOOK.exists();BOOK.mkdir(parents=True)
(BOOK/'scenes').mkdir();(BOOK/'research').mkdir()
shutil.copy2(ROOT/'plans/chapter1-quality-20261031-01/book-v03/dist/book.css',BOOK/'book.css')
with (BOOK/'book.css').open('a',encoding='utf-8') as f:f.write('\na:focus-visible,button:focus-visible{outline:3px solid #d0b477;outline-offset:5px}.chapter-map{display:flex;gap:18px;align-items:center;flex-wrap:wrap;padding:26px 0}.chapter-map a{padding:16px;border-block:1px solid #5e747f;text-decoration:none}.table-scroll{overflow-x:auto}figcaption{max-width:76ch}.wide{width:100%}\n')
NAV=[('index','제1장'),('chapter','세 구역'),('loot','장비와 드롭'),('profile','보관함'),('animation','동작 연구'),('validation','검증')]
def e(v):return html.escape(str(v))
def page(key,title,body):
 nav=''.join('<a href="%s.html"%s>%s</a>'%(a,' aria-current="page"' if a==key else '',b) for a,b in NAV)
 data=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 잿빛 회랑 도감</title><link rel="stylesheet" href="book.css"></head><body><header><p>잿빛 회랑 제작 도감 · 전체1장 후보09 · 2026-11-01</p><nav aria-label="제작 항목">{nav}</nav></header><main><h1>{title}</h1>{body}</main><footer>목표: SACRATA 지향의 화려하고 읽기 쉬운 군중 전투와 디아블로식 장비·기술 성장. 최종 표현·실청취·수동 한 판·정식 성능 승인 전입니다. <a href="../../../../chapter1-quality-20261031-01/book-v03/dist/index.html">품질03 도감</a> · <a href="../../../../chapter1-c2-20261031-01/book-v02/dist/index.html">39브리프 이력</a></footer></body></html>'
 (BOOK/(key+'.html')).write_text(data,encoding='utf-8')
def copy_capture(source,name):
 assert source.is_file(),source
 shutil.copy2(source,BOOK/'scenes'/name)
 return '<figure><img loading="lazy" src="scenes/'+name+'" alt="'+e(name)+'"><figcaption>'
native=ROOT/'plans/chapter1-quality04-20261101-01/full07/runtime/native01/captures'
playing=sorted(native.glob('*frame-005.png'))[0]
figure=copy_capture(playing,'native07-opening.png')+'후보07의 직접 시작 화면. 후보09는 이 공간에 작은 영웅 표식을 더하고 초반 압박을 조정했습니다. 두 후보를 같은 상태의 전후 화면으로 표시하지 않습니다.</figcaption></figure>'
page('index','한 판이 끝까지 이어지는 회랑',f'<p class="lead">앞뜰에서 장비를 줍고, 열린 회랑을 지나, 성장한 기술로 성소의 보스에 도달하는 한 장을 연결했습니다.</p><p class="note">후보09는 전체1장 기능을 연결한 검토본입니다. SACRATA 수준의 최종 표현이나 수동 플레이 품질을 승인한 결과가 아닙니다.</p>{figure}<div class="chapter-map"><a href="chapter.html">세 마당과 두 회랑</a><a href="loot.html">12개 장비 바탕과3개 고유 효과</a><a href="profile.html">다음 판에 남는 장비</a></div><p>화염·냉기·번개는 각자의 주기로 자동 시전됩니다. 봉인 주변의 적을 처치하고 정예를 쓰러뜨리면 다음 마당으로 갈 수 있습니다. 마지막 보스의 실제 처치가 완료 조건입니다. 단순히 시간이 지나면 승리하지 않습니다.</p><div class="actions"><a href="../../../../../builds/chapter1/chapter1-full-candidate-20261101-09/AshenCloister-Chapter1.exe">후보09 실행 파일</a><a href="../../../../../builds/chapter1/chapter1-full-candidate-20261101-09/RUN.ko.md">조작 안내</a></div>')
page('chapter','세 봉인을 지나 재의 성소로','''<p class="lead">각 마당에는 무리를 모아 쓸어버릴 공간과 다음 목표가 있습니다. 열린 문 사이를 직접 이동합니다.</p><div class="chapter-map"><a href="#courtyard">잿빛 앞뜰 →</a><a href="#nave">무너진 성가대 →</a><a href="#sanctuary">재의 성소</a></div><h2 id="courtyard">잿빛 앞뜰</h2><p>첫10초의 압박을 낮추고12마리로 시작합니다. 봉인 주변600처치 뒤 잿불의 문지기가 등장합니다. 근접 원과 부채탄의 전조를 피하고 처치하면 동쪽 문이 열립니다. 가까운 불씨 의식은25초 동안 위치를 지키며 추가 적을 상대하는 선택 보상입니다.</p><h2 id="nave">무너진 성가대</h2><p>짧은 회랑을 지나 실제로 도착해야 다음 봉인 전투가 시작됩니다.900처치 뒤 성가대장의 십자형 냉기 공격과 부채탄이 이어집니다. 십자 네 팔의 표시와 실제 피해 범위가 같은 캡슐로 정의됩니다. 성유물 의식은 주변60처치로 별도 보상을 줍니다.</p><h2 id="sanctuary">재의 성소</h2><p>900처치 뒤 회랑의 파수왕이 등장합니다. 근접/부채탄 외에 현재 위치에 재의 낙인을 남깁니다.72틱의 예고 뒤 반경1.8m 안에 피해가 발생하며, 생명력이 절반이면 세 장판으로 늘어납니다. 보스를 쓰러뜨린 뒤 남은 장판은 취소됩니다.</p><h2>회복과 선택</h2><p>Q는 최대 생명력35%를 회복하며4초 재사용 시간이 있습니다. 시작3개, 최대5개입니다. 정예와 일반 전투에서 회수할 기회가 있으며 의식의 보상에도 포함됩니다. 장비는 I로 비교하고 직접 장착합니다. 장비 교체로 현재 생명력이 회복되지는 않습니다.</p>''')
source=(ROOT/'chapter1/core/chapter_items.gd').read_text(encoding='utf-8')
arrays={}
for key,next_ in [('BASES','AFFIXES'),('AFFIXES','UNIQUES'),('UNIQUES','LIMITS')]:
 arrays[key]=json.loads(re.search(r'const '+key+r' := (\[.*?\])\nconst '+next_,source,re.S).group(1))
def stats(values):
 names={'damage_bps':'피해','cooldown_bps':'시전 속도','max_hp_raw':'최대 생명력','damage_reduction_bps':'피해 감소','pickup_radius_cm':'회수 반경','projectiles':'발사체/번개 대상','pierce':'투사체 관통','chain_targets':'연쇄 대상','shatter_count':'파쇄 파편','radius_cm':'화염 폭발·번개 거리','slow_bps':'냉기 감속','fire_damage_bps':'화염 피해','fire_burst':'화염 처치 폭발','frost_threshold':'빙결 문턱 감소','arc_branches':'번개 분기','arc_damage_bps':'번개 피해'}
 result=[]
 for key,value in values.items():
  suffix='';number=value
  if key.endswith('_bps'):number=value/100;suffix='%'
  elif key=='max_hp_raw':number=value/256
  elif key.endswith('_cm'):number=value/100;suffix='m'
  result.append(f'{names.get(key,key)} {number:+g}{suffix}')
 return ' / '.join(result)
rows=''.join(f'<tr><td>{e(b["name"])}</td><td>{e(b["slot"])}</td><td>{b["level"]}</td><td>{e(stats(b["stats"]))}</td></tr>' for b in arrays['BASES'])
affix=''.join(f'<tr><td>{e(a["name"])}</td><td>{e(a["group"])}</td><td>{e(stats({a["stat"]:a["low"]}))} ～ {e(stats({a["stat"]:a["high"]}))}</td><td>{a["level"]}</td></tr>' for a in arrays['AFFIXES'])
unique=''.join(f'<h3>{e(u["name"])}</h3><p>{e(u["description"])}</p>' for u in arrays['UNIQUES'])
page('loot','装備を選ぶ楽しさ'.replace('装備を選ぶ楽しさ','장비를 고르는 이유'),f'<p class="lead">같은 슬롯에서도 화력·방어·회수·공격 형태를 교환합니다. 아래 표는 실제 후보09의 독자 장비 정의입니다. 아이템 아이콘 아트는 아직 제작 전입니다.</p><h2>장비 바탕12개</h2><div class="table-scroll"><table><thead><tr><th>이름</th><th>슬롯</th><th>등장 레벨</th><th>기본 효과</th></tr></thead><tbody>{rows}</tbody></table></div><h2>무작위 옵션12종</h2><p>일반은 추가 옵션0, 마법은1, 희귀는2개입니다. 등장 레벨/슬롯/가중치와 배타 그룹을 적용합니다. 같은 그룹은 한 장비에 중복하지 않습니다.</p><div class="table-scroll"><table><thead><tr><th>옵션</th><th>배타 그룹</th><th>범위</th><th>최소 레벨</th></tr></thead><tbody>{affix}</tbody></table></div><h2>고유 효과3개</h2>{unique}<p>마지막 보스는 선택한 주력에 해당하는 고유 장비를 보상합니다. 고유 장비가 첫 완료의 필수 조건은 아닙니다. 효과마다 발동 깊이·대상 중복 방지와 한 시전의 피해 예산을 제한합니다.</p>')
stash=sorted(native.glob('*menu.png'))[0]
page('profile','전투가 끝나도 남는 장비','<p class="lead">획득 장비를 보관하고 다음 도전의 네 슬롯을 고릅니다. 런의 경험치와 기술 선택은 새 판에서 다시 시작합니다.</p><p>승리·패배 모두 새로 획득한 장비를 전용 프로필에 보관합니다. 가져온 장비는 다시 저장해 복제하지 않으며, 같은 도전의 보상을 두 번 처리하지 않습니다. 보관함에서 장착 또는 해체를 직접 선택합니다.</p><p>보관함은256개, 마지막 판의 회수 보상은 최대69개를 추가 보존합니다.256개를 넘으면 정리 후 다음 판을 시작할 수 있습니다. 저장 revision을 남기고 손상된 원본이나 다른 실행의 변경은 덮어쓰지 않습니다.</p><p class="note">기존 Baseline 장비/진행 파일은 읽거나 변환하지 않습니다. 실제 전용 경로는 해당 후보의 새 사용자 폴더입니다. 화면 검증용 실행은 저장을 명시적으로 끄고 별도 표시합니다.</p><p>현재 검증: 새 프로필27개 검사에서 복원·슬롯 선택·중복 방지·손상 보존·325개 최종 회수를 확인했습니다. 실제 패키지의 비어 있지 않은 보관함 전체 조작과 재시작 저장 검수는 계속 진행할 항목입니다.</p>')
research=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01')
for name in ['00_idle.png','02_run.png','06_cast.png','11_death.png']:
 shutil.copy2(Path('C:/Project/game-research/build-staging/mage-gltf-research-20261101-02/captures')/name,BOOK/'research'/name)
page('animation','발을 디디는 동작부터 다시','<p class="lead">반복되는 네 프레임의 보행을 최종 품질로 받아들이지 않고 실제 리깅 후보를 검토했습니다.</p><p>AI8보행 시도03은 같은 선행발을 반복해 거절했습니다. 공개 rigged mage는 실제 골격으로 자체 IK 보행·시전·피격·사망을 작성해 Godot에서 재생했습니다.54개 엔진 골격과5개 클립을 확인했지만 어깨 옷감의 늘어짐, 단순한 사망 자세가 남아 런타임에 아직 채택하지 않았습니다.</p><div class="columns"><figure><img src="research/02_run.png" alt="실제 골격으로 한쪽 다리를 앞으로 내딛은 연구 모델"><figcaption>교대 보행의 실제 엔진 프레임</figcaption></figure><figure><img src="research/06_cast.png" alt="시전 중인 모델의 어깨 옷감"><figcaption>시전 범위를 낮췄지만 옷감 변형 검수는 열려 있습니다.</figcaption></figure></div><figure><img src="research/11_death.png" alt="가라앉지 않도록 수정한 사망 연구 자세"><figcaption>바닥 관통은 수정했으나 완성된 사망 연기로 승인하지 않았습니다.</figcaption></figure><p>연구 모델/렌더: <a href="https://opengameart.org/content/rigged-textured-mage">thecubber · Rigged textured mage</a>, 원 리그 크레딧 Julius/OGA, <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA3.0</a>. 변경: 구형 재질 변환, 자체 IK 자세/베이크, 엔진 재생. 이 연구 이미지의 파생물도 같은 라이선스를 따릅니다. 게임 규칙 코드와 다른 아트의 라이선스는 각 출처를 따릅니다.')
page('validation','확인한 결과와 열린 관문','<p class="lead">대표90초에서 전체1장으로 확장했지만, 기술 검사와 목표 품질을 구분합니다.</p><h2>실제 구현</h2><p>세 구역·두 회랑·봉인 목표·서로 다른 정예 공격·보스2단계·선택 의식2종·회복약·장비12바탕/12옵션/3고유·새 보관함과 저장을 연결했습니다.</p><h2>보존한 실패</h2><p>첫 전투 체력이 초기 처치를 지연시켜93.8초 패배했던 실행, 냉기10분35초로 목표 시간을 초과한 실행, 후보07 릴리스의 검사문 안 호출 생략으로 첫 성장 선택에 멈춘 실행을 남겼습니다. 후보08은 선택을 고쳤으나 고정FPS 종료의 오디오 해제 경고가 있어 승인하지 않았습니다. 후보09는 실제 시간으로 오디오 해제를 기다리며 같은 경로를 재검증합니다.</p><h2>아직 승인하지 않은 것</h2><p>SACRATA 수준의 배우·환경·효과 통일성, 실제 수동 한 판의 흐름, 음향 실청취, 정식1080p 성능3회, 비어 있지 않은 보관함의 실제 재시작 검수는 열려 있습니다. 리깅 후보가 존재한다는 이유로 동작 품질을 완료 처리하지 않습니다.</p><p>후보09의 실제GPU 전체 실행과 세 빌드의 패키지 실행 결과는 별도 실행 보고서로 갱신합니다. 고정FPS/headless·자동 입력은 수동 조작이나 실제 성능 측정이 아닙니다.</p>')
manifest={str(p.relative_to(BOOK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in BOOK.rglob('*') if p.is_file()}
with (BOOK.parent/'BUILD.json').open('x',encoding='utf-8') as f:json.dump({'files':manifest,'pages':6,'scope':'Initial v04. GPU09 evidence still pending; no final quality approval.'},f,indent=2)
print(json.dumps({'path':str(BOOK),'pages':6,'files':len(manifest)}))
