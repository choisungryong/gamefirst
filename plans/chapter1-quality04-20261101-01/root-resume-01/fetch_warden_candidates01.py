from pathlib import Path
from html.parser import HTMLParser
import urllib.request,urllib.parse,hashlib,json,zipfile
SOURCES=[('oga-skeleton-outlaw-20261101-01','Skeleton Outlaw','KevDev','CC0','https://opengameart.org/node/89457','https://opengameart.org/sites/default/files/SkeletonOutlaw_0.zip'),('oga-chained-demon-20261101-01','Chained Demon','Mophs','CC-BY3.0 selected from offered alternatives','https://opengameart.org/content/chained-demon','https://opengameart.org/sites/default/files/Chained_Demon_0.zip')]
for folder,title,author,license_,url,archive in SOURCES:
 out=Path('C:/Project/game-research/art-sources')/folder;assert not out.exists();out.mkdir()
 data=urllib.request.urlopen(url,timeout=60).read();(out/'source.html').write_bytes(data)
 payload=urllib.request.urlopen(archive,timeout=90).read();(out/'source.zip').write_bytes(payload)
 records=[]
 with zipfile.ZipFile(out/'source.zip')as z:
  assert sum(p.file_size for p in z.infolist())<400_000_000
  for member in z.infolist():
   target=(out/'extracted'/member.filename).resolve()
   assert target.is_relative_to((out/'extracted').resolve())
   records.append({'name':member.filename,'bytes':member.file_size})
   if not member.is_dir()and target.suffix.lower()in ['.blend','.fbx','.png','.tga','.jpg','.jpeg','.txt','.license']:
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(member))
 class P(HTMLParser):
  def __init__(self):super().__init__();self.urls=[]
  def handle_starttag(self,tag,attrs):
   a=dict(attrs)
   if tag=='img'and '/styles/medium/'in a.get('src',''):self.urls.append(urllib.parse.urljoin(url,a['src']))
 p=P();p.feed(data.decode('utf-8'));previews=[]
 for i,u in enumerate(dict.fromkeys(p.urls)):
  name='preview-%02d'%i+Path(urllib.parse.urlsplit(u).path).suffix
  content=urllib.request.urlopen(u,timeout=45).read();(out/name).write_bytes(content);previews.append({'name':name,'url':u,'sha256':hashlib.sha256(content).hexdigest()})
 with(out/'SOURCE.json').open('x',encoding='utf-8')as f:json.dump({'title':title,'author':author,'license':license_,'source':url,'archive':{'url':archive,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()},'entries':records,'previews':previews,'scope':'Public original art research, not runtime adoption. Archive paths validated; extracted only art/text; no embedded scripts executed.'},f,indent=2)
 print(json.dumps({'folder':str(out),'entries':records,'previews':previews}),flush=True)
