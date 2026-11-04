from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline')
E=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    assert not p.exists(),p
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=json.loads((E.parent/'source-manifest.json').read_text(encoding='utf-8'))
changed=['chapter1/view/cloister_hud.gd','chapter1/view/flame_bloom.gdshader']
assert all(sha(E/'before'/p)==old[p] for p in changed)
assert all(sha(R/p)==s for p,s in old.items() if p not in changed)
current={p:sha(R/p) for p in old}
for p in changed:
    target=E/'source'/p
    target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists(),target
    shutil.copy2(R/p,target)
assert all(sha(E/'source'/p)==current[p] for p in changed)
write(E/'source-manifest.json',current)
groups={}
for name,path in [('core03','chapter1/evidence/core-pilot-20261031-03/source-manifest.json'),('baseline51','evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json')]:
    manifest=json.loads((R/path).read_text(encoding='utf-8'))
    if isinstance(manifest,list):manifest={v['path']:v['sha256'] for v in manifest}
    mismatches=[p for p,s in manifest.items() if sha(R/p)!=s]
    assert not mismatches,mismatches
    groups[name]={'count':len(manifest),'mismatches':mismatches}
runs=[]
for name,expected in [('layout-current',0),('layout-intentional',1),('layout-before',1)]:
    data=json.loads((E/'attempt04-raw'/(name+'-execution.json')).read_text(encoding='utf-8'))
    assert data['actual_exit']==expected
    assert not data['stderr']
    line=next(v for v in data['stdout'].splitlines() if v.startswith('QUALITY_HUD_LAYOUT '))
    result=json.loads(line.split(' ',1)[1])
    runs.append({'name':name,'actual_exit':data['actual_exit'],'checks':result['checks'],'failures':result['failures']})
write(E/'FREEZE.json',{'runtime_source_count':len(current),'changed_files':changed,'source_manifest_sha256':sha(E/'source-manifest.json'),'v01_before_copies_match':True,'unchanged_v01_files':len(old)-2,'unchanged_groups':groups,'layout_runs':runs,'scope':'Headless container/text geometry only; actual GPU shader compile, all3skills images, visual acceptance and hearing remain open.'})
print('v02 freeze33; changed2; unchanged31; core9 baseline51 match; current99 exit0, intentional100 exit1, legacy99 exit1')
