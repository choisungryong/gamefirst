from pathlib import Path
import urllib.request,hashlib,json,zipfile,http.cookiejar
ROOT=Path(__file__).resolve().parent
SOURCE=Path('C:/Project/game-research/audio-sources/quality03-20261031-01')
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
page='https://kenney.nl/assets/impact-sounds'
html=opener.open(page,timeout=30).read()
(SOURCE/'impact-sounds-page.html').write_bytes(html)
# Official page's Continue without donating JavaScript requests this public link.
endpoint='https://kenney.nl/download-link/6173736574732f696d706163742d736f756e6473'
request=urllib.request.Request(endpoint,headers={'Referer':page,'Accept':'application/json'})
signed=json.loads(opener.open(request,timeout=30).read())
(SOURCE/'public-download-link-response.json').write_text(json.dumps(signed,indent=2))
print(signed.keys())
url=signed.get('url',signed.get('download_url'))
assert isinstance(url,str), signed
data=opener.open(urllib.request.Request(url,headers={'Referer':page}),timeout=60).read()
dest=SOURCE/'kenney_impact-sounds-valid.zip';assert not dest.exists();dest.write_bytes(data)
with zipfile.ZipFile(dest) as z:
    names=z.namelist()
    for name in names:
        if name.lower().endswith('.ogg') or name.lower().endswith('license.txt'):
            target=SOURCE/name
            assert SOURCE.resolve() in target.resolve().parents
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
record={'creator':'Kenney','primary_page':page,'download_method':'Official public Continue without donating signed link endpoint, no account/payment','license':'CC0 1.0 Universal','archive':str(dest),'sha256':hashlib.sha256(data).hexdigest(),'files':names,'first_attempt':'Old static link returned HTML, retained as failed download evidence.'}
(ROOT/'AUDIO-SOURCE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'bytes':len(data),'files':names}))
