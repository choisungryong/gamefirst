# 후보03 비정식 실행·성능 진단

2026-11-01, Asia/Seoul. 같은 후보03 EXE를 실제1920×1080/Forward+/Vulkan1.4.341/RTX2070SUPER에서 일반 입력 드라이버로70게임초 실행했다. **이 결과는 정식60FPS 성능 통과가 아니다.** 제품 소스는 바꾸지 않았다.

## 실제 결과

`execution.json`의 실제 exit0, stdout/stderr에 오류·경고 없음. 벽시계72.3600449562초, 게임70.0초에 `playing`,698처치·Lv12·HP7210raw, 화염4진화/냉기3/번개3, 무기·갑옷·부적·반지 장착 상태였다. 정예가70초에 등장하므로 이70초 종료는 승리 증거가 아니다. max_alive59, peak_projectiles28이다. 최대180적 부하도 아니다.

PNG·movie·HP/XP/아이템/처치 주입 없이 기존 정상 이동/선택/장착 드라이버와seed90131을 썼다. `--delta-smoothing disable --disable-vsync --max-fps0`이며, 창초점 무시는 끄고 실행했다. world/actor/audio의 raw fallback 목록은 모두 비었다.

root는 실제 EXE03 창461208을 선택하고31초·198처치·Lv7·HP47/154 화면과1920×1080을 관찰했다. AX Raise 뒤 게임창의 초점도 확인했다. 별도 gameplay 키/클릭은 없었다. 약31초의 CUA 스크린샷 한 번은 관찰 비용을 넣을 수 있으며, 전체 프레임의 초점 기록은 없다. `ROOT-FOCUS-OBSERVATION.json`은 부모가 전달한 해당 관찰을 기록한다.

## 표본 상한 발견과 해석 정정

실행본이 출력한 p95는1.38888888888889ms, frame_samples15000이다. **기존15000프레임 저장 상한에 도달했다.** `chapter_view.gd`는 `_frame_ms.size()<15000`일 때만 추가하므로 이 값은 처음15000 playing 프레임의 엔진 delta에 한정된다. 표본 종료 시각은 기록되지 않았고,70초 전체의 p95라고 말할 수 없다.31초의 root 초점 관찰도 표본 전체의 전경 상태를 증명하지 못한다.

준비 도구/초기 scope 문자열이 'whole0–70'로 설명한 것은 잘못된 가정이었다. `CORRECTION.json`이 이 해석을 정정한다. 원래 PREPARATION·실제 argv·stdout/stderr·execution JSON은 바꾸지 않아 원시를 보존했다. 이 숫자는 원시GPU 프레임 시간·첫10초 제외 후60초·3회 반복·정식60FPS 통과 또는 기존 PNG QA 약20ms 대비 개선율의 근거로 쓰면 안 된다. 좋은 수치를 얻기 위한 반복 실행이나 상한 변경은 하지 않았다.

다음 정식 측정에는 프레임별 단조 시각·게임 시각·초점·viewport·warmup 경계를 기록하고,15000개로 조기 중단하지 않는 충분한 저장 범위가 필요하다. 새 계측이 들어가면 별도 후보와 새 증거로 검증해야 한다.

## 보존·종료

source70·core9·baseline51·현재/기존EXE3·사용자 저장2의 전후 핀이 모두 일치했다. 후보03 EXE SHA256은 `c916e280facbc89c6fcb1b21ee9a3fc9725313e248956e1918342ac2d4602fbb`다. 실행 종료 뒤 Godot/Ashen 프로세스가 없음을 확인하고 GPU를 root에게 반환했다. 커밋·업로드·원작 복사·제품 수정·성능 승인·실제 음향 청취는 하지 않았다.
