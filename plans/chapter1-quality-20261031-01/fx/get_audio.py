from pathlib import Path
import urllib.request,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
SOURCE=Path('C:/Project/game-research/audio-sources/quality03-20261031-01')
SOURCE.mkdir(parents=True,exist_ok=True)
url='https://kenney.nl/media/pages/assets/impact-sounds/87b4ddecda-1677589768/kenney_impact-sounds.zip'
dest=SOURCE/'kenney_impact-sounds.zip'
assert not dest.exists()
with urllib.request.urlopen(url,timeout=60) as response:
    data=response.read()
dest.write_bytes(data)
with zipfile.ZipFile(dest) as z:
    names=z.namelist()
    for name in names:
        if name.lower().endswith('.ogg') or name.lower().endswith('license.txt'):
            target=SOURCE/name
            assert SOURCE.resolve() in target.resolve().parents
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(name))
record={'creator':'Kenney','primary_page':'https://kenney.nl/assets/impact-sounds','download':url,'license':'CC0 1.0 Universal','archive':str(dest),'sha256':hashlib.sha256(data).hexdigest(),'files':names,'inspection':'Primary page lists130 files and Creative Commons CC0; bundledLicense.txt inspected separately.'}
(ROOT/'AUDIO-SOURCE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
