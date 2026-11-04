from pathlib import Path
import json,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full14';GPU=OUT/'runtime/gpu-cold01';BOOK=OUT/'book-v07/dist'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
execution=read(GPU/'execution.json');assert execution['actual_exit']==0 and execution['stderr_bytes']==0 and execution['capture_count']==24
comparison=read(OUT/'cold-reference13/COMPARISON.json');assert all(comparison['same'].values())
result=comparison['after14'];assert result['mode']=='victory'and result['tick']==24749 and result['kills']==3632
lines=(GPU/'stdout.txt').read_text(encoding='utf-8').splitlines();deaths=[json.loads(s.split('CHAPTER1_WARDEN_DEATH_POSE ',1)[1])for s in lines if 'CHAPTER1_WARDEN_DEATH_POSE 'in s];assert len(deaths)==1 and deaths[0]['visual_age']>=deaths[0]['clip_length']
write(OUT/'GPU-COLD-RESULT.json',{'actual_exit':0,'stderr_bytes':0,'capture_count':24,'result':result,'same_input_comparison13':comparison['same'],'terminal_death':deaths,'visual_review':{'reviewed':['run-001-frame-210.png','run-001-frame-390.png'],'finding':'Cold lance body/white nose, inherited hero/boss and ward danger readable in these frames; frozen/shatter spectacle appears much less frequent than configured arena, so passive actual-event observer is being collected before claiming real build feedback.','not_final_art_approval':True},'scope':'Actual packaged14 GPU/default difficulty/normal policy/profileoff/maxfps120; seed90131. Before13 reference same seed headlessfixed60. Old09cold used71, not same-seed improvement. Not manual/heard audio/performance/storage UI proof.'})
rev=OUT/'book-v07/revision-02-before';rev.mkdir()
for n in ['index.html','validation.html','profile.html']:shutil.copy2(BOOK/n,rev/n)
shutil.copy2(OUT/'STATUS.ko.md',OUT/'STATUS-initial-GPU-pending.ko.md')
p=OUT/'STATUS.ko.md';s=p.read_text(encoding='utf-8')
s=s.replace('실제GPU냉기정상전체는runtime/gpu-cold01/에서진행중이며종료후GPU-COLD-RESULT.json으로확정한다. 이문장의진행중을전체완료로확대하지않는다.','실제GPU냉기정상전체도24749틱/412.4833초(6분52초)/3632처치/Lv12승리/24PNG/종료0/stderr0다. 같은90131시드의실제13패키지headless참조와10전투상태동일. 옛09냉기는seed71이므로427초와개선율/동일시드비교하지않는다. GPU-COLD-RESULT.json을따른다. 정상필드빙결/파쇄가연구배치보다드물게보여별도읽기전용observer로빈도를추적중이며추가판정한다.')
s+='\n추가 저장 증거: profile-process02/RESULT.json의31검사/독립3프로세스/종료0/stderr0. 실제기본user://경로에서고유3장비선택을저장하고새프로세스가읽어실제ChapterRun에적용(화염2발),영수증재생무변경/패배후시작장비중복없음/다시재시작후3개유지를확인했다. 고유QA사용자namespace B이며사용자본래저장미접근. MSIX리디렉션의실제경로는PATH-CORRECTION.json이권위있고,잘못가정한수집경로/프로브예약어실패는보존했다. 이는백엔드재시작증거이며네이티브보관함UI·동시CAS·전원손실승인이아니다.\n'
p.write_text(s,encoding='utf-8')
shutil.copy2(GPU/'captures/run-001-frame-390.png',BOOK/'scenes/cold14-normal390.png')
p=BOOK/'index.html';s=p.read_text(encoding='utf-8').replace('아래 첫 화면은 지급한 성장 빌드의 비교용 배치이며 정상 한 판을 이긴 장면과 구분합니다.','정상 냉기 한 판은6분52초·3632처치로 완료했습니다. 전후 연구 영상의 지급 빌드는 별도로 표시합니다.')
s=s.replace('scenes/frost-after14.png','scenes/cold14-normal390.png')
s=s.replace('수정14 · 실제 core 이벤트가 발생하는 연구 배치.80적/적140HP·영웅5000HP·지급 진화 냉기4. 정상 전투의 난이도/획득 성장/성능 증거가 아닙니다.','후보14 실제 패키지GPU · 정상 냉기 빌드의6분29초 보스전. 자동 입력/저장off이며 수동 한 판·실제 성능 승인과 구분합니다.')
p.write_text(s,encoding='utf-8')
p=BOOK/'validation.html';s=p.read_text(encoding='utf-8').replace('실제14 패키지·기본 난이도·정상 자동 입력·저장off로 진행 중입니다. 종료 후 상태 보고서에 확정합니다. 지급 빌드 연구와 섞지 않습니다.','실제14 패키지·기본 난이도·정상 자동 입력·저장off로6분52초/3632처치/Lv12완료,종료0/stderr0/24PNG입니다. 같은 시드90131의13패키지와10전투상태가 같습니다. 빙결/파쇄의 실제 필드 빈도는 별도 추적하고 있어 연구 영상의 화려함을 정상 한 판 전반의 체감으로 확대하지 않습니다.')
s=s.replace('<h2>보존한 실패</h2>','<p><a href="../../GPU-COLD-RESULT.json">정상 냉기GPU 결과</a></p><h2>세 프로세스 저장 재시작</h2><p>별도QA 기본user경로에서31검사/3프로세스가3장비·선택·영수증을 유지하고 실제 새ChapterRun에 적용했습니다. 패배 후 시작 장비 중복도 없었습니다. 네이티브 보관함UI/동시CAS/전원손실 승인은 아닙니다.</p><p><a href="../../profile-process02/RESULT.json">백엔드 재시작 증거</a></p><h2>보존한 실패</h2>')
p.write_text(s,encoding='utf-8')
p=BOOK/'profile.html';s=p.read_text(encoding='utf-8').replace('</h1>','</h1><p class="note">14 추가 검수: 실제 기본user경로를 쓰는 독립3프로세스/31검사에서3장비 선택·새전투 적용·중복방지·다시재시작을 확인했습니다. 별도 QA namespace이며 네이티브 보관함UI·저장 경쟁 구간·전원손실은 여전히 미검수입니다. <a href="../../profile-process02/RESULT.json">결과</a></p>',1);p.write_text(s,encoding='utf-8')
print(json.dumps({'seconds':result['tick']/60,'kills':result['kills'],'same13':comparison['same'],'profile_checks':31}),flush=True)
