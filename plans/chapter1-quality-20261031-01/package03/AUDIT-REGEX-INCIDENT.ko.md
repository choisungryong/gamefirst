# 정적 검사 표현식 수정

첫 `audit_final_package.py` 실행은 제품 오류가 아닌 검사기 정규식 오류로 중단됐다. 확장자 선택에서 `gd`가 `gdshader`보다 먼저 일치하고 종료 경계가 없어 `chapter1/view/comet.gdshader`를 존재하지 않는 `chapter1/view/comet.gd`로 잘라 읽었다.

도구 출력: `AssertionError: ('chapter1/view/cloister_effects.gd', 'chapter1/view/comet.gd')`

검사기에서 긴 확장자를 먼저 두고 따옴표/공백 종료 경계를 확인하도록 수정했다. 첫 실행은 최종 감사 파일 생성 전에 중단됐고 제품·스테이징·기존 증거에는 쓰지 않았다. 수정 후 별도 실행 원시와 결과를 보존한다. 이 실패를 제품 수정이나 성공 검사로 계산하지 않는다.
