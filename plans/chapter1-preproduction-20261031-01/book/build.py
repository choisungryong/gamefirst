"""Build a portable, offline local production book. Reference media stays reference-only."""
import copy
import html
import json
import shutil
from pathlib import Path

BOOK=Path(__file__).resolve().parent
ROOT=BOOK.parent
DIST=BOOK/'dist'
DIST.mkdir(exist_ok=True)
(DIST/'media').mkdir(exist_ok=True)
(DIST/'reference').mkdir(exist_ok=True)
data=json.loads((BOOK/'content.json').read_text('utf-8'))
for o in data['observations']:
    filename=Path(o['image']).name
    shutil.copyfile(ROOT/'evidence'/filename,DIST/'media'/filename)
    o['image']='media/'+filename
shutil.copyfile(ROOT.parent.parent/'evidence/phase7/runtime-pilot-20261030-01/case/frame-75.png',DIST/'media/prototype-75.png')
data['prototype']='media/prototype-75.png'
for name in ['SACRATA-ANALYSIS.ko.md','INVENTORY-FACTS.ko.md','PRIMARY-SOURCES.ko.md','BOOK-DESIGN.ko.md']:
    shutil.copyfile(ROOT/name,DIST/'reference'/name)
shutil.copyfile(ROOT.parent/'chapter1-replan-20261030-01/DOCUMENTATION-DISCOVERY.ko.md',DIST/'reference/DOCUMENTATION-DISCOVERY.ko.md')
for s in data['sources']:
    if s['id']=='L01':s['url']='reference/INVENTORY-FACTS.ko.md'
    if s['id']=='L02':s['url']='reference/DOCUMENTATION-DISCOVERY.ko.md'
(DIST/'content.js').write_text('window.BOOK_DATA = '+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';\n',encoding='utf-8')
for name in ['app.js','style.css']:shutil.copyfile(BOOK/name,DIST/name)
for page in data['pages']+[{'id':'asset','title':'제작 항목'}]:
    title=html.escape(page['title'])
    content=f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 1장 제작 도감</title><meta name="description" content="SACRATA 분석과 디아블로식 성장·파밍을 연결하는 1장 설계·에셋북"><link rel="stylesheet" href="style.css"><script defer src="content.js"></script><script defer src="app.js"></script></head>
<body data-page="{page['id']}"><a class="skip" href="#main">본문으로 이동</a><aside class="sidebar"><a class="brand" href="index.html">1장 제작 도감<small>잿빛 회랑 · 사양 0.1</small></a><nav id="nav" aria-label="도감 목차"></nav><footer><span id="book-status"></span><br>2026.10.31 / 로컬 작업본<br>참고 캡처 ≠ 제품 사용 자산</footer></aside><div class="workspace"><header class="topbar"><button id="menu-toggle" aria-expanded="false" aria-controls="nav">목차</button><label class="search-label"><span>항목 찾기</span><input id="search" type="search" autocomplete="off" placeholder="이름·ID·효과 검색" aria-label="제작 항목 검색"></label><div class="tools"><button id="print">이 페이지 인쇄</button><button id="export-notes">메모 내보내기</button><label class="file-label">메모 가져오기<input id="import-notes" type="file" accept="application/json,.json"></label></div></header><p id="global-feedback" class="global-feedback" role="status"></p><section id="search-results" class="search-results" aria-label="검색 결과" hidden></section><main id="main" tabindex="-1"></main><noscript>본문을 표시하려면 JavaScript를 켜 주세요. 원문 분석 문서는 reference 폴더에 있습니다.</noscript><footer class="page-footer">독립 설계 · 참고 영상의 내부 규칙/성능을 복원한 제품이 아닙니다. 최종 모델·효과·음향의 제작과 품질 검수는 별도입니다.</footer></div><dialog id="image-dialog" aria-label="참고 캡처 원본"><button id="close-image">닫기</button><div id="dialog-content"></div></dialog></body></html>'''
    (DIST/(page['id']+'.html')).write_text(content,encoding='utf-8')
(DIST/'content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Built {len(data["pages"])+1} local HTML pages; {len(data["assets"])} asset briefs; {len(data["observations"])} reference frames.')
