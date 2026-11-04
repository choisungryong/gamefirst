from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, hashlib

ROOT=Path(__file__).resolve().parents[2]
PROOF=Path(__file__).resolve().parent
DIST=PROOF/'book-v03/dist'
OUT=PROOF/'book-v03/STATIC-QA-01.json'

class Page(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.lang=None;self.title=0;self.h1=0;self.audio=0;self.video=0;self.images=0;self.imgmissing=[];self.current=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang')
        if tag=='title':self.title+=1
        if tag=='h1':self.h1+=1
        if tag=='audio':self.audio+=1
        if tag=='video':self.video+=1
        if tag=='img':
            self.images+=1
            if not a.get('alt'):self.imgmissing.append(a)
        if a.get('aria-current')=='page':self.current+=1
        for k in ['href','src']:
            if k in a:self.refs.append(a[k])

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not OUT.exists(),'Preserve QA evidence'
    pages=[];missing=[];fail=[]
    for p in sorted(DIST.glob('*.html')):
        parser=Page();parser.feed(p.read_text(encoding='utf-8'))
        for ref in parser.refs:
            u=urlsplit(ref)
            if u.scheme or u.netloc or not u.path:continue
            target=(p.parent/unquote(u.path)).resolve()
            if not target.exists():missing.append({'page':p.name,'ref':ref,'resolved':str(target)})
        if parser.lang!='ko' or parser.title!=1 or parser.h1!=1 or parser.current!=1 or parser.imgmissing:fail.append(p.name)
        pages.append({'file':p.name,'sha256':sha(p),'refs':len(parser.refs),'images':parser.images,'audio':parser.audio,'video':parser.video,'lang':parser.lang,'one_h1':parser.h1==1,'one_current_nav':parser.current==1})
    assert len(pages)==8
    assert sum(p['audio'] for p in pages)==20
    assert not missing,(missing,fail)
    assert not fail,fail
    copies=json.loads((DIST.parent/'COPY-MANIFEST.json').read_text(encoding='utf-8'))
    mismatch=[p for p,h in copies.items() if sha(DIST/p)!=h]
    assert not mismatch,mismatch
    backup=Path('C:/Project/game-research/implementation-backups/chapter1-quality03-docs-before-20261101-01')
    prior=json.loads((backup/'manifest.json').read_text(encoding='utf-8'))
    old_bad=[p for p,h in prior['old_book_v02'].items() if sha(ROOT/p)!=h]
    original=(backup/'HANDOFF.md').read_bytes()
    assert not old_bad
    assert (ROOT/'HANDOFF.md').read_bytes().endswith(original)
    out={'success':True,'pages':pages,'missing':missing,'metadata_failures':fail,'audio_controls':20,'copied_assets_checked':len(copies),'copy_mismatches':mismatch,'old_v02_files_checked':len(prior['old_book_v02']),'old_v02_mismatches':old_bad,'handoff_exact_suffix':True,'scope':'Static link/metadata/copy hash QA only. No browser screenshot, mobile, interaction, playback or print approval.'}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'success':True,'pages':len(pages),'audio_controls':20,'local_missing':0,'preserved_v02_files':len(prior['old_book_v02'])}))

if __name__=='__main__':main()
