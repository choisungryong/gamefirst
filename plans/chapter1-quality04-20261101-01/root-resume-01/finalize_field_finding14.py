from pathlib import Path
import json,shutil
ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/full14';BOOK=OUT/'book-v07/dist'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
rows=(OUT/'cold-observer01/stdout.txt').read_text(encoding='utf-8').splitlines();observed=read(OUT/'cold-observer01/RESULT.json');assert observed['observed']['shatter_events']==0
state=next(json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1])for s in rows if 'FULL_CHAPTER_RUNTIME_RESULT 'in s and json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1])['mode']=='victory')
gpu=read(OUT/'GPU-COLD-RESULT.json')['result'];keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];same={k:state[k]==gpu[k]for k in keys};assert all(same.values())
p=OUT/'cold-observer01/CORE-COMPARISON.json';assert not p.exists();p.write_text(json.dumps({'same_gpu14':same,'scope':'Observer gameplay matches recorded GPU14. Event frequency is passive headless proof, not another GPU/manual/performance run.'},indent=2),encoding='utf-8')
back=OUT/'book-v07/revision-03-before';back.mkdir()
for n in ['index.html','elements.html','validation.html','profile.html']:shutil.copy2(BOOK/n,back/n)
shutil.copy2(OUT/'STATUS.ko.md',OUT/'STATUS-before-field-finding.ko.md')
p=OUT/'STATUS.ko.md';s=p.read_text(encoding='utf-8')
s=s.replace('정상필드빙결/파쇄가연구배치보다드물게보여별도읽기전용observer로빈도를추적중이며추가판정한다.','실제읽기전용observer도같은10전투상태를유지했으며,정상한판의실제shatter는0회/살아있는일반적빙결tick합0/정예빙결545틱/최대동시1/얼음최대4였다. 따라서연구배치의화려함은실전일반무리에서재현되지않았고이품질은미달이다. COLD-FIELD-FINDING.ko.md를따른다.15별도연구소스는진화냉기실제처치에얼음잔해를연결하며추가빙결/피해를만들거나이를실제파쇄proc로부르지않는다. 루트preload/14freeze는유지하고15정상기본HP/획득성장GPU190초부분실행을별도stage에서검증중이다.')
s+='\n다음우선순위정정: 일반/정예모델보다먼저정상냉기처치/성장체감을개선한다.15연구는chapter1/view/chapter_elements_quality15.gd와elements15/normal01/을따르며아직15EXE/전체한판완료가아니다. 이후일반/정예·공간·파밍/보상UX와수동전체/실청취/정식성능을진행한다.\n';p.write_text(s,encoding='utf-8')
warning='<p class="note">정상 냉기 한 판을 추가 추적하니 실제 파쇄는0회였고, 살아 있는 일반 적의 빙결도 없었습니다. 아래 지급 빌드 연구의 화려함이 실전 무리에서는 아직 재현되지 않았습니다.15에서 실제 진화 냉기 처치의 얼음 잔해를 먼저 개선하고 있습니다. <a href="../../COLD-FIELD-FINDING.ko.md">원인과 실제 수치</a></p>'
for n in ['index.html','elements.html','validation.html']:
 p=BOOK/n;s=p.read_text(encoding='utf-8');at=s.index('</h1>')+len('</h1>');s=s[:at]+warning+s[at:];p.write_text(s,encoding='utf-8')
p=BOOK/'profile.html';s=p.read_text(encoding='utf-8').replace('결과</a></p>','결과</a> · <a href="../../profile-process02/PATH-CORRECTION.json">실제 QA 경로 정정</a></p>',1);p.write_text(s,encoding='utf-8')
p=OUT/'SACRATA-COMPARISON.ko.md';s=p.read_text(encoding='utf-8');s+='\n정상필드추적추가: 같은GPU결과10항목을보존하는observer에서실제파쇄0회/일반적살아있는빙결0틱으로확인했다. 연구HP140과달리기본HP12/18은28피해에한번에죽어조건에들어가지않는다. COLD-FIELD-FINDING.ko.md의한계를반영해다음작업은일반모델보다15의실제냉기처치피드백이다. 처치잔해연출과실제빙결/파쇄피해규칙을구분하고수치조작으로성공장면을만들지않는다.\n';p.write_text(s,encoding='utf-8')
print(json.dumps({'actual_shatter':0,'observer_core_matches':same,'goal':'active'}))
