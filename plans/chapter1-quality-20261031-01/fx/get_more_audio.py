from pathlib import Path
import urllib.request,hashlib,json,zipfile,http.cookiejar,re
ROOT=Path(__file__).resolve().parent
BASE=Path('C:/Project/game-research/audio-sources/quality03-20261031-01')
records=[]
for pack in ['rpg-audio','sci-fi-sounds']:
    source=BASE/pack;source.mkdir(parents=True,exist_ok=True)
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    page='https://kenney.nl/assets/'+pack
    html=opener.open(page,timeout=30).read();(source/'primary-page.html').write_bytes(html)
    key=re.search("data-download-id='([^']+)'",html.decode()).group(1)
    signed=json.loads(opener.open(urllib.request.Request('https://kenney.nl/download-link/'+key,headers={'Referer':page,'Accept':'application/json'}),timeout=30).read())
    data=opener.open(urllib.request.Request(signed['url'],headers={'Referer':page}),timeout=60).read()
    dest=source/(pack+'.zip');assert not dest.exists();dest.write_bytes(data)
    with zipfile.ZipFile(dest) as z:
        names=z.namelist()
        for name in names:
            if name.lower().endswith(('.ogg','.wav','license.txt')):
                target=source/name
                assert source.resolve() in target.resolve().parents
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
    records.append({'creator':'Kenney','primary_page':page,'license':'CC0 1.0 Universal','archive':str(dest),'sha256':hashlib.sha256(data).hexdigest(),'files':names})
    print(pack,names)
(ROOT/'AUDIO-MORE-SOURCES.json').write_text(json.dumps(records,indent=2)+'\n')
