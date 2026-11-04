from pathlib import Path
import hashlib,json
ROOT=Path('C:/Project/d2r-combat-baseline')
PROOF=Path(__file__).resolve().parent
OUT=PROOF/'preservation-before-native-exit.json'
assert not OUT.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
current=json.loads((PROOF/'source-manifest.json').read_text())
old=json.loads((ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json').read_text())
core=json.loads((ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json').read_text())
stage02=Path('C:/Project/game-research/build-staging/chapter1-c2-candidate-20261031-02')
stage01=Path('C:/Project/game-research/build-staging/chapter1-c2-candidate-20261031-01')
staged02=json.loads((PROOF/'staging-manifest.json').read_text())
staged01=json.loads((ROOT/'plans/chapter1-c2-20261031-01/package-candidate01/staging-manifest.json').read_text())
fixed={
 ROOT/'builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe':'5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29',
 ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-01/AshenCloister-Chapter1.exe':'fc9e41da23af5ae004204bb3fb12f63d9c7acfc34adbf9e43d00e71d11be027d',
 Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/equipment-v1.json'):'b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353',
 Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/progress-v1.json'):'56a9d80654774ec7fc013e1a1e4c7b614243c796f4d02d5af77059ab9849b227',
}
record={
 'runtime42_mismatches':[p for p,h in current.items() if sha(ROOT/p)!=h],
 'core03_nine_mismatches':[e['path'] for e in core if sha(ROOT/e['path'])!=e['sha256']],
 'baseline51_mismatches':[p for p,h in old.items() if sha(ROOT/p)!=h],
 'stage02_44_mismatches':[p for p,h in staged02.items() if sha(stage02/p)!=h],
 'stage01_44_mismatches':[p for p,h in staged01.items() if sha(stage01/p)!=h],
 'fixed_files':[{'path':str(p),'sha256':sha(p),'matches':sha(p)==h} for p,h in fixed.items()],
 'scope':'Current exact pins at this check; no claim of unpinned historical evidence-byte recovery.'
}
record['success']=not any(v for k,v in record.items() if k.endswith('_mismatches')) and all(e['matches'] for e in record['fixed_files'])
OUT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(0 if record['success'] else 1)
