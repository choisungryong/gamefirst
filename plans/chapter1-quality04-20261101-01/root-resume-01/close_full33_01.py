from pathlib import Path
import json,hashlib,re,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full33';P=O/'runtime/gpu-fire01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=read(O/'ADOPTION.json');assert all(sha(R/n)==h for n,h in read(O/'FINAL-SOURCE-FREEZE.json').items());assert all(sha(R/n)==h for n,h in a['preserved_exes'].items());assert all(sha(Path(n))==h for n,h in a['user_pins'].items());r=read(P/'RESULT.json');assert all(r['same10_as_packaged16'].values())
p=O/'STATUS.ko.md';assert not p.exists();p.write_text('''# 후보33 · 실제 전체 화염 종료

Core16/World31d/Actor32b/HUD27/Input21/FX33b. EXE SHA f22c74d623a2dc1c62a870a9fabcc74f2d38c0bb5d881e8e1218cf52d8f5679d/130087672bytes/runtime135-stage137-PCK246. 세로화염높이/잔연기감소와바닥드롭등급위계. 상세source비교는loot33/REVIEW.ko.md 및flame33/REVIEW.ko.md.

실제GPU 전체화염 session45133/PID5240 종료,exit0-stderr0/RESULT완료. 정상정책21749tick=362.48sim초(약6분2초)/3185처치/Lv11/장비23. 기존16 release 정상화염과 mode/tick/kills/hero/growth/metrics/chapter/equipped/inventory/elite_reward_uid10필드같음. 세구역World31d/33기둥/2shadowbatch활성,724회표시소유권표본불일치0/풀224/3189checkout(첫사용포함,순수재사용횟수아님). 실제ground UID31개의common/magic/rare등급표시와새FX33b로드확인/동시세로화염peak8. 자연unique바닥드롭을확인한것이아님.

25PNG중150초·330초·승리후.35/.90/1.60초 총5장직접검수. 화염속주인공상체·적외곽유지,보스쓰러짐뒤보상카드읽힘. 나머지20장전부직접검수주장금지. 정상자동정책이며수동전체·실청취·정식1080p성능은아님. 보스체형/일반적같은계열반복과보상아이콘미술은최종질감개선여지남음.

기존후보EXEs·사용자23복원후·29rev2/journals/root33핀재확인. 모든이번Godot종료/같은완료검사중복실행금지. full30/book-v37 최신표지는현재후보와6개항목으로간결히정리,이전판보존. 브라우저/WindowsUI tool kernel assets path error로실제브라우저·새기본입력·수동검수미완료. 코드/파일/GPU검사는계속가능. 수동검수에는외부UI연결복구필요. 목표active/추가툴·Github보류.

다음은기존보존 SkeletonOutlaw 자료로다른몸실루엣/저작된보행·공격을활용할수있는지확인한다. CC0 KevDev/source.html·SOURCE.json·원ZIP·conversion02·preview03보존. 아직제품에복사/연결안함. 서로다른6skin의57bind와8mesh/9clip이므로Mophs리그를그대로대입하거나무검수채택금지. 최종수동전체/실청취/같은제품focused성능·최종아트는여전히남음.
''',encoding='utf-8')
p=B/'loot33/REVIEW.ko.md';p.write_text(p.read_text(encoding='utf-8')+'\n## 실제 전체 종료\n\nfull33/STATUS.ko.md 참조. session45133 exit0-stderr0/21749tick/3185kills/Lv11/장비23/원16화염10필드같음.25PNG중5직접검수/보스.35-.90-1.60초마무리확인/31groundUID의3실제등급표시/소유권724표본불일치0. 전수이미지·수동·실청취·정식성능승인아님. 같은실행재시작금지.\n',encoding='utf-8')
p=R/'HANDOFF.md';p.write_text('# 최신 · 후보33 전체GPU 종료 / 같은검사 재실행 금지\n\nfull33/STATUS.ko.md 먼저읽는다. session45133/PID5240 terminal exit0-stderr0/RESULT완료. 정상화염21749tick(6분2초)/3185kills/Lv11/장비23/원16release10필드같음.25PNG중5직접검수/보스쓰러짐→보상카드확인. actualFX33b/ground31UID3등급/724표시소유권표본불일치0. 기존EXEs·사용자23복원후/29rev2·root33핀보존. 제품33·도감v37갱신/로컬서버PID8528재사용(확인후)/UI도구커널경로오류라새수동입력·브라우저미검수. 다음원목표동작개선자료: C:/Project/game-research/art-sources/oga-skeleton-outlaw-20261101-01의source/converted02/preview03 읽기확인,3PNG직접검수/CC0 KevDev/다른몸실루엣/9authoredclips. 아직제품복사·연결·새검사안함.6skin57bind/8mesh주의. 목표active/최종수동·실청취·focused성능·최종질감미완료. 추가툴·Github보류.\n\n---\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
N=B/'full30/book-v37/dist';rel=lambda p:os.path.relpath(p,N).replace('\\','/')
for name in ['index.html','candidate33.html']:
 p=N/name;s=p.read_text(encoding='utf-8');s=s.replace('후보33 실제 실행 파일의 전체 화염 빌드 검수가 진행 중입니다. 종료 후 보스 마무리와 보상 화면을 확인합니다.','후보33 실제 실행 파일로 정상 화염 빌드 전체를 진행해 약6분2초에 보스를 처치했습니다. 3185처치·레벨11·장비23개, 기존 정상 전투 상태와의 일치와 오류 없는 종료를 확인했습니다. 자동 정책 실행으로 수동 플레이와는 구분합니다.')
 body='<h2>실제 후보33 · 보스에서 보상으로</h2>'
 for f,c in [('victory-after-0.90.png','보스가 쓰러진 뒤 전장을 정리하는 순간'),('victory-after-1.60.png','마무리 뒤 확인하는 고유 장비 보상')]:body+=f'<figure><img loading="lazy" src="{rel(P/"captures"/f)}" alt="{c}"><figcaption>{c} · 실제 후보33 정상 화염 빌드 전체 실행</figcaption></figure>'
 body+=f'<p><a href="{rel(O/"STATUS.ko.md")}">현재 검수와 남은 작업</a> · <a href="{rel(P/"RESULT.json")}">실제 전체 결과</a></p>'
 s=s.replace('</main>',body+'</main>');p.write_text(s,encoding='utf-8')
missing=[];refs=0
for p in N.rglob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([str(p.relative_to(N)),v])
assert not missing,missing
(N.parent/'FINAL-LINK-AUDIT01.json').write_text(json.dumps(dict(html=len(list(N.rglob('*.html'))),references=refs,missing=missing,browser_review='Not run; kernel assets path error'),indent=2),encoding='utf-8');print('FINAL BOOK LINKS',refs)
