from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent
SOURCE=BASE.parent/'core04/growth_regression_diagnostic.gd'
DEST=BASE/'growth_wall_diagnostic.gd'
assert not DEST.exists()
text=SOURCE.read_text(encoding='utf-8')
needle='\tif nearest < 1.35 and move.length_squared() > .1: run.request_dash(move)'
assert text.count(needle)==1
text=text.replace(needle,'''\t# Separate diagnostic policy: ordinary movement input must not keep steering
\t# outward after the hero reaches the arena wall. No game state is granted.
\tif policy == "primary-first-wall-aware":
\t\tvar at:Vector2=run.hero.position
\t\tfor axis in 2:
\t\t\tif absf(at[axis])>16.0:
\t\t\t\tif signf(move[axis])==signf(at[axis]):move[axis]=0.0
\t\t\t\tmove[axis]-=signf(at[axis])*.85
\t\tmove=move.limit_length(1.0)
'''+needle)
text=text.replace('if policy == "primary-first-normal-choices": selected = offer.cards[0]','if policy.begins_with("primary-first"): selected = offer.cards[0]')
text=text.replace('for driver in ["fixed-normal-driver","primary-first-normal-choices"]:','for driver in ["fixed-normal-driver","primary-first-normal-choices","primary-first-wall-aware"]:')
with DEST.open('x',encoding='utf-8') as f:f.write(text)
with (BASE/'wall-diagnostic-provenance.json').open('x',encoding='utf-8') as f:
    json.dump({'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'derived':str(DEST),'derived_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'scope':'Adds an explicitly separate wall-aware normal-input policy; original driver/outcomes remain unchanged. No HP/XP/items/seed grants.'},f,indent=2)
