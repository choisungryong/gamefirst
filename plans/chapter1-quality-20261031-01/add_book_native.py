from pathlib import Path
import json, hashlib, shutil
ROOT=Path(__file__).resolve().parents[2]
PROOF=Path(__file__).resolve().parent
NATIVE=PROOF/'native-runtime-03/native-20261101-01'
DIST=PROOF/'book-v03/dist'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writej(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    execution=json.loads((NATIVE/'EXECUTION.json').read_text(encoding='utf-8'))
    assert execution['actual_exit']==0
    assert (NATIVE/'stderr.log').stat().st_size==0
    caps=ROOT/'builds/chapter1/chapter1-c2-candidate-20261101-03/qa-captures/native-20261101-01'
    dest=NATIVE/'captures';dest.mkdir(exist_ok=True)
    for filename,pin in execution['captures'].items():
        assert sha(caps/filename)==pin['sha256']
        if (dest/filename).exists():assert sha(dest/filename)==pin['sha256']
        else:shutil.copy2(caps/filename,dest/filename)
        assert sha(dest/filename)==pin['sha256']
    results=[]
    for line in (NATIVE/'stdout.log').read_text(encoding='utf-8').splitlines():
        if line.startswith('CHAPTER1_RUNTIME_RESULT '):results.append(json.loads(line.split('CHAPTER1_RUNTIME_RESULT ',1)[1]))
    assert results[0]['elapsed']==17.85 and results[0]['kills']==80 and results[0]['hp_raw']==0 and results[0]['pilot']==False
    observation='''# 후보03 root 네이티브 조작 관찰

2026-11-01, Asia/Seoul. **실제 OS 입력은 root가 CUA로 직접 수행했다. 이 보고서 작성자는 root의 관찰 전달, 실제 실행 로그·20PNG와 해시를 읽어 정리했다.** 작성자의 자동 입력/합성 fixture를 수동 플레이로 표시하지 않는다.

동일 후보03 EXE SHA256 `c916e280facbc89c6fcb1b21ee9a3fc9725313e248956e1918342ac2d4602fbb`,1440×810/Forward+다. autostart/pilot/ignore-focus는 켜지 않았다. EXECUTION.json의 실제 exit0, stderr0bytes. 원시 시작/종료는 UTC2026-10-31 18:22:38.664101→18:26:25.047907, 한국시간2026-11-01 03:22:38→03:26:25다. 벽시계 약226초는 UI 관찰/모달을 포함하며 전투 플레이 길이가 아니다.

## 직접 확인한 입력과 결과

| 조작/상태 | root의 실제 관찰 |
|---|---|
| 메뉴 | 시작3버튼/안내가1440×810 안에 들어옴. 화면 흔들림 checkbox를 끄고 화염으로 시작. HP120/120. |
| 성장·정지 | 8초/8처치/Lv2/HP65에서 성장. Esc로 정지 후 Esc로 같은 성장 화면 복원. 화염2 선택. |
| 회피 | Space 입력 뒤 대기1.3초 표시를 봄. 장기 이동·무적 전 구간의 수동 증명은 아님. |
| 무기 | 12초/20처치/HP25에서 성장 중 I로 장비 열기. 균열의 잿불 가지 피해+14%/발사체+1을 장착했고 HP25 유지. I로 성장 화면 복귀. |
| 갑옷 | 화염3,14초/52처치/Lv4/HP15. 수호의 재옷 최대HP+34/피해감소7% 장착 후15/120→15/154, 현재HP 회복 없음. I로 원래 성장 복귀. |
| 성장·음소거 | 화염4와 패시브 선택. M 뒤 소리 꺼짐 toast 확인. 실제 청취 승인은 아님. |
| 실제 패배 |17.85초/80처치/Lv5/소유3개/HP0raw, HUD0/154. 화염4·패시브1, 진화없음. |
| 재도전 | R 후 Esc로00:00/0처치/Lv1/HP120/120을 확인. 이번 런 장비가 초기화됨. |
| 종료 | 창 X로 닫고 실제 exit0 및 앱 창 부재 확인. |

root의 당시 CUA 화면 관찰에는 장착 직후 변화도 포함되지만, 자동 모드 PNG는 모든 장착 클릭 직후를 따로 캡처하지 않는다. `state-0008`은 무기 장착 전 비교, `state-0012`는 갑옷 선택 전 인벤토리, `state-0013`은 장비 창을 닫은 성장 화면, `state-0017`은 패배, `state-0019`는 재도전 직후 정지를 보여준다.20PNG 원본은 실행본 qa-captures에 남기고 이 폴더의 captures에 동일 해시 사본을 보존했다.

실제 로그는 elapsed17.85/kills80/xp69/Lv5/hp_raw0, fire rank4/passive embers/evolved[], picked_items3, casts17/hits82, max_alive60, peak_projectiles16, enemy_attacks162다. _frame_ms의 p9516.667ms/1019표본은 이 짧은810p 실행의 모달·캡처 조건 결과이며 정식1080p 성능 통과가 아니다.

## 한계와 품질 관찰

일반 입력의 정지·장비·성장·패배·재도전 경계를 확인했지만, 진화/세 기술 동시 사용/정예 승리를 수동으로 완료하지 않았다. OS WASD hold, 긴 좌클릭 이동, 별도 초점 상실, 실제 청취도 이 실행의 확정 항목이 아니다.17.85초 패배는 도구로 UI를 천천히 관찰하며 주로 정지한 실행이므로 일반 플레이 승률·난이도 판정으로 확대하지 않는다.

root는 영웅 주변에 적이 겹쳐 실루엣을 가리는 문제를 직접 봤다. 초반 성장 화면이 자주 끊기는 흐름도 개선 검토 대상이다. SACRATA의 연속 쓸어내기·동작·타격감 품질을 통과했다고 보지 않는다.

EXECUTION.json은 baseline51/코어03/이전EXE/사용자저장/후보02stage 선택 핀 일치를 기록한다. 새 C2는 사용자 저장을 읽거나 쓰지 않는다. 이 확인이 모든 과거 증거의 바이트 불변이나 누수0을 증명하지 않는다.
'''
    (NATIVE/'OBSERVATIONS.ko.md').write_text(observation,encoding='utf-8')
    writej(NATIVE/'OBSERVATION-EVIDENCE.json',{'source':'root CUA manual observations plus independently read EXECUTION/stdout/stderr/capture hashes','raw_execution_sha256':sha(NATIVE/'EXECUTION.json'),'captures_count':len(execution['captures']),'copied_matches':True,'actual_exit':0,'stderr_bytes':0,'terminal':results[0],'scope':'Manual UI boundary observations, not natural-play winrate, full chapter, hearing, formal GPU performance, or SACRATA quality approval.'})
    draft=PROOF/'book-v03/drafts/before-native-01';assert not draft.exists();draft.mkdir(parents=True)
    for p in [DIST/'validation.html',ROOT/'HANDOFF.md',PROOF/'STATUS.ko.md']:shutil.copy2(p,draft/p.name)
    (DIST/'native').mkdir()
    for filename in ['state-0008-run-001-inventory.png','state-0012-run-001-inventory.png','state-0013-run-001-choice.png','state-0017-run-001-defeat.png','state-0019-run-002-paused.png']:shutil.copy2(dest/filename,DIST/'native'/filename)
    shutil.copy2(NATIVE/'OBSERVATIONS.ko.md',DIST/'native/OBSERVATIONS.ko.md')
    p=DIST/'validation.html';text=p.read_text(encoding='utf-8')
    text=text.replace('후보03 root 검수 진행 대기','root가 실제1440×810 조작, 종료actual0').replace('이 페이지 작성 시점에는 미확정. 후보02 이전 실기와 구분.','메뉴·모달·장착무회복·회피표시·M안내·실제패배HP0·R초기화. 수동진화/세기술/정예승리·실청취는 미완료.')
    section='''<h2>root가 직접 조작한 후보03</h2><p>메뉴3시작, 화면 흔들림 끄기, 성장과 Esc 정지/복귀, Space 대기 표시, 성장 중 장비 열기·복귀를 확인했습니다. 무기+14%/+1발사체와 갑옷+34최대HP/7%감소를 장착해도 현재HP를 회복하지 않았습니다.</p><div class="columns"><figure><img class="wide" src="native/state-0013-run-001-choice.png" alt="갑옷 장착 후 성장 화면, 생명력15/154"><figcaption>갑옷 장착 뒤14초 성장 화면, HP15/154.</figcaption></figure><figure><img class="wide" src="native/state-0017-run-001-defeat.png" alt="17초80처치 패배와 HP0/154"><figcaption>실제17.85초/80처치/Lv5 패배, HP0/154.</figcaption></figure></div><p>R 재도전 뒤0초/0처치/Lv1/HP120/120과 장비 초기화, 창 X 종료actual0을 확인했습니다. 진화·세 기술·정예 승리는 수동으로 완료하지 않았고 실제 청취도 미확인입니다. UI를 느리게 관찰하며 주로 정지한 실행이므로17.85초 패배를 일반 플레이 난이도나 승률로 확대하지 않습니다.</p><p><a href="native/OBSERVATIONS.ko.md">root 네이티브 관찰·원시 한계</a>. 자동 모드 PNG는 모든 장착 직후를 찍지 않으며, 일부 즉시 변화는 root의 당시 CUA 관찰에 근거합니다.</p>'''
    text=text.replace('<h2>근거 문서</h2>',section+'<h2>근거 문서</h2>');p.write_text(text,encoding='utf-8')
    status=PROOF/'STATUS.ko.md';text=status.read_text(encoding='utf-8')+'\n## root 후보03 네이티브 후속 확인\n\n[root 직접 조작 관찰](native-runtime-03/native-20261101-01/OBSERVATIONS.ko.md)을 추가했다.1440×810 메뉴/성장/정지복원·회피표시·장비 비교/장착무회복·Mtoast·실제17.85초/80처치/Lv5/HP0/154 패배·R초기화120/120·창X 종료actual0, stderr0bytes다.20PNG/실행/해시 원시를 보존했다. 진화·세기술·정예 승리·OS WASD hold·긴좌클릭 이동·실청취는 확정하지 않았다. 관찰용으로 주로 정지한 수동 실행의 조기 패배를 승률이나 난이도로 일반화하지 않는다. 영웅 주변 적 겹침과 잦은 초반 성장 화면의 흐름은 품질 개선 대상으로 남겼다.\n'
    status.write_text(text,encoding='utf-8')
    h=ROOT/'HANDOFF.md';text=h.read_bytes()
    old='후보03 직접 OS 조작 결과는 아직 이 인계에 확정하지 않았다.'.encode('utf-8')
    new='후보03은 root가1440×810에서 직접 OS 조작했다. `native-runtime-03/native-20261101-01/OBSERVATIONS.ko.md`:메뉴3시작/모션끄기·성장Esc정지복원·Space대기·장비무기14%/+1탄/갑옷+34최대HP·감소7% 장착무회복·M안내·17.85초/80처치/Lv5/HP0/154 실제패배·R초기화120/120·X종료actual0/stderr0bytes,20PNG다. 수동진화/세기술/정예승리·OS WASDhold·긴좌클릭이동·실청취는 확정하지 않았다. 느린UI관찰/주로정지한실행의 패배를 일반승률로 확대하지 않는다.'.encode('utf-8')
    assert text.count(old)==1;text=text.replace(old,new,1);h.write_bytes(text)
    old=Path('C:/Project/game-research/implementation-backups/chapter1-quality03-docs-before-20261101-01/HANDOFF.md').read_bytes();assert text.endswith(old)
    print(json.dumps({'native_actual_exit':0,'captures':len(execution['captures']),'terminal_seconds':17.85,'handoff_exact_suffix':True}))
if __name__=='__main__':main()
