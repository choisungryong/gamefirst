from pathlib import Path
import hashlib,json,shutil
ROOT=Path('C:/Project/d2r-combat-baseline')
DEST=Path('C:/Project/game-research/implementation-backups/chapter1-nativefix02-before-20261031-01')
assert not DEST.exists()
manifest=json.loads((ROOT/'plans/chapter1-c2-20261031-01/package-candidate01/source-manifest.json').read_text())
paths=list(manifest)+['chapter1/tools/build_candidate.py','plans/chapter1-c2-20261031-01/package-candidate01/source-manifest.json','plans/chapter1-c2-20261031-01/package-candidate01/staging-manifest.json','plans/chapter1-c2-20261031-01/package-candidate01/native-menu-exit.json','builds/chapter1/chapter1-c2-candidate-20261031-01/qa-captures/root-native01/godot.log']
rows=[]
for name in paths:
    src=ROOT/name; dst=DEST/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    a=hashlib.sha256(src.read_bytes()).hexdigest();b=hashlib.sha256(dst.read_bytes()).hexdigest();assert a==b
    rows.append({'path':name,'sha256':a})
(DEST/'manifest.json').write_text(json.dumps({'files':rows,'scope':'Before input observer/HUD correction; candidate01 EXE and source evidence retained in place.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(rows),'backup':str(DEST)}))
