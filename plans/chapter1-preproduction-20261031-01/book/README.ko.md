# 1장 제작 도감 사용법

`dist/index.html`을 브라우저에서 열면 된다. 설치·외부 계정·배포가 필요 없다. 로컬 본문과 이미지는 오프라인 사용 가능하며 원문 영상·Steam 링크는 인터넷이 필요하다.

- 목차14개와 제작 항목39개. 각 항목은 `asset.html?id=SK-001`처럼 고정 주소가 있다.
- 이름/ID/효과 검색, 에셋 원장의 분류/단계 필터, 참고 원본 보기, 페이지 인쇄.
- 검토 메모는 해당 브라우저/주소에만 저장된다. `메모 내보내기`로 JSON을 보존하고 다른 환경에서 가져올 수 있다. 같은ID는 가져온 메모로 교체된다.
- 제작 사양과 참고 이미지는 완성된 게임 자산이 아니다. 실제 자산이 생기면 원본·라이선스·SHA256·리비전·검수 상태를 원장에 등록한다.
- 기준 내용은 `content.json`, 화면은 `app.js/style.css`. `python build.py`로 dist를 다시 만든다. `author_content.py`는 최초/일괄 저술 도구이며 실행하면 content.json을 다시 작성하므로 수동 수정 뒤에는 덮어쓰기에 주의한다.

선택적 HTTP 미리보기:

```powershell
python -m http.server 8766 --bind 127.0.0.1 --directory "C:\Project\d2r-combat-baseline\plans\chapter1-preproduction-20261031-01\book\dist"
```

브라우저에서 `http://127.0.0.1:8766/index.html`을 연다. 작업이 끝나면 서버 터미널에서Ctrl+C로 종료한다. 파일로 열기와HTTP주소는 브라우저 메모 저장 영역이 다르므로 JSON 내보내기로 옮긴다.
