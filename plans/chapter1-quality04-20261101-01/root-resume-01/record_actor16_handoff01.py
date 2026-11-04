from pathlib import Path
import json,hashlib,shutil
ROOT=Path('C:/Project/d2r-combat-baseline'); BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'cold16/actors01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((BASE/'full14/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
archive=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-14')
archive_pins=json.loads((BASE/'full14/build/staging-manifest.json').read_text(encoding='utf-8'))
assert all(sha(archive/n)==h for n,h in archive_pins.items())
exe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'
assert sha(exe)=='5fa58077545ea3cc3c0d55bc6abbd5bc57eab32bdd78c8ccdbfa398ca28f5952'
assert all(json.loads((BASE/'cold16/actor-exclusions04/RESULT.json').read_text()).values())
backup=OUT/'HANDOFF-before-actors01.md';assert not backup.exists();shutil.copy2(ROOT/'HANDOFF.md',backup)
header='''# 최신 재개 — cold16 일반 냉기 사체 겹침 개선 구현/격리 검증

먼저 `plans/chapter1-quality04-20261101-01/cold16/actors01/REVIEW.ko.md`와 `RESULT.json`, `cold16/actor-exclusions04/RESULT.json`을 읽는다. 후보14 EXE/전체 freeze 및 루트 조립은 그대로다. 새 파일 `chapter1/view/chapter_actors_quality16.gd`가 이제 존재한다. 아래 이전 인계의 “없음/미구현”은 과거 상태다.

Actor12 상속, 실제 frost death의 죽은 일반 entity만 generation:id/seq로 추적. 푸른 색 .025초 유지 후 .22초 fade. 부모 sync가 매번 기본 색/owner alpha를 재계산한 뒤 한번 적용한다. paused/choice/inventory/equipment 시간 정지, terminal 시간 진행, reset clear. 정예 플래그/elite 종류와 비냉기 제외. core 피해/충돌/보스/영웅/FX .48초 파편 그대로. root preload는14 유지, 새16 EXE 아직 없음.

actors01은 정상 full_pilot/defaultHP/실제획득성장/seed90131의 core를 tick3240까지 재시뮬레이션 후 cosmetic 초기화하고 8초 GPU fixed60으로 전후 재생했다. 양쪽 모두16 규칙이며 전체 core snapshot 시작/종료 동일. 전후 import/check/GPU 모두 exit0/stderr0. 32 PNG. shatter02 after15의 중앙 갈색 사체 덩어리가 제거되고 얼음 파편/생존 적/바닥이 드러남을 직접 확인했다. after06/30도 확인했다. 8개 modal/tint/terminal/dedupe/reset/core 검사 통과. 전체 실시간/수동/음향/성능/최종아트 승인은 아니다.

별도 제외 fixture 8개는 actor-exclusions04에서 모두 true/import0/실행0/stderr0. 앞선01과03은 검사 true/exit0이나 ObjectDB 종료 경고124bytes,02는 import3221225477/stderr0 실패였다. 원본 stage/log 모두 보존. helper에 종료 전 audio.reset과4프레임 대기를 넣었으나03에도 경고가 있었으므로 원인/해결을 확정하지 않는다.04는 verbose 실행의 깨끗한 한 번 성공이며 장기 누수 검증이 아니다. hero_never_tracked는 reset 뒤 빈 기록 확인일 뿐 별도 영웅 사망 fixture가 아니다.

새 stage는 `C:/Project/game-research/build-staging/chapter1-cold16-actors01-before`, `...-after`, `chapter1-cold16-actor-exclusions01..04`. 모든 실행 terminal, 재사용/덮어쓰기 금지. helper는 root-resume-01/cold_actor16_replay.gd,run_cold_actor16_01.py,cold_actor16_exclusions.gd,run_cold_actor16_exclusions04.py. 보존 확인은 actors01/FINAL-PRESERVATION.json.

다음은 필요시 .00/.06부분 프레임의 시각 추가 검토 후14 백업을 확보하고16 core/FX/HUD/Actor의 새 closure/freeze/candidate EXE와 전체 정상 GPU/보스/보상 검증으로 이어간다. 기존14를 덮어쓰지 않는다. 첫 장 목표 active이며2·3장 미착수. 아래 이전 기록을 그대로 보존한다.

---

'''
header=header.replace('후보14 EXE/전체 freeze 및 루트 조립은 그대로다.','후보14 EXE/보관14stage 전체 freeze는 일치한다. 아래 루트/패키징 상태에는 동시 변경 주의가 필요하다.')
header=header.replace('root preload는14 유지, 새16 EXE 아직 없음.','이번 격리 작업은 root preload/EXE를 변경하지 않았다. 그러나 최종 점검에서 별도 동시 작업으로 root preload 4개가16에 연결되고 후보16 EXE가 실행 중인 것을 발견했다. 이 프로세스/패키지의 완료나 품질은 이 작업에서 검증하지 않았다.')
header=header.replace('다음은 필요시 .00/.06부분 프레임의 시각 추가 검토 후14 백업을 확보하고16 core/FX/HUD/Actor의 새 closure/freeze/candidate EXE와 전체 정상 GPU/보스/보상 검증으로 이어간다.','다음은 먼저 동시 패키징 작업의 상태와 실제 actor 소스핀을 확인하고, 중복 실행 없이16 closure/freeze/EXE 및 전체 정상 GPU/보스/보상 검증을 이어간다.')
(ROOT/'HANDOFF.md').write_bytes(header.encode('utf-8')+backup.read_bytes())
report={'candidate14_exe_sha256':sha(exe),'freeze_files':len(archive_pins),'all_archived14_freeze_files_match':True,'root_freeze_differences':[n for n,h in freeze.items() if sha(ROOT/n)!=h],'new_actor_sha256':sha(ROOT/'chapter1/view/chapter_actors_quality16.gd'),'old_handoff_sha256':sha(backup),'handoff_preserves_exact_suffix':(ROOT/'HANDOFF.md').read_bytes().endswith(backup.read_bytes()),'scope':'Archived14 preservation and narrow visual change; concurrent root16 integration/package observed, not verified by this worker.'}
(OUT/'FINAL-PRESERVATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)

