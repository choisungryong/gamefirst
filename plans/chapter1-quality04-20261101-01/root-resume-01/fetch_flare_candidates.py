from pathlib import Path
import urllib.request,json,hashlib
OUT=Path('C:/Project/game-research/art-sources/flare-hd-20261101-01')
tree=json.loads((OUT/'repository-tree.json').read_text(encoding='utf-8'))
commit=tree['sha'];known={x['path']:x for x in tree['tree']}
paths=['README.md','LICENSE.txt','CREDITS.txt','CREDITS_FLARE_GAME.txt','art_src_hd/characters/heroine/heroine.blend']
for name in ['head_long','leather_chest','leather_pants','leather_boots','leather_gloves','staff']:
    paths+=['mods/hd-flare-game/images/avatar/female/'+name+'.png','art_src_hd/mod_data/core/animations/avatar/female/'+name+'.txt']
manifest=[]
for path in paths:
    assert path in known,path
    target=OUT/'files'/path;assert not target.exists(),str(target)
    url='https://raw.githubusercontent.com/flareteam/flare-game-art-src/'+commit+'/'+path
    req=urllib.request.Request(url,headers={'User-Agent':'AshenCloister-asset-research'})
    with urllib.request.urlopen(req,timeout=60) as response:data=response.read()
    assert len(data)==known[path]['size'],{'path':path,'expected':known[path]['size'],'actual':len(data)}
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
    manifest.append({'path':path,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'status':'research candidate only, not adopted runtime'})
with (OUT/'download-manifest.json').open('x',encoding='utf-8') as f:json.dump({'git_tree_sha':commit,'files':manifest},f,ensure_ascii=False,indent=2)
print(json.dumps({'count':len(manifest),'bytes':sum(x['bytes'] for x in manifest),'manifest':str(OUT/'download-manifest.json')}))
