from pathlib import Path
from html.parser import HTMLParser
import urllib.request,urllib.parse,json,hashlib
OUT=Path('C:/Project/game-research/art-sources/oga-horror-monster-20261101-01');assert not OUT.exists();OUT.mkdir()
url='https://opengameart.org/content/3d-horror-game-monster'
data=urllib.request.urlopen(url,timeout=45).read();(OUT/'source.html').write_bytes(data)
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='img' and 'src'in attrs and '/sites/default/files/'in attrs['src']:self.urls.append(urllib.parse.urljoin(url,attrs['src']))
p=Parser();p.feed(data.decode('utf-8'));records={}
for i,u in enumerate(dict.fromkeys(p.urls)):
 if '/pictures/'in u or '/file-icons/'in u:continue
 suffix=Path(urllib.parse.urlsplit(u).path).suffix
 if suffix.lower()not in ['.png','.jpg','.jpeg','.webp']:continue
 content=urllib.request.urlopen(u,timeout=45).read();name='preview-%02d'%i+suffix;(OUT/name).write_bytes(content)
 records[name]={'url':u,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}
with(OUT/'PREVIEWS.json').open('x',encoding='utf-8')as f:json.dump({'source':url,'scope':'Author page previews only, not downloaded mesh/animation or adopted runtime','images':records},f,indent=2)
print(json.dumps(records))
