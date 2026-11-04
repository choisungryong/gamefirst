from pathlib import Path
import urllib.request,json,hashlib
OUT=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01')
OUT.mkdir(parents=True,exist_ok=True)
items=[('preview.jpg','https://opengameart.org/sites/default/files/screen_1.jpg'),('mage_final.blend','https://opengameart.org/sites/default/files/mage_final.blend')]
files=[]
for name,url in items:
    target=OUT/name;assert not target.exists()
    request=urllib.request.Request(url,headers={'User-Agent':'AshenCloister-asset-research'})
    with urllib.request.urlopen(request,timeout=60) as response:data=response.read()
    assert data.startswith(b'BLENDER') if name.endswith('.blend') else data.startswith(b'\xff\xd8')
    with target.open('xb') as f:f.write(data)
    files.append({'path':str(target),'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
with (OUT/'SOURCE.json').open('x',encoding='utf-8') as f:
    json.dump({'title':'Rigged, textured mage','author':'thecubber','rig_credit':'Julius / OGA rig as credited by author','source_page':'https://opengameart.org/content/rigged-textured-mage','license':'CC-BY-SA 3.0','license_url':'https://creativecommons.org/licenses/by-sa/3.0/','access':'Public author asset page inspected via normal CUA browser; no login, payment or challenge. Asset links present in page.','status':'research candidate, not runtime adopted','files':files},f,ensure_ascii=False,indent=2)
print(json.dumps({'files':files,'status':'research only'}))
