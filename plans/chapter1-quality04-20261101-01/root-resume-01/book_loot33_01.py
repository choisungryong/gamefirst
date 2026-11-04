from pathlib import Path
import json,hashlib,shutil,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full33';N=B/'full30/book-v37/dist';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=read(O/'ADOPTION.json');S=Path(read(O/'build/closure.json')['stage']);checks=dict(root33=all(sha(R/n)==h for n,h in read(O/'FINAL-SOURCE-FREEZE.json').items()),stage33=all(sha(S/n)==h for n,h in read(O/'build/staging-manifest.json').items()),previous_exes=all(sha(R/n)==h for n,h in a['preserved_exes'].items()),user23restored29=all(sha(Path(n))==h for n,h in a['user_pins'].items()));assert all(checks.values());p=O/'PRESERVATION01.json';assert not p.exists();p.write_text(json.dumps(checks,indent=2),encoding='utf-8')
p=B/'loot33/REVIEW.ko.md';assert not p.exists();p.write_text('''# 드롭33b · 화염33 결합 / 후보33

제품33은 Core16/World31d/Actor32b/HUD27/Input21/FX33b. 기존FX26에세로화염높이.52와잔연기감소,드롭등급별색/빛높이/희귀+고유작은halo를추가했다. 아이템생성·획득·판정·저장규칙은변경하지않음.

compare01/session80502 import/check/26/33b GPU exit0-stderr0. 정상정책으로common/magic/rare가hero11m안에함께있는지점11165tick에서전후비교. 두정상core·tick동일/각독립전체core일치.4등급legal-item복사fixture는고유를자연드롭으로주장하지않는다. 전후4PNG모두직접검수. 실제전투밀집에서는아이템빛일부가배우뒤에가려지지만이름은구분된다. 별도배치fixture에서일반.35m/마법.85/희귀1.5/고유1.9m의빛과희귀·고유작은고리가확인된다. 전투읽힘을위해일반드롭은낮게유지. 이전후보덮어쓰기없음.

33b9checks pass:높이위계·원아이템데이터·halo중복없음·추가itemnodes없음·정상3등급·전체core같음·희귀이상만halo·삭제시node정리·원정상core복원.26baseline6checks pass. source/stage/root32핀보존.4등급fixture는실제수동획득이나고유바닥발생증거아님.

cost01/session92691는33b새단일arm만실행(기존baselineGPU중복실행안함). 정상화염16000checkpoint/2초warmup+10초OS시계/실제1920×1080/uncapped/VSyncoff/ignorefocus/profileoff/측정중캡처없음. p9510.488,p9912.174,max16.310ms/33ms초과0/drawmax384/끝16729tick독립전체core같음. flame33/cost01은별도이전참고이며이수치로정밀전후성능개선율계산금지. 정식focused최종3회아님.

package33/session83207 종료. EXE f22c74d623a2dc1c62a870a9fabcc74f2d38c0bb5d881e8e1218cf52d8f5679d/130087672bytes/runtime135-stage137-PCK246. 기존32assembly/project/preset/freeze/사용자23복원후·29rev2사본은chapter1-before33-20261105-01, 이전후보EXE핀은full33/ADOPTION.json. PRESERVATION01모두pass.

현재실제33 전체화염GPU full33/runtime/gpu-fire01/session45133/PID5240진행중. 원시launch/execution/RESULT/process확인후재사용/중복실행금지. 관찰기65sim초headless는quietpass. 실제완주·보스보상은종료전승인금지. 수동·실청취·최종동일패키지focused성능및최종품질남음. 브라우저/WindowsUI커널경로오류로실제브라우저·기본입력검수미완료. 목표active/추가툴·Github보류.
''',encoding='utf-8')
p=R/'HANDOFF.md';p.write_text('# 최신 · 후보33 패키지 종료 / 실제 전체화염 GPU 진행\n\nloot33/REVIEW.ko.md 먼저읽는다. product33 Core16/World31d/Actor32b/HUD27/Input21/FX33b. EXE SHA f22c74d623a2dc1c62a870a9fabcc74f2d38c0bb5d881e8e1218cf52d8f5679d/runtime135-stage137-PCK246. package83207완료. 정상3등급11165tick·4등급fixture compare80502 quietpass/4PNG전부검수/원core같음;cost92691 새33b단독p9510.488ms/독립core같음. 기존후보/사용자23복원후·29rev2사본·핀보존. 실제전체화염 full33/runtime/gpu-fire01/session45133/PID5240 live. 다음진입시launch/execution/raw/현재process확인하고절대중복실행금지. 종료후21749tick 원16화염10필드같음·드롭등급표시수명·보스보상화면확인예정. 도감v37 최신후보표지를간결하게정리/이전v36보존/브라우저미검수. 목표active/수동·실청취·최종focused성능미완료/추가툴·Github보류.\n\n---\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
assert not N.exists();shutil.copytree(B/'full30/book-v36/dist',N);rel=lambda p:os.path.relpath(p,N).replace('\\','/')
t=(N/'candidate32.html').read_text(encoding='utf-8');body='<h1>불꽃은 낮게, 전리품은 뚜렷하게</h1><p class="lead">후보33은 적의 몸을 덜 가리는 화염과 등급별로 구분되는 드롭 표시를 더했습니다.</p><p>일반 드롭의 빛은 낮게, 마법 장비는 푸르게, 희귀 장비는 금빛 기둥과 작은 고리로 표시합니다. 기존 공격·드롭·성장 규칙은 유지합니다.</p>'
body+=f'<div class="actions"><a class="primary" href="{rel(Path(read(O/"build/build.json")["exe"]))}">후보33 실행 파일</a><a href="loot33.html">드롭 전후 비교</a><a href="flame33.html">화염 전후 비교</a></div>'
body+='<p>WASD / 좌클릭 이동 · Space 회피 · Q 회복약 · E 의식 · I 장비 · Esc 정지</p>'
for f,c in [('flame33/compare01/33/frame-037.png','상체를 덜 가리는 화염 · 정상 획득 전투의 소스 시안'),('loot33/compare01/33b/fixture.png','네 등급의 표시 비교 · 고유 장비는 별도 배치한 표시 검수용입니다')]:body+=f'<figure><img loading="lazy" src="{rel(B/f)}" alt="{c}"><figcaption>{c}</figcaption></figure>'
body+='<h2>현재 검수 범위</h2><p id="whole-status">후보33 실제 실행 파일의 전체 화염 빌드 검수가 진행 중입니다. 종료 후 보스 마무리와 보상 화면을 확인합니다.</p><p>수동 전체 플레이·실청취·최종 성능 검수는 남아 있습니다. 이전 후보의 검증을 이번 후보 전체 승인으로 대신하지 않습니다.</p>'
body+=f'<details><summary>개선 기록과 이전 후보</summary><p><a href="{rel(B/"loot33/REVIEW.ko.md")}">후보33 검수 기록</a> · <a href="{rel(O/"build/build.json")}">빌드 고정 정보</a> · <a href="candidate32.html">이전 후보32</a> · <a href="history-index.html">이전 도감 표지</a></p></details>'
t=re.sub(r'<title>.*?</title>','<title>후보33 · 잿빛 회랑 제1장</title>',t);t=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S);t=re.sub(r'<nav.*?</nav>','<nav aria-label="제작 항목"><a href="index.html">현재 후보</a><a href="loot33.html">드롭 비교</a><a href="flame33.html">화염 비교</a><a href="motion32.html">적의 동작</a><a href="candidate31.html">공간 깊이</a><a href="history-index.html">이전 기록</a></nav>',t,flags=re.S).replace('v35 · 후보32','v37 · 후보33').replace('v36 · 후보32','v37 · 후보33')
for name in ['index.html','candidate33.html']:(N/name).write_text(t,encoding='utf-8')
body='<h1>드롭33 · 등급이 보이는 빛</h1><p class="lead">일반 드롭은 은은하게, 희귀 장비는 더 뚜렷하게 구분했습니다.</p>'
for v,c in [('26','기존 드롭 표시'),('33b','등급별 색·높이·희귀 바닥 고리')]:body+=f'<figure><img loading="lazy" src="{rel(B/f"loot33/compare01/{v}/fixture.png")}" alt="{c}"><figcaption>{c} · 네 등급 표시를 배치한 검수 장면이며 고유 장비의 자연 드롭 증거가 아닙니다.</figcaption></figure>'
body+=f'<figure><img loading="lazy" src="{rel(B/"loot33/compare01/33b/normal.png")}" alt="정상 성장 전투의 실제 세 등급 드롭"><figcaption>정상 성장11165tick에서 일반·마법·희귀 드롭을 함께 확인했습니다. 밀집 중 일부 빛은 적 뒤에 가려지며, 이름은 기존처럼 구분됩니다.</figcaption></figure><p>아이템 데이터와 생성·획득 규칙은 유지했습니다. 반복 표시 시 고리가 늘어나지 않고, 아이템이 사라지면 표시도 정리됩니다.</p><p><a href="candidate33.html">현재 후보33</a> · <a href="{rel(B/"loot33/REVIEW.ko.md")}">검수 기록과 한계</a></p>'
s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S);(N/'loot33.html').write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='Not run: prior kernel assets path error'),indent=2),encoding='utf-8');print(checks,refs)
