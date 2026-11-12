"""Add evidence thumbnails without classifying them as shipped assets."""
from pathlib import Path

root=Path(__file__).resolve().parents[3]
path=root/'tools/game_manager/app.js'
body=path.read_bytes();eol=b'\r\n' if b'\r\n' in body else b'\n'
old=b"${assets.length?'<div id=\"previews\"></div>':''}"
new=b"${(assets.length||(e.previews||[]).length)?'<div id=\"previews\"></div>':''}"
assert body.count(old)==1
body=body.replace(old,new)
old=b'assets.slice(0,8).forEach(p=>preview(p));'
assert body.count(old)==1
body=body.replace(old,old+b'(e.previews||[]).forEach(p=>evidencePreview(p));')
function='''
function evidencePreview(item){
 const host=$('#previews'),box=document.createElement('section');
 box.className='preview evidence-preview';
 const url=fileURL(item.path);
 box.innerHTML=`<h3>${esc(item.name||'실제 검증 장면')}</h3><a target="_blank" rel="noopener" href="${esc(url)}"><img loading="lazy" src="${esc(url)}" alt="${esc(item.name||'게임 검증 장면')}"></a><p class="evidence-scope">${esc(item.scope||'정지 이미지')}</p><p><a target="_blank" rel="noopener" href="${esc(url)}">장면 크게 보기</a></p>`;
 box.querySelector('img').addEventListener('error',()=>{box.innerHTML='<p>검증 장면 파일이 없습니다. 원본 게임 에셋의 미리보기와 구분되는 로컬 검증 기록입니다.</p>'});
 host.append(box);
}
'''
body+=function.encode('utf-8').replace(b'\n',eol)
path.write_bytes(body)
print('Connected evidence previews; existing viewer preserved')
