# 후보25 릴리스 실패 보존

import/export/PCK까지 성공했으나 packaged-headless-smoke의 종료에서265개 material 등 누수가 발생해 build가 중단됐습니다. prewarm에서assert(_stash25(actor))를 호출해 release에서부작용까지생략되며224노드가부모없이고아가됐습니다. source-debug 검사에서는호출되므로성공해도release를증명하지못했습니다. 후보25EXE/stage/freeze/raw전부그대로보존. 저장profile-off. 새25b는부작용을assert밖으로분리하며새stage/output로검증합니다. 후보25는승인제품이아닙니다.
