# 후보10 패키지 감사 실패 — 보존

Godot import/export는 종료0이었다. 이후 PCK 감사가 새 모델 출처 `ATTRIBUTION.ko.md` 누락을 발견해 패키징 도구가 실제1로 종료했다. 따라서 이 폴더의 EXE는 검증된 최신 실행본이 아니다.

원인: 원래 export preset의 `exclude_filter`에 있던 `*.md`가 추가한 라이선스 include보다 우선했다. 실패 EXE, stage, import/export JSON과 source freeze를 보존한다. 후보11의 격리 export preset에서만 해당 MD 배제를 제거하고, 명시적으로 선택한 모델 출처 파일의 PCK 해시를 다시 확인한다. 프로젝트 루트 export preset을 변경하지 않는다.
