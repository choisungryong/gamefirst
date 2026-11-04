from pathlib import Path
import json,hashlib,shutil
ROOT=Path('C:/Project/d2r-combat-baseline')
PROOF=Path(__file__).resolve().parent
paths=['chapter1/chapter_view.gd','chapter1/view/cloister_effects.gd','chapter1/view/cloister_hud.gd','chapter1/view/element_emblem.gd','chapter1/view/comet.gdshader','chapter1/view/impact.gdshader','chapter1/view/flame_bloom.gdshader','chapter1/view/element_particle.gdshader','chapter1/presentation/combat_audio.gd']
paths+=sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'chapter1/art/quality03_audio').iterdir() if p.is_file())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={name:sha(ROOT/name) for name in paths}
target=PROOF/'source-manifest.json';assert not target.exists()
for name in paths:
    dest=PROOF/'source'/name;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
target.write_text(json.dumps(manifest,indent=2)+'\n')
groups={}
for label,mp in [('core03',ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json'),('baseline51',ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json')]:
    pin=json.loads(mp.read_text())
    mismatches=[p for p,h in pin.items() if sha(ROOT/p)!=h]
    groups[label]={'count':len(pin),'mismatches':mismatches}
record={'runtime_source_count':len(paths),'source_manifest_sha256':sha(target),'current_and_snapshot_match':all(sha(ROOT/n)==sha(PROOF/'source'/n) for n in paths),'unchanged_groups':groups,'scope':'Author freeze; separate GPU, visual/audio audition, independent review and package verification pending.'}
(PROOF/'FREEZE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
