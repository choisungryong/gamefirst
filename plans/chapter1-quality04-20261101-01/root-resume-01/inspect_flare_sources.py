from pathlib import Path
import urllib.request,json,hashlib
OUT=Path('C:/Project/game-research/art-sources/flare-hd-20261101-01')
OUT.mkdir(parents=True,exist_ok=True)
target=OUT/'repository-tree.json';assert not target.exists()
url='https://api.github.com/repos/flareteam/flare-game-art-src/git/trees/master?recursive=1'
req=urllib.request.Request(url,headers={'User-Agent':'AshenCloister-asset-research','Accept':'application/vnd.github+json'})
with urllib.request.urlopen(req,timeout=60) as response:raw=response.read()
with target.open('xb') as f:f.write(raw)
tree=json.loads(raw)
selected=[x for x in tree.get('tree',[]) if any(s in x['path'].lower() for s in ['heroine','characters/hero/','license','credits'])]
result={'source_url':url,'tree_sha':tree['sha'],'truncated':tree.get('truncated'),'tree_sha256':hashlib.sha256(raw).hexdigest(),'selected':selected}
with (OUT/'selected.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps({'tree_sha':tree['sha'],'truncated':tree.get('truncated'),'selected':[{'path':x['path'],'bytes':x.get('size')} for x in selected]},indent=2))
