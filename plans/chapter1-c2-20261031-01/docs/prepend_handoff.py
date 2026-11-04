"""Append current authority as a prefix; retain previous document bytes exactly."""
from pathlib import Path
import hashlib
import json

ROOT=Path('C:/Project/d2r-combat-baseline')
C2=ROOT/'plans/chapter1-c2-20261031-01'
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01')
OUT=C2/'docs/DOCUMENT-PREFIX-MANIFEST.json'
assert not OUT.exists(), 'Choose a new document update ID'
def sha(b):return hashlib.sha256(b).hexdigest()
baseline=json.loads((BACKUP/'manifest.json').read_text(encoding='utf-8'))['documents']
handoff='''# 2026-10-31 최신 인계 — 새1장 C2 후보02 실기 확인 · 품질 관문 열림

사용자 목표는 SACRATA의 표현·화려한 군중 전투와 디아블로식 장비 드롭·스킬 성장의5–8분짜리1장이다. 현재는 새 chapter1 경로에 대표 전투·성장·장비·정예를 통합한 플레이테스트 후보02까지 구현했다. **C2 최종 품질이나5–8분 1장 전체 완성은 아니다.** 기존 기술 승인으로 표현/재미 미달을 통과 처리하지 않으며1장 품질 전2·3장을 확장하지 않는다.

1. 현재 실행: `builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe`, 조작은 같은 폴더 `RUN.ko.md`. EXE109675984bytes, SHA256 `111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188`. source42/stage44/PCK78, 코어03을 포함한 **패키지 후보02**다. 코어03을 패키지03으로 부르지 않는다. 원본 Baseline/Expedition 진입점은 유지한다.
2. 실제 연결: 세 기술 독립 자동 시전·4랭크/패시브/진화·XP3지선다, 일반3역할/정예1명, 무기/갑옷/부적/반지의 실제 드롭·비교·장착·승패·재도전. 70초 정예가 실제 죽으면 즉시 승리하며 시간만으로 승리하지 않는다. 새 C2는 런에서만 장비/성장을 유지하고 저장 기능이 없다. 기존 equipment-v1/progress-v1을 읽거나 변경/자동 변환하지 않는다.
3. 실제 아트는 독립 생성2.5D PNG이며 리깅3D가 아니다. 역할5개 각각 이동4방향×4키프레임, 남쪽 공격/시전·피격·사망 각4키프레임. `chapter1/art/ASSET-LEDGER.json`에 원본/프롬프트/해시/한계가 있다. 전용idle·다른방향 행동·기하 환경 소품·바닥 반복·최종 효과/음향·연속 타격감은 개선/검수 중이다. 기존 합성WAV를 재사용했고 실제 청취를 완료했다고 주장하지 않는다.
4. `plans/chapter1-c2-20261031-01/STATUS.ko.md`가 현재 보고서다. 독립 코어03 기능75 actual0·의도실패76 actual1·독립114 actual0,9pin 전후 일치. 일반입력6회는5승1패(actual1/success:false): 냉기seed71은64.9초/237처치/HP0, 주력진화·3기술·장비6개에서 패배했다. 실패를 보존했고 HP/XP/아이템/스폰/처치 주입이나 seed 교체로 성공을 만들지 않았다. 바닥32에서 정예 보상 소실을 일반64+목표예비1칸(총65) 정책으로 수정하고 UID/장착/중복경계를 확인했다. 회피는12회 이동·미래18step 무적이다.
5. 부모/root가 **후보02 실제 OS 입력을 직접 수행**했다. `native-runtime-02/OBSERVATIONS.ko.md`:1440×810 메뉴/카드·Esc모달복원·I·무기피해14%/+1탄·부적회수+1m/주기8% 장착무회복·좌클릭이동·Space대기3초·M안내·화염진화·냉기/번개습득·실제57.433333초/499처치/Lv9/장비4개 패배HP0/120·R재도전HP120/120·X종료actual0. 정예OS승리·WASD물리hold·별도초점상실·실청취는 미검수다. 벽시계447.8초는 모달/관찰을 포함하며1장 완주 시간이 아니다.
6. 후보01은 보존했다. 그 실제 OS 관찰에서 같은tick 종료HUD와 도구주입 physical키=Pause/논리키정상 문제를 발견했다. 실제 물리 키보드 고장으로 일반화하지 않는다. 후보02의 논리키우선/동일tick HUD/실행별 캡처 수정은 독립뷰53 actual0·의도54 actual1과 부모실기로 확인했다. 최초 fixture의 종료 resource warning도 남겼고 재실행은 깨끗했지만 누수0은 주장하지 않는다. 후보01 동일코어/아트의 packaged 자동입력78.15초/813처치 승리·1080p p95약20ms는01의 참고 원시이며02 정식 성능이 아니다. 목표16.67ms는 아직 정식 통과하지 못했다.
7. 현재 제작 도감은 `plans/chapter1-c2-20261031-01/book-v02/dist/index.html`:17목차·39상세브리프·25참고장면·14실행캡처·PNG12개(런타임11+초기증거1). 실제 장비4개 이름/수치를 원본과 맞추고 v0.1 계획은 별도 이력으로 구분했다. 부모가 데스크톱 표지/현재C2/갤러리/아트/IT003을 확인했고 새모바일·전체메모/인쇄 재검수는 아니다. v01 도감/ZIP는 보존했고 루프백 임시 미리보기는 종료했다. 새도감ZIP·해시는 `BOOK-ARTIFACTS.json`, 보존 비교는 `FINAL-PRESERVATION.json`을 따른다.

다음은 같은 C2 실행 후보에서 환경/동작/연속 효과·소리/성능/직접 플레이의 품질 격차를 줄이는 작업이다. 연결3구역·이벤트·정예변형·고유보스/단계·보상보존·저장과5–8분 전체1장은 아직 없다. 해당 관문을 품질로 통과하기 전 대표90초를1장으로 축소하거나2·3장으로 넘어가지 않는다.

이번 갱신 전 인계/상태2문서는 `C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01/`에 보존했다. 아래 이전 원문은 bytes 그대로 exact suffix로 남는다. 기존 source51·phase7 EXE·현재 사용자 equipment/progress 두 저장·v01 도감/ZIP의 선택 핀을 다시 비교한다. 이 비교가 미핀된 과거 증거 전체의 바이트 불변이나 과거 두 보고서 복구를 의미하지 않는다. 커밋·외부 업로드·유료구매·원작 보호자산 복사는 하지 않았다.

---

'''
status='''# 2026-10-31 현재 상태 — 새1장 C2 후보02 플레이테스트 인수

성장·장비·군중·정예가 연결된 별도 전투를 구현하고 새 실행본 후보02를 내보냈다. 현재 실행은 `builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe`, SHA256 `111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188`. 상세는 `plans/chapter1-c2-20261031-01/STATUS.ko.md`다. 코어03/패키지02를 구분한다.

독립 코어 기능75/경계114 actual0·의도76 actual1, 일반6입력5승1패(actual1,냉기seed71 64.9초 패배)를 보존했다. 후보01에서 발견한 HUD/도구주입 단축키 호환을02에서 수정했고 독립뷰53 actual0·의도54 actual1 및 부모 실제 OS 입력으로 확인했다. source42/PCK78, 원본/staging/EXE·과거source51/사용자저장 선택 핀을 별도 보존 결과에 연결한다.

부모 실기02:1440×810 메뉴/성장·무기/부적 비교장착·모달정지·좌클릭이동·Space/M안내·화염진화·3기술·실제57.433333초/499처치/Lv9/장비4개 패배HP0·재도전HP120·actualexit0. OS정예승리·실청취·WASD물리hold·별도초점상실은 미검수다. 후보01 자동승리와1080p p95약20ms를02 정식성능으로 바꾸지 않는다.

현재 도감 v02 `book-v02/dist/index.html`은17목차·39브리프·14실행이미지·실제PNG원장을 제공한다. v01은 보존했다. 부모 데스크톱 시각검수와 정적참조 검증을 연결하며 새모바일/전체메모·인쇄 재검수는 아니다. 미리보기 서버는 종료했다.

**C2 최종 품질과5–8분 1장 전체는 미완료다.** 독립2.5D 후보의 다른방향 행동·idle·환경소품·바닥반복·연속 타격/음향·성능을 개선한다. 연결3구역·이벤트·고유보스·보상보존·저장도 남았다. 새 C2는 저장을 구현하지 않았고 기존 equipment-v1/progress-v1을 읽거나 변경하지 않는다. 1장 품질 검수 전2·3장으로 확장하지 않는다.

이전 문서 bytes를 아래 exact suffix로 보존한다. 백업은 `C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01/`, 비교는 새C2 `FINAL-PRESERVATION.json`. 과거 기술 승인을 최종 아트/손맛 승인으로 해석하지 않는다.

---

'''
records=[]
for name,prefix in [('HANDOFF.md',handoff),('IMPLEMENTATION-STATUS.ko.md',status)]:
    old=(BACKUP/name).read_bytes()
    assert sha(old)==baseline[name], 'Backup pin changed'
    assert (ROOT/name).read_bytes()==old, 'Document changed since backup; reconcile before prefix'
    data=prefix.encode('utf-8')+old
    (ROOT/name).write_bytes(data)
    assert (ROOT/name).read_bytes().endswith(old)
    records.append({'path':name,'before_sha256':sha(old),'after_sha256':sha(data),'prefix_bytes':len(data)-len(old),'old_exact_suffix':True})
OUT.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
