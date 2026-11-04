"""Preserve the exact candidate02 intake before any quality03 mutations."""
from pathlib import Path
import hashlib, json, shutil

ROOT = Path('C:/Project/d2r-combat-baseline')
DEST = Path('C:/Project/game-research/implementation-backups/chapter1-quality03-before-20261031-01')
assert not DEST.exists(), 'Choose a new backup ID; never overwrite an existing intake'
DEST.mkdir(parents=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
runtime = json.loads((ROOT/'plans/chapter1-c2-20261031-01/package-candidate02/source-manifest.json').read_text(encoding='utf-8'))
old = json.loads((ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json').read_text(encoding='utf-8'))
core = json.loads((ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json').read_text(encoding='utf-8'))
names = set(runtime)
names.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'chapter1/art').rglob('*') if p.is_file() and p.suffix != '.import')
names.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'chapter1/tools').glob('*.py'))
names.update(['chapter1/README.ko.md','HANDOFF.md','IMPLEMENTATION-STATUS.ko.md','project.godot','export_presets.cfg'])
files = {}
for name in sorted(names):
    src=ROOT/name; dst=DEST/'source'/name
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    files[name]={'sha256':sha(src),'copy_sha256':sha(dst),'bytes':src.stat().st_size}
    assert files[name]['sha256']==files[name]['copy_sha256']
fixed={}
for name in ['builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe','builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe']:
    fixed[name]={'sha256':sha(ROOT/name),'bytes':(ROOT/name).stat().st_size}
profiles={}
profile_base=Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline')
for name in ['equipment-v1.json','progress-v1.json']:
    src=profile_base/name;dst=DEST/'native-profiles'/name
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    profiles[str(src)]={'sha256':sha(src),'copy_sha256':sha(dst)}
def mismatches(manifest):
    return [name for name,expected in manifest.items() if sha(ROOT/name)!=expected]
record={'source_files':files,'runtime42_mismatches':mismatches(runtime),'old_source51_mismatches':mismatches(old),'core03nine_mismatches':mismatches(core),'fixed_files':fixed,'native_profiles':profiles,'scope':'Pinned current source/art/doc intake; does not rewrite historical evidence.'}
assert not record['runtime42_mismatches'] and not record['old_source51_mismatches'] and not record['core03nine_mismatches']
(DEST/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'plans/chapter1-quality-20261031-01/.gdignore').write_text('',encoding='utf-8')
print(json.dumps({'backup':str(DEST),'source_count':len(files),'runtime42_mismatches':[],'old_source51_mismatches':[],'core03nine_mismatches':[]}))
