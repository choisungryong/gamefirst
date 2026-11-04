from pathlib import Path
import hashlib,json
ROOT=Path('C:/Project/d2r-combat-baseline')
STAGE=Path('C:/Project/game-research/build-staging/chapter1-quality03-integrated-preview03')
PROOF=ROOT/'plans/chapter1-quality-20261031-01/world/preview03'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((PROOF/'staging-manifest.json').read_text(encoding='utf-8'))
record=json.loads((PROOF/'gpu-execution.json').read_text(encoding='utf-8'))
lines=record['stdout'].splitlines()
events={line.split(' ',1)[0]:json.loads(line.split(' ',1)[1]) for line in lines if line.startswith(('CHAPTER1_WORLD_ART ','CHAPTER1_AUDIO ','CHAPTER1_READY ','CHAPTER1_RUNTIME_RESULT '))}
summary={'actual_exit':record['actual_exit'],'stderr':record['stderr'],'pinned_files':len(pins),'source_mismatches':[p for p,h in pins.items() if sha(ROOT/p)!=h],'stage_mismatches':[p for p,h in pins.items() if sha(STAGE/p)!=h],'events':events,'images':{p.name:sha(p) for p in PROOF.glob('*.png')},'limitations':['45sec normalinput driver with synchronous captures, not formal performance','frame040 frost not learned; state0009 at41sec shows all3 learned','remaining repeated round foliage silhouettes and flat authored shading','not SACRATA quality approval or completed chapter']}
assert not summary['source_mismatches'] and not summary['stage_mismatches']
assert summary['actual_exit']==0 and not summary['stderr']
assert events['CHAPTER1_WORLD_ART']['raw_texture_fallbacks']==[]
assert events['CHAPTER1_AUDIO']['raw_fallbacks']==[]
assert events['CHAPTER1_READY']['raw_texture_fallbacks']==[]
out=PROOF/'FINAL-PINS.json';assert not out.exists()
out.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:summary[k] for k in ['actual_exit','pinned_files','source_mismatches','stage_mismatches']}))
