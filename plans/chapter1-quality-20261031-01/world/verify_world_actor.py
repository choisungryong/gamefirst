"""Current world/actor boundaries, immutable intake pins, and actual test exits."""
from pathlib import Path
import json, hashlib, subprocess
ROOT=Path('C:/Project/d2r-combat-baseline')
PROOF=ROOT/'plans/chapter1-quality-20261031-01/world/verification01'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
assert not PROOF.exists();PROOF.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
core=json.loads((ROOT/'chapter1/evidence/core-pilot-20261031-03/source-manifest.json').read_text(encoding='utf-8'))
old=json.loads((ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json').read_text(encoding='utf-8'))
owned=['cloister_world.gd','cloister_world_quality03.gd','cloister_ground_quality03.gdshader','cloister_props_quality03.gdshader','cloister_contact_quality03.gdshader','cloister_actors.gd']
pins={'chapter1/view/'+name:sha(ROOT/'chapter1/view'/name) for name in owned}
(PROOF/'source-manifest.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
results={}
for label,script,negative in [('world-positive','test_world_quality03.gd',False),('world-negative','test_world_quality03.gd',True),('actor-positive','test_actor_quality03.gd',False),('actor-negative','test_actor_quality03.gd',True)]:
    command=[str(ENGINE),'--headless','--path',str(ROOT),'--script','res://plans/chapter1-quality-20261031-01/world/'+script]
    if negative:command+=['--','--prove-failure']
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    record={'command':command,'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'scope':'Synthetic headless presentation boundaries, not normal gameplay or rendering quality approval.'}
    (PROOF/(label+'-execution.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    assert result.returncode==(1 if negative else 0),label
    assert 'SCRIPT ERROR' not in result.stdout+result.stderr,label
    results[label]=result.returncode
summary={'exits':results,'source_mismatches':[p for p,h in pins.items() if sha(ROOT/p)!=h],'core03_mismatches':[r['path'] for r in core if sha(ROOT/r['path'])!=r['sha256']],'old_source51_mismatches':[p for p,h in old.items() if sha(ROOT/p)!=h],'candidate02_exe_sha256':sha(ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe')}
assert not summary['source_mismatches'] and not summary['core03_mismatches'] and not summary['old_source51_mismatches']
(PROOF/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
