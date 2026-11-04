from pathlib import Path
import json,hashlib,shutil,re
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full13';GPU=OUT/'runtime/gpu-full01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def lines(p,marker):return[json.loads(s.split(marker,1)[1])for s in p.read_text(encoding='utf-8').splitlines()if marker in s]
execution=read(GPU/'execution.json');assert execution['actual_exit']==0 and execution['stderr_bytes']==0 and execution['capture_count']==22
victory=next(r for r in lines(GPU/'stdout.txt','FULL_CHAPTER_RUNTIME_RESULT ')if r['mode']=='victory')
old=read(BASE/'full11/GPU-FULL-RESULT.json')['result']
keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid']
same={k:victory[k]==old[k]for k in keys};assert all(same.values()),same
deaths=lines(GPU/'stdout.txt','CHAPTER1_WARDEN_DEATH_POSE ')
assert len(deaths)==1 and deaths[0]['mode']=='victory'and deaths[0]['visual_age']>=deaths[0]['clip_length']
rigs=lines(GPU/'stdout.txt','CHAPTER1_WARDEN_RIG ');assert len(rigs)==1 and rigs[0]['bones']==73
write(OUT/'GPU-FULL-RESULT.json',{'actual_exit':0,'stderr_bytes':0,'capture_count':22,'same_gameplay_as11':same,'result':victory,'warden':rigs,'terminal_death':deaths,'visual_review':{'reviewed':['run-001-frame-330.png','state-0012-run-001-victory.png'],'finding':'Boss body/mask readable through surrounding fire at same330s instead of false-positive ghosting in normal05. Immediate victory modal still weakens death/reward staging. GPU09 separately shows terminal death pose.','not_final_art_approval':True},'scope':'Actual packaged13 RTX2070SUPER/Forward+ normal policy, max-fps120/profile off/captures. No manual whole run, heard audio, storage IO or formal performance approval.'})
oldgpu=BASE/'boss-research12/normal05'
v=next(r for r in lines(oldgpu/'stdout.txt','FULL_CHAPTER_RUNTIME_RESULT ')if r['mode']=='victory')
eq={k:v[k]==old[k]for k in keys};assert all(eq.values())
write(oldgpu/'RESULT-REVIEW.json',{'execution':read(oldgpu/'execution.json'),'same_gameplay_as11':eq,'result':v,'scope':'Source/debug GPU normal driver. Functional success but visual boss opacity/death defects; not adopted visual approval. Comparison with13 is same330s scene, different nearby render frames.'})
rev=OUT/'book-v06/revision-02-before';rev.mkdir()
for n in ['index.html','validation.html']:shutil.copy2(OUT/'book-v06/dist'/n,rev/n)
shutil.copy2(OUT/'STATUS.ko.md',OUT/'STATUS-initial-GPU-pending.ko.md')
p=OUT/'STATUS.ko.md';s=p.read_text(encoding='utf-8')
start='실제 패키지 GPU 전체는';end='모델은 Mophs/Chained Demon'
a=s.index(start);b=s.index(end,a)
s=s[:a]+'''실제 패키지 GPU 전체도 종료0/stderr0/22PNG로 완료했다. 첫 승리21749틱/362.4833초/3185처치/Lv11이며 후보11 첫 자동 승리의10개 전투 상태 항목이 모두 같다. 실제GPU에서도 승리 후 사망 클립1.125초 끝을1.1362초에 통과했다. root는 같은330초 전투 화면에서12의 희미한 보스가13에서는 선명하게 남는 것을 확인했다. 다만 승리 모달이 즉시 화면을 덮어 처치→보상 리듬이 약한 점은 남는다. `GPU-FULL-RESULT.json`을 따른다. 자동 입력/저장off이며 수동 전체·실청취·저장IO·정식 성능 승인과 구분한다.

도감v06은9페이지이며 기존11의 항목/화면·영상 번호를 유지하고 파수왕 페이지를 추가했다. 초기BUILD/진행 중 문서를 보존한 뒤 새13의 실제GPU 결과로 갱신했다. 브라우저 검수와 최종 로컬 참조 감사는 `book-v06/BROWSER-QA.json`과`REVISION-02.json`을 따른다.

'''+s[b:];p.write_text(s,encoding='utf-8')
p=OUT/'book-v06/dist/index.html';s=p.read_text(encoding='utf-8')
s=s.replace('5–8분</strong>첫 장 목표 · 전체 패키지 재검수 중','6분2초</strong>패키지 실제GPU 정상 입력 완료')
shutil.copy2(GPU/'captures/run-001-frame-330.png',p.parent/'scenes/boss13-actual330.png')
s=s.replace('scenes/warden-front_clear5m.png','scenes/boss13-actual330.png')
s=s.replace('현재13 표현 · GPU09 배치 검사. 실제 보스전을 이긴 장면이 아닙니다. 영웅 앞5m에서 불필요하게 투명해지지 않는지 확인했습니다.','후보13 실제 패키지 GPU · 게임5분29초 보스전. 정상 자동 입력이며 수동 전체 플레이/성능 승인은 아닙니다.')
p.write_text(s,encoding='utf-8')
p=OUT/'book-v06/dist/validation.html';s=p.read_text(encoding='utf-8').replace('실제GPU 전체 실행 결과는 별도 보고서로 확정합니다.','실제GPU 전체도 종료0/stderr0/22PNG, 같은6분2초 승리와 사망 클립 완료를 확인했습니다. 후보11 첫 자동 승리와10개 전투 상태 항목이 같습니다. 자동 입력/저장off이며 수동 전체·실청취·정식 성능 승인이 아닙니다.')
s=s.replace('<h2>보스 표현 검사</h2>','<p><a href="../../GPU-FULL-RESULT.json">실제 패키지 GPU 결과/화면 판정</a></p><h2>보스 표현 검사</h2>');p.write_text(s,encoding='utf-8')
print(json.dumps({'same':same,'seconds':victory['tick']/60,'terminal':deaths,'book_updated':True},ensure_ascii=False))
