from pathlib import Path
from urllib.request import Request, urlopen
import json
PROOF=Path(__file__).resolve().parent
DIST=PROOF/'book-v03/dist'
OUT=PROOF/'book-v03/HTTP-QA-01.json'
assert not OUT.exists()
resources=sorted(p for p in DIST.rglob('*') if p.is_file())
records=[]
for p in resources:
    relative=p.relative_to(DIST).as_posix()
    url='http://127.0.0.1:8768/plans/chapter1-quality-20261031-01/book-v03/dist/'+relative
    with urlopen(Request(url,method='HEAD'),timeout=8) as r:
        assert r.status==200
        assert int(r.headers['Content-Length'])==p.stat().st_size
        records.append({'path':relative,'status':r.status,'bytes':p.stat().st_size,'type':r.headers.get('Content-Type')})
OUT.write_text(json.dumps({'success':True,'requests':records,'scope':'Read-only local HTTP HEAD/resource size checks. Browser interaction/visual/audio/print approval remains separate.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'success':True,'resources':len(records),'method':'HEAD','byte_length_mismatches':0}))
