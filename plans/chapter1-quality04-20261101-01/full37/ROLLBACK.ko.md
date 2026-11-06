# 수동 복원 안내 · 자동 삭제/복원 없음

채택 helper는 실행 전 원36 freeze158개·실행본·최신 사용자9핀을 대조하고, 백업에 assembly/project/preset 원본3개·사용자9파일과 manifest를 보존합니다. 이후 새37 사용자 경로는 원36의3파일을 바이트 그대로 복사하고 모든12핀을 기록합니다. 새37 stage/output은 각 하나만 생성하며 예상 총220~250MiB입니다.

문제가 생기면 모든 게임·Godot 프로세스를 종료하고 현재 root assembly가 ADOPTION 후 freeze의 해시와 일치하는지 먼저 확인합니다. 추가 사용자 변경이 없다면 `ADOPTION.json`의 backup/source/chapter1/chapter_one_view.gd 사본을 원경로로 복원하고 원36 freeze와 다시 대조합니다. root project.godot/export_presets.cfg는 채택 시 수정하지 않으므로 임의 덮어쓰지 않습니다. 달라진 경우 원인을 먼저 조사합니다.

새37 실행본·stage·실패 증거·Quality37 사용자 저장은 삭제하지 않습니다. 실제 플레이로 바뀐 사용자 저장을 과거 사본으로 덮어쓰지 않습니다. 백업 복원이 필요하면 기존·새 파일을 모두 보존한 상태에서 별도 결정합니다. 자동 rollback 명령은 제공하지 않습니다.
