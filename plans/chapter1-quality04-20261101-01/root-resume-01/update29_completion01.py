from pathlib import Path
import json,hashlib,re,shutil,os
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';F=B/'full29';O=F/'runtime/default-profile-earn01'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
a=read(F/'performance/FINAL-THREE-RUNS01.json');s=read(O/'proof/RESULT.json');pins=read(O/'PROFILE-PINS.json')
assert a['target_met_all_three'] and s['saved'] and s['same_profile_after_reload'] and s['same_complete_core']
for n,h in pins['pins'].items():assert hashlib.sha256((Path(pins['path'])/n).read_bytes()).hexdigest()==h
note='''# 최신 재개 — 2026-11-04 / 후보29 전체 냉기·대표 성능3회·기본 저장 완료

현재 제품은 후보29 그대로다. 기존 후보14~29, 모든 stage·원시 성공/실패·소스·사용자23 저장을 보존한다. 전체 GPU session10115/PID24300과 기본저장 session60604/PID26504 모두 exit0/stderr0 종료, 현재 AshenCloister/Godot 프로세스 없음을 직접 확인했다. 같은 검사를 중복 실행하지 않는다.

전체 GPU: 정상 냉기90131/profileoff/실제1920×1080, 23862tick=397.7sim초/3451처치/Lv12/34장비, 원16과 전체core10필드 동일. 파쇄840/냉기사망823/224생성/3461 checkout/794소유표본 mismatch0. checkout은 첫 사용 포함. 27PNG 중 직접 검수한 것은210·270·330초와 승리후.35/.90/1.60초 총6장. 냉기 파편이 사체더미를 가리는 문제는 줄었고, 공격 부채꼴·보스 위험원과 장비 이름이 구분된다. 군중의 같은 체형 반복과 넓은 바닥의 단조로움은 여전히 개선 여지다. 정지화면만으로 동작 최종 승인하지 않는다.

성능: full29/performance/FINAL-THREE-RUNS01.json. 동일29 EXE/실제 냉기 메뉴 클릭/정상policy/focus/Forward+/RTX2070SUPER/MSAA2/VSync off/uncapped/10초warmup+60초OS monotonic intervals/측정 내 캡처·녹음·observer IO 없음. formal03/04/05 p95 9.581/9.545/10.138ms, p99 13.057/12.931/13.528ms, 최대52.779/51.921/63.115ms. 실제 전후1920×1080, reportedTexture2304×1296 별도 기록. 3회 target16.67 통과지만 간헐 hitch와 전체 후반 성능 보증은 별개. formal01 wrapper가 Actor25b를 잘못 기대한 실패·수정감사 보존, 시작 직후 warmup screenshot 때문에 최종3회 제외. formal02 메뉴 대기 후 세션 소실/원인 불명/프레임자료 없음으로 제외. 최종3회는03~05 연속 clean 실행이며 best-of 선별 아님.

기본 저장: full29/runtime/default-profile-earn01/proof/RESULT.json. 실제29 EXE/headless fixed60/처음 기본profile없음/정상획득 전체23862tick/원래 저장 이벤트, 기본 user:// 경로 재configure 후 전체 상태 일치. 34장비/완료1/revision1/겨울의심장 storage34. profileoff false/우회경로·장비지급 없음. 새 실제 사용자29 파일과 journal은 default-profile-preserved 및 PROFILE-PINS에 보존. C:/Users/twins/AppData/Roaming/AshenCloisterChapterOneQuality29/chapter-one-profile-v1.json 절대 reset/delete 금지. GPU·수동 검사가 아닌 기본 저장 파이프라인 증거다.

다음: 실제29 메뉴 보관함의 획득장비 선택→저장→다시 실행→새 도전 시작능력 반영을 검수한다. 기존23의 native 성공을29 증거로 확대하지 않는다. 도감v29는 새 결과 반영본이며 브라우저 검수는 아직 pending. 정상속도 수동 전체·실청취·최종 전투/공간 질감 판정은 남아 있다. 같은 긴 입력왕복 수동패배 방식 반복 금지. 목표 active, 2·3장 미착수.

---
'''
p=R/'HANDOFF.md';p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=F/'STATUS.ko.md';p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
(O/'REVIEW.ko.md').write_text(note.split('기본 저장:')[1].split('다음:')[0],encoding='utf-8')
p=F/'runtime/WHOLE-COLD-REVIEW.ko.md';p.write_text(p.read_text(encoding='utf-8')+'\n추가 직접 검수:210초·330초 두 장을 더 열었다. 총6장. 210초 돌진 부채꼴과 냉기파편,330초 보스 위험원/체력막대/바닥 이름이 구분된다. 동일체형 반복·넓은 바닥 단조로움은 남음. 최종 대표성능3회와 기본저장 검증은 위 최신 STATUS 별도 완료 근거를 따른다.\n',encoding='utf-8')
old=F/'book-v28/dist';new=F/'book-v29/dist';assert not new.exists();shutil.copytree(old,new)
for p in new.glob('*.html'):
 text=p.read_text(encoding='utf-8')
 def fix(m):
  k,v=m.groups()
  if v.startswith(('http:','https:','#','data:')):return m.group(0)
  raw,sep,anchor=v.partition('#');t=(old/raw).resolve()
  if not t.is_relative_to(old.resolve()):v=os.path.relpath(t,new).replace('\\','/')+(sep+anchor if sep else '')
  return k+'="'+v+'"'
 text=re.sub(r'(src|href)="([^"]+)"',fix,text).replace('v28 · 후보29','v29 · 후보29')
 if p.name=='candidate29.html':
  text=re.sub(r'<h2>전체 장 검수 진행</h2>.*?<p>독립보존감사', '<h2>전체 냉기 전투와 보상</h2><p>정상 성장으로 6분37.7초에 첫 장을 마쳤습니다. 3451처치와 34개 장비, 냉기 파쇄840회를 확인했습니다. 실제 GPU 전투와 보스 붕괴·겨울의 심장 보상 화면을 검수했습니다.</p><h2>실제 1080p 성능과 저장</h2><p>같은 제품의 대표60초 측정3회 p95는9.581/9.545/10.138ms입니다. 최장63.115ms 지연이 있어 끊김이 전혀 없다고 하지는 않습니다. 기본 저장에는 정상 획득 장비34개와 완료기록1회가 남고 재로딩 상태가 일치했습니다. 수동 완주와 실제 청취, 최종 질감 판단은 남아 있습니다.</p><p>독립보존감사',text,flags=re.S)
 p.write_text(text,encoding='utf-8')
missing=[];refs=0
for p in new.glob('*.html'):
 for v in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if v.startswith(('http:','https:','#','data:')):continue
  refs+=1
  if not (p.parent/v.split('#')[0]).exists():missing.append([p.name,v])
assert not missing
(new.parent/'BUILD.json').write_text(json.dumps(dict(html=len(list(new.glob('*.html'))),references=refs,missing=missing,browser_review='pending'),indent=2))
print('HANDOFF STATUS SAVE REVIEW BOOK29 UPDATED',refs)
