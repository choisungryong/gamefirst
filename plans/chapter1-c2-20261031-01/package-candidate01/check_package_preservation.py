"""Read-only hash validation, writing only new candidate evidence."""
from pathlib import Path
import hashlib
import json

ROOT = Path('C:/Project/d2r-combat-baseline')
PROOF = Path(__file__).resolve().parent
OUT = PROOF / 'package-preservation.json'
assert not OUT.exists()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
runtime = json.loads((PROOF / 'source-manifest.json').read_text())
old = json.loads((ROOT / 'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json').read_text())
core = json.loads((ROOT / 'chapter1/evidence/core-pilot-20261031-03/source-manifest.json').read_text())
expected = {
    ROOT/'builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe':'5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29',
    Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/equipment-v1.json'):'b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353',
    Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/progress-v1.json'):'56a9d80654774ec7fc013e1a1e4c7b614243c796f4d02d5af77059ab9849b227',
}
record = {
 'runtime_count':len(runtime), 'runtime_mismatches':[p for p,h in runtime.items() if sha(ROOT/p)!=h],
 'baseline_count':len(old), 'baseline_mismatches':[p for p,h in old.items() if sha(ROOT/p)!=h],
 'core03_count':len(core), 'core03_mismatches':[e['path'] for e in core if sha(ROOT/e['path'])!=e['sha256']],
 'fixed_files':[{'path':str(p),'expected':h,'actual':sha(p),'matches':sha(p)==h} for p,h in expected.items()],
 'scope':'Current hash comparison at package verification, not proof of unpinned historical evidence bytes.'
}
record['success'] = not any(record[k] for k in ('runtime_mismatches','baseline_mismatches','core03_mismatches')) and all(e['matches'] for e in record['fixed_files'])
OUT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(0 if record['success'] else 1)
