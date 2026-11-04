"""Read-only book closure and preservation checks; each output ID is unique."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path('C:/Project/d2r-combat-baseline')
C2=ROOT/'plans/chapter1-c2-20261031-01'
DIST=C2/'book-v02/dist'
OLD=ROOT/'plans/chapter1-preproduction-20261031-01/book/dist'
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01')
OUT=C2/'docs'/(sys.argv[1] if len(sys.argv)>1 else 'book-static-qa.json')
assert not OUT.exists(), 'Choose new evidence ID'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def link_exists(url):
    parsed=urlsplit(url)
    return bool(parsed.scheme or url.startswith('#')) or (DIST/unquote(parsed.path)).is_file()
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src'] and v:self.links.append(v)

d=json.loads((DIST/'content.json').read_text(encoding='utf-8'))
failures=[]
def check(ok,label):
    if not ok:failures.append(label)
page_ids=[p['id'] for p in d['pages']]
asset_ids=[a['id'] for a in d['assets']]
check(len(page_ids)==17 and len(set(page_ids))==17,'17 unique pages')
check(len(asset_ids)==39 and len(set(asset_ids))==39,'39 unique assets')
html_links=0
for p in DIST.glob('*.html'):
    parser=Links();parser.feed(p.read_text(encoding='utf-8'))
    for url in parser.links:
        html_links+=1;check(link_exists(url),f'HTML link {p.name}: {url}')
for url in re.findall(r'(?:href|src)="([^"$]+)"',(DIST/'app.js').read_text(encoding='utf-8')):
    if '`' not in url and '${' not in url:
        html_links+=1;check(link_exists(url),'app-generated constant link '+url)
for p in d['pages']:
    check((DIST/(p['id']+'.html')).is_file(),p['id']+' route')
    check(all(a in asset_ids for a in p['assets']),p['id']+' asset references')
    check(all(any(o['id']==i for o in d['observations']) for i in p['media']),p['id']+' observation references')
for a in d['assets']:
    check(all(i in asset_ids for i in a['links']),a['id']+' related references')
for item in d['runtimeGallery']+d['runtimeArt']:
    file=DIST/item['image']
    check(file.is_file(),item['image']+' exists')
    if file.is_file():check(sha(file)==item['sha256'],item['image']+' hash')
for item in d['observations']:
    check((DIST/item['image']).is_file(),item['id']+' image')
core=(ROOT/'chapter1/core/combat_run.gd').read_text(encoding='utf-8')
literal=core.split('const ITEM_TEMPLATES := ',1)[1].split('\n]\n',1)[0]+'\n]'
templates=json.loads(literal)
gear_mapping=[]
for n,template in enumerate(templates,1):
    item=next(a for a in d['assets'] if a['id']==f'IT-{n:03d}')
    check(item['runtime_id']==template['base_id'] and item['title']==template['name'],item['id']+' actual runtime name/ID')
    gear_mapping.append({'book_id':item['id'],'runtime_id':template['base_id'],'name':template['name'],'base_stats':template['stats']})
backup=json.loads((BACKUP/'manifest.json').read_text(encoding='utf-8'))
old_current={str(p.relative_to(OLD)).replace('\\','/'):sha(p) for p in OLD.rglob('*') if p.is_file()}
check(old_current==backup['book_v01'],'v01 book byte preservation')
zip_v01=ROOT/'plans/chapter1-preproduction-20261031-01/CHAPTER1-PRODUCTION-BOOK-20261031-01.zip'
check(zip_v01.exists() and sha(zip_v01)==backup['book_v01_zip_sha256'],'v01 zip preservation')
commands=[]
for script in ['app.js','content.js']:
    argv=['node','--check',str(DIST/script)]
    r=subprocess.run(argv,capture_output=True,text=True)
    commands.append({'argv':argv,'actual_exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    check(r.returncode==0,script+' syntax')
result={'success':not failures,'failures':failures,'pages':len(page_ids),'detail_briefs':len(asset_ids),'observations':len(d['observations']),'runtime_gallery':len(d['runtimeGallery']),'art_pngs':len(d['runtimeArt']),'html_links_checked':html_links,'actual_gear_mapping':gear_mapping,'commands':commands,'v01_book_files':len(old_current),'v01_book_mismatches':[] if old_current==backup['book_v01'] else ['changed'],'scope':'This script checks static closure/hash/JS syntax only. Separate root desktop browser observations are in BOOK-VISUAL-QA.ko.md. New mobile and full notes/print interaction QA were not performed.'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
sys.exit(0 if result['success'] else 1)
