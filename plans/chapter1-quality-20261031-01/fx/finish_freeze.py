from pathlib import Path
import json,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');PROOF=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
target=PROOF/'source-manifest.json';manifest=json.loads(target.read_text())
groups={}
for label,mp in [('core03',ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json'),('baseline51',ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json')]:
    pin=json.loads(mp.read_text());entries=pin.items() if isinstance(pin,dict) else [(r['path'],r['sha256']) for r in pin]
    mismatches=[p for p,h in entries if sha(ROOT/p)!=h]
    groups[label]={'count':len(pin),'mismatches':mismatches}
record={'runtime_source_count':len(manifest),'source_manifest_sha256':sha(target),'current_and_snapshot_match':all(sha(ROOT/n)==h==sha(PROOF/'source'/n) for n,h in manifest.items()),'unchanged_groups':groups,'freeze_writer_correction':'Initial writer assumeddictcoremanifest; it created33validsources+manifest thenfailedlist.items. That failure/script ispreserved; thisfinisherreadsexistingcopieswithoutrewriting.','scope':'Author freeze; separate GPU, visual/audio audition, independent review and package verification pending.'}
out=PROOF/'FREEZE.json';assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
