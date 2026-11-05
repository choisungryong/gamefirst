from pathlib import Path
import json,hashlib,shutil,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full34';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=read(O/'ADOPTION.json');S=Path(read(O/'build/closure.json')['stage']);checks=dict(root34=all(sha(R/n)==h for n,h in read(O/'FINAL-SOURCE-FREEZE.json').items()),stage34=all(sha(S/n)==h for n,h in read(O/'build/staging-manifest.json').items()),previous_exes=all(sha(R/n)==h for n,h in a['preserved_exes'].items()),user23restored29=all(sha(Path(n))==h for n,h in a['user_pins'].items()));assert all(checks.values());p=O/'PRESERVATION01.json';assert not p.exists();p.write_text(json.dumps(checks,indent=2),encoding='utf-8')
p=B/'monster34/REVIEW.ko.md';p.write_text(p.read_text(encoding='utf-8')+'''
## 네 방향·사망과 후보34 패키징

directions01의observer bool추론check오류는GPU전중단/FAILURE보존. 명시bool의directions02/session23391은check/GPUexit0-stderr0/13checks/6PNG전부직접검수. 네방향을비교용으로snap한복사fixture에서windup/release/recover 및death.25/.60/1.00초의도끼·몸자세가읽힘.1초에는쓰러진사체가희미해짐. 정상2800전체core복원. 이것을자연획득전투/모든방향연속영상/수동검수로승격하지않는다.

후보34 채택: sourceActor34b는cost01/directions02와동일바이트. package/session9532종료/import-export-PCK-30sim초headless-releasebehavior통과. EXE e7b97b250c592bd69da2390eb183c25a39def354f02df0c1d318d5f122b9933f/134104744bytes/runtime141-stage143-PCK258. Core16/World31d/Actor34b/HUD27/Input21/FX33b. CC0원출처·병합기록·credits포함. 원33assembly/project/preset/freeze와23복원후/29rev2/journals는chapter1-before34-20261105-01. 기존EXE핀/full34ADOPTION/PRESERVATION01모두보존.

현재 full34/runtime/gpu-cold01/session93270/PID4796 실제전체냉기실행중. observer65sim초headlessquietpass. 완료전승인금지/원시launch·execution·현재PID확인후재사용/중복실행금지. 새walker실제family·냉기사체alpha와840파쇄·전체core/보스보상관찰.150초actualPNG1장직접봤고새뼈형태/파쇄위치구분/사체누적억제보임. 끝났다고전수시각승인하지않는다.

별도equipment35/svg01은기존네슬롯용자체SVG4개를새미연결폴더에작성. Godot headless SVG파서192×192렌더4개quiet/4PNG직접검수. HUD/기존Sigil/UI/제품34에는아직연결안함. 미래범용툴개발이아니라실제보상아이콘미술준비. 아이템종류·능력치불변. 다음은현재34전체종료확인후새아이콘의실제발견/보상UI크기·가독성검수. 최종수동·실청취·focused성능은UI복구등증거필요.
''',encoding='utf-8')
p=R/'HANDOFF.md';p.write_text('# 최신 · 후보34 패키지 종료 / 실제전체냉기 GPU 진행\n\nmonster34/REVIEW.ko.md 최신부분읽는다. directions02(23391)quiet/13checks/네방향공격·사망6PNG전부직접검수. 첫directions01 bool추론실패/GPU전보존. package34/session9532완료 EXE SHA e7b97b250c592bd69da2390eb183c25a39def354f02df0c1d318d5f122b9933f/runtime141-stage143-PCK258/Actor34b. source와코어및기존EXEs·사용자23복원후/29rev2핀보존. 실제전체냉기full34/runtime/gpu-cold01/session93270/PID4796현재live. launch/execution/raw/현재PID확인후중복실행금지. observer65sim초headlessquietpass,actual150초PNG1장직접검수/완료전승인금지. 도감v39현재34표지준비(전체검수중표기)/브라우저미검수. 별도equipment35/svg01 자체4SVG 아이콘작성·headless192px파서렌더quiet/4PNG검수,HUD35/제품연결아직없음. 다음34전체종료·후반/보상화면→아이콘발견/보상UI검수. UI복구질문답대기/목표active/최종수동·실청취·focused성능미완료/추가툴·Github보류.\n\n---\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
N=B/'full30/book-v39/dist';assert not N.exists();shutil.copytree(B/'full30/book-v38/dist',N);rel=lambda p:os.path.relpath(p,N).replace('\\','/')
t=(N/'candidate33.html').read_text(encoding='utf-8');body='<h1>도끼를 든 해골과 냉기 전투</h1><p class="lead">후보34는 일반 근접 적을 해골·도끼 모델과 저작된 보행·공격·사망 동작으로 구분했습니다.</p><p>원거리·돌진·정예·보스와 기존 냉기 파쇄, 화염 가림 개선, 드롭 표시는 유지합니다. 공격 판정과 성장·아이템 규칙도 같습니다.</p>'
body+=f'<div class="actions"><a class="primary" href="{rel(Path(read(O/"build/build.json")["exe"]))}">후보34 실행 파일</a><a href="monster34.html">근접 적 전후 비교</a><a href="equipment35.html">장비 그림35 연구</a></div>'
for f,c in [('monster34/directions02/proof/release.png','네 방향 도끼 타격 자세 · 복사한 표시 검수 장면'),('monster34/directions02/proof/death100.png','사망1초 후의 쓰러짐과 사라짐 · 복사한 표시 검수 장면')]:body+=f'<figure><img loading="lazy" src="{rel(B/f)}" alt="{c}"><figcaption>{c}</figcaption></figure>'
body+='<p id="whole-status">후보34 실제 실행 파일의 전체 냉기 빌드 검수가 진행 중입니다. 종료 후 파쇄·사체 처리와 보스 보상 화면을 확인합니다.</p><p>수동 전체 플레이·실청취·최종 성능 검수는 남았습니다. 소스 단회비용p9510.101→10.548ms는정식최종성능승인과구분합니다.</p>'
body+=f'<p><a href="{rel(B/"monster34/REVIEW.ko.md")}">검수 기록·실패 보존·남은 작업</a> · <a href="{rel(R/"chapter1/art/skeleton_outlaw/v02/ATTRIBUTION.ko.md")}">CC0 KevDev 출처</a> · <a href="candidate33.html">이전 후보33</a></p>'
t=re.sub(r'<title>.*?</title>','<title>후보34 · 잿빛 회랑 제1장</title>',t);t=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S);t=re.sub(r'<nav.*?</nav>','<nav aria-label="제작 항목"><a href="index.html">현재 후보</a><a href="monster34.html">근접 적 비교</a><a href="loot33.html">드롭</a><a href="flame33.html">화염</a><a href="equipment35.html">장비 그림 연구</a><a href="candidate33.html">이전 후보</a></nav>',t,flags=re.S).replace('v38 · 후보33','v39 · 후보34')
for name in ['index.html','candidate34.html']:(N/name).write_text(t,encoding='utf-8')
body='<h1>장비 그림35 · 네 슬롯의 작은 일러스트</h1><p class="lead">보상과 발견 화면의 단순한 기호를 대신할 새 그림을 준비했습니다. 현재 제품34에는 연결하지 않았습니다.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:16px">'
for name,label in [('weapon','지팡이'),('body','로브'),('ring','반지'),('charm','부적')]:body+=f'<figure><img style="width:96px;max-width:100%;height:auto" src="{rel(B/f"equipment35/svg01/proof/{name}.png")}" alt="{label}"><figcaption>{label}</figcaption></figure>'
body+='</div><p>프로젝트 자체 SVG 그림이며 외부 그림·글꼴·원격 리소스를 사용하지 않았습니다. 기존 네 슬롯의 표시만 개선하는 미술 시안으로, 아이템 종류나 능력치는 바꾸지 않습니다.</p><p>Godot의 SVG 파서로192×192렌더한그림을직접확인했습니다. 실제발견·보상UI에서작은크기의가독성과배치검수는아직남았습니다.</p><p><a href="candidate34.html">현재 후보34</a></p>'
s=re.sub(r'<main>.*?</main>','<main>'+body+'</main>',t,flags=re.S);(N/'equipment35.html').write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='Not run; prior kernel assets path error'),indent=2),encoding='utf-8');print(checks,refs)
