# 후보03 패키지·영상 준비

2026-11-01, Asia/Seoul. 코어03은 동결된 전투 규칙이며, 아래 후보03은 별도의 실행 패키지 번호다. 이 도구는 제품 소스를 수정하지 않는다. `prepare`만 실행했으며 아직 내보내기·GPU·영상 렌더를 실행하지 않았다.

명시적 런타임 원본70개는 채택된 품질03 아트 PNG5개/JSON3개, 기존 배우 PNG10개/JSON5개, CC0 WAV20개·출처 장부·라이선스3개, 전투 코어와 새 월드/효과/HUD/음향 코드를 포함한다. 거절한 달리기 시트·연구자료·검증 도구·이전 합성음은 포함하지 않는다. 패키지 원본70개와 프로젝트/내보내기 설정을 더한 스테이징72개를 각각 핀한다. 실제 개수는 `build.json`이 최종 기준이다.

준비 검사에서 기존51개·코어9개·이전 실행본2개·사용자 저장2개·후보02 스테이징44개는 불일치0이었다. 선택 핀 검사이며 모든 과거 증거 전체의 불변을 주장하지 않는다.

소스 담당자의 최종 동결과 root의 GPU 일정 할당 후 순서대로 실행한다. 모든 출력 경로는 최초 생성만 허용하며 실패했을 때도 기존 폴더를 덮거나 지우지 않는다. 재시도는 원인을 확인하고 새 ID로 도구를 복사·조정한다.

```powershell
$qualityPython = 'C:\Users\twins\AppData\Local\Programs\Python\Python310\python.exe'
$qualityTool = 'C:\Project\d2r-combat-baseline\plans\chapter1-quality-20261031-01\package03\package_quality03.py'
$qualityFreeze = 'C:\Project\d2r-combat-baseline\plans\chapter1-quality-20261031-01\package03\FINAL-SOURCE-FREEZE.json'
& $qualityPython -B $qualityTool freeze $qualityFreeze
& $qualityPython -B $qualityTool build --source-freeze $qualityFreeze
```

별도 경로에 채택된 원본만 복사하고, 새 진입점·분리 사용자 디렉터리와 명시적 리소스 내보내기를 적용한다. 실제 import/export exit·원시 로그·PCK 내부 payload 체크섬·동적 리소스 포함·금지 경로 부재를 기록한다. 동일 EXE의2초 headless 실행으로 새 음향 raw fallback0과 배우 텍스처 raw fallback0을 검사한다. 이는 GPU 화면 검수나 실제 청취가 아니다. 실행 폴더의 `credits`에 생성 아트 장부와 CC0 라이선스/출처를 제공한다.

```powershell
& $qualityPython -B $qualityTool movie --variant new --capture-id new-20261101-01
& $qualityPython -B $qualityTool movie --variant old --capture-id old-20261101-01
```

영상은 새 후보 스테이징 또는 핀된 후보02 스테이징의 새 사본으로 만든다. seed90131·기존 일반 입력/선택/장착 드라이버를 사용하며 HP·XP·아이템·처치를 주입하지 않는다. 기본 드라이버는 성장 카드를 곧바로 선택하므로 영상에서 카드 내용을 읽을 시간은 거의 없다. 카드/장비 가독성은 별도 실제 UI 검수로 확인한다.

Godot4.5.1 로컬 `--help`에서 확인한 `--write-movie`·`--fixed-fps 30`·`--quit-after 2700`으로720p/90초를 오프라인 렌더한다. 출력 AVI와 변환 MP4를 모두 보존한다. ffmpeg `-n`으로 덮어쓰기를 금지하며 ffprobe로 크기·길이·오디오 스트림을 확인한다. 두 영상은 수동 플레이나 실제60FPS 성능 측정이 아니다. 현재 `_frame_ms` 출력도 고정 FPS 영상의 성능 증거로 사용하지 않는다.

영상 하나를 시작하기 전에 C드라이브18GiB 초과 여유를 요구한다. 부족하면 이전 원시를 자동 삭제하지 않고 중단한다. GPU 렌더는 다른 GPU 측정·화면 QA와 겹치지 않도록 root가 순서대로 할당한다.
