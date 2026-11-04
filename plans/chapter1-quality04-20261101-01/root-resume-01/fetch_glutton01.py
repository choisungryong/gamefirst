from pathlib import Path
import urllib.request,hashlib,json,datetime
OUT=Path('C:/Project/game-research/art-sources/oga-glutton-20261101-01')
assert not OUT.exists();OUT.mkdir(parents=True)
files={'source.html':'https://opengameart.org/content/glutton-demon','glutton_final.blend':'https://opengameart.org/sites/default/files/glutton_final_0.blend'}
records={}
for name,url in files.items():
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=90)as response:data=response.read();content_type=response.headers.get('Content-Type')
 if name.endswith('.blend'):assert data[:7]==b'BLENDER'
 (OUT/name).write_bytes(data)
 records[name]={'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'content_type':content_type}
with(OUT/'SOURCE.json').open('x',encoding='utf-8')as f:json.dump({'title':'Glutton Demon','author':'Teh_Bucket','concept_credit':'RayMooHawk (permission stated by source author)','license':'CC0','license_url':'https://creativecommons.org/publicdomain/zero/1.0/','fetched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records,'source_claims':'Author describes an original FreeDoom contribution with rig, animations and diffuse/normal textures; warns rig/UV issues. Must inspect actual files; no quality approval or runtime adoption yet.','scope':'Public research source. Never run embedded scripts; Blender --disable-autoexec only.'},f,indent=2)
print(json.dumps(records))
