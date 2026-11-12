# 최신 확인 — 2026-11-12

root의 probe01 화면 검토 후 같은 시작 버튼3개에 기본 rank1 효과 한 줄을 추가하고 높이를88논리픽셀로 늘렸다. growth_quality37.json의 rank1값을 확인해 잿불탄 기본피해12/1발, 서리창 기본피해10/관통2/적속도-20%, 번개 기본피해9/연쇄3대상을 표시했다. 짧은 기절은 실제Core36의 별도상태처리다. rank1 서리창은 freeze_stacks0이므로 빙결을 주장하지 않는다. 최종 장비 보너스가 아닌 기본 특성이다.

probe02는26개 확인/종료0을 통과했고 root가720p 큰 버튼·원화·옵션 배치를 시각 승인했다. 감속 대상이 플레이어로 오해되지 않도록 '적 이동 속도'로 명확히 한 최종 probe03도26개 확인/종료0/stderr빈값이다. 최종720p·1080p 화면은 probe03/menu-1280x720.png와 probe03/menu-1920x1080.png다. 두 해상도를 직접 확인했고 잘림·원화 왜곡·옵션 겹침 없음. 이전 probe01/02 원시는 보존했다.

UI41 소스만 변경했으며 제품40freeze174개 해시는 모두 일치한다. root 조립본·기존 제품·사용자 프로필은 변경하지 않았다. GPU 반납 및 Godot/Ashen 프로세스 없음 확인. 초상 출처 문서 상단에는 UI41의 2D 메뉴 원화 용도·분리 검증 완료·실제 제품 상태는 full41/STATUS.ko.md 참조를 기록했고 생성 시점 본문은 보존했다. 제품41 freeze 후에는 출처 문서를 변경하지 않는다.

---
# 초상 메뉴41 분리 검증

2026-11-12. **UI41 타이틀 메뉴의 실제 Forward+ 화면·입력 연결 확인을 통과했다.** 제품 채택·3D 외형·전체 플레이·최종 성능 완료를 뜻하지 않는다.

## 구현과 화면

`chapter1/view/ui41/chapter_hud_quality41.gd`는 UI40을 상속한다. 메뉴에서만 원래 시작 버튼3개와 화면 흔들림·보관함·프로필 안내 노드를 새 구성으로 옮긴다. 시작 기술 ID를 캡처한 기존 콜백 자체를 보존한다. 원화는360×540 논리 크기와 비율 유지 방식으로 표시한다. 새 음소거 버튼은 기존 신호를 사용한다.

실제720p·1080p 캡처를 직접 확인했다. 초상의 전체 비율과 얼굴이 유지되며 제목·설명·기술 버튼·보관함·프로필 안내가 화면 안에 들어온다. 캡처의 서리창 포커스는 Tab 이동 확인 후 찍은 결과이며, 최초 포커스는 잿불탄 시작 버튼임을 별도로 확인했다.

캡처: `probe01/menu-1280x720.png`, `probe01/menu-1920x1080.png`.

## 확인 범위

`probe01/RESULT.json`의26개 확인이 모두 통과했고 실행 종료0·stderr 빈값이다. Vulkan Forward+ 실제 렌더에서 다음을 확인했다.

- 원화 로드와 실제 메뉴 구성, 각 해상도에서 시작 버튼3개가 중복 없이 존재함
- 첫 시작 버튼의 최초 포커스와 Tab의 메뉴 내 이동
- 기존 세 버튼이 전달하는 정확한 ember/frost/arc 기술 ID
- 음소거와 화면 흔들림의 기존 신호 및 실제 표시 상태 연결
- 기존 보관함 콜백으로 열기, Esc 복귀 후 초상 메뉴 단일 트리 유지
- PNG 캡처 저장 성공

시작 콜백의 원래 owner는 검사 중 분리하고 전달되는 기술 ID를 수집했다. 정상 전투 시작과 저장 연속성은 제품40의 별도 통합 근거를 따른다. 이 메뉴 검사를 전체 전투 검사로 확대하지 않는다.

## 실행·보존

독립 스테이지: `C:/Project/game-research/build-staging/chapter1-ui41-preview-20261112-01`.
제품40의172개 런타임 소스에 UI41 스크립트·초상PNG·출처문서3개만 추가했다. stage-only HUD preload와 고유 `AshenCloisterChapterOneUI41Preview20261112` 저장 namespace를 사용했다. 모든 실행은 `--chapter1-profile-off`로 진행했다.

실행한 주요 명령:

```powershell
python -B plans/chapter1-quality04-20261101-01/ui41/prepare_and_verify41.py
Godot_v4.5.1-stable_win64_console.exe --headless --path C:/Project/game-research/build-staging/chapter1-ui41-preview-20261112-01 --check-only --script res://ui41_probe.gd
Godot_v4.5.1-stable_win64_console.exe --path C:/Project/game-research/build-staging/chapter1-ui41-preview-20261112-01 --position 20,20 --script res://ui41_probe.gd -- --chapter1-profile-off --ui41-output=C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/ui41/probe01
```

첫 준비의 Windows 기본 cp949 읽기 오류는 명시 UTF-8로 수정했다. 최초 helper parser의 동적 메뉴 변수 타입 추론 오류는 `Node` 명시로 수정했고 `parser01.log` 실패 원시를 보존했다. `parser02`와 실제 `probe01`은 종료0이다. UI41 제품 소스에는 변경이 필요하지 않았다.

`PRESERVATION.json`에서 원제품40 소스174개·원스테이지174개 해시 불일치0과 EXE 동일 SHA를 확인했다. root 조립본·기존 제품·사용자 프로필을 변경하지 않았다. 실행 후 Godot/Ashen 프로세스 없음, GPU 반납.

AI 생성2D 초상과 기존3D 배우는 서로 다른 자산이다. 이 결과는 3D 모델·리그·애니메이션·여성 외형 적용 완료를 뜻하지 않는다. 제품 채택은 root의 시각 승인과 별도 패키징 이후다.
