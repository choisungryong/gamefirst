from pathlib import Path
import hashlib,json
ROOT=Path('C:/Project/d2r-combat-baseline');PROOF=Path(__file__).resolve().parent
OUT=PROOF/'preservation-after-native-exit.json';assert not OUT.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
core=load(ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json')
groups={
 'runtime42':(ROOT,load(PROOF/'source-manifest.json')),
 'core03nine':(ROOT,{e['path']:e['sha256'] for e in core}),
 'baseline51':(ROOT,load(ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json')),
 'stage02':(Path('C:/Project/game-research/build-staging/chapter1-c2-candidate-20261031-02'),load(PROOF/'staging-manifest.json')),
 'stage01':(Path('C:/Project/game-research/build-staging/chapter1-c2-candidate-20261031-01'),load(ROOT/'plans/chapter1-c2-20261031-01/package-candidate01/staging-manifest.json')),
}
rows={label:{'count':len(pin),'mismatches':[name for name,h in pin.items() if sha(base/name)!=h]} for label,(base,pin) in groups.items()}
fixed={
 ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe':'111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188',
 ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-01/AshenCloister-Chapter1.exe':'fc9e41da23af5ae004204bb3fb12f63d9c7acfc34adbf9e43d00e71d11be027d',
 ROOT/'builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe':'5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29',
 Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/equipment-v1.json'):'b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353',
 Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/progress-v1.json'):'56a9d80654774ec7fc013e1a1e4c7b614243c796f4d02d5af77059ab9849b227',
}
files=[{'path':str(p),'sha256':sha(p),'matches':sha(p)==h} for p,h in fixed.items()]
record={'groups':rows,'fixed_files':files,'success':not any(e['mismatches'] for e in rows.values()) and all(e['matches'] for e in files),'scope':'Current pins after native exit; does not prove unpinned historical bytes.'}
OUT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,ensure_ascii=False));raise SystemExit(0 if record['success'] else 1)
