from pathlib import Path
import hashlib,json,shutil
ROOT=Path('C:/Project/d2r-combat-baseline')
DEST=Path('C:/Project/game-research/implementation-backups/chapter1-quality04-before-20261101-01')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not DEST.exists(), 'Preserve prior backup; select new id'
runtime=json.loads((ROOT/'plans/chapter1-quality-20261031-01/package03/build/source-manifest.json').read_text(encoding='utf-8'))
core=json.loads((ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json').read_text(encoding='utf-8'))
core={r['path']:r['sha256'] for r in core}
for group in (runtime,core):
    assert all(sha(ROOT/p)==h for p,h in group.items()), 'Pre-change runtime/core pins differ'
paths=set(runtime)|set(core)|{'HANDOFF.md','plans/chapter1-quality-20261031-01/STATUS.ko.md','plans/chapter1-quality-20261031-01/book-v03/BOOK-ARTIFACTS.json','plans/chapter1-quality-20261031-01/package03/FINAL-SOURCE-FREEZE.json'}
manifest={}
for name in sorted(paths):
    src=ROOT/name; dst=DEST/'source'/name
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    assert sha(src)==sha(dst)
    manifest[name]={'sha256':sha(src),'bytes':src.stat().st_size}
extra={
    'builds/chapter1/chapter1-c2-candidate-20261101-03/AshenCloister-Chapter1.exe':'c916e280facbc89c6fcb1b21ee9a3fc9725313e248956e1918342ac2d4602fbb',
    'builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe':'111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188',
    'builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe':'5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29',
    'C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/equipment-v1.json':'b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353',
    'C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/progress-v1.json':'56a9d80654774ec7fc013e1a1e4c7b614243c796f4d02d5af77059ab9849b227'}
pins={}
for name,expected in extra.items():
    src=ROOT/name; actual=sha(src);assert actual==expected,name
    pins[name]={'sha256':actual,'bytes':src.stat().st_size}
    # Existing immutable EXEs are pinned in place; profile bytes additionally copied.
    if 'AppData/' in name:
        dst=DEST/'user-profiles'/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(dst)==actual
record={'source_count':len(manifest),'runtime70_count':len(runtime),'core03_count':len(core),'files':manifest,'pinned_exes3_profiles2':pins,'book_v03_artifacts_sha256':sha(ROOT/'plans/chapter1-quality-20261031-01/book-v03/BOOK-ARTIFACTS.json'),'scope':'Pre-quality04 backup. Core03/runtime03 become historical pins when new core changes; original snapshots/builds/evidence remain.'}
(DEST/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'backup_ready':True,'path':str(DEST/'manifest.json'),'source_count':len(manifest),'manifest_sha256':sha(DEST/'manifest.json')}))
