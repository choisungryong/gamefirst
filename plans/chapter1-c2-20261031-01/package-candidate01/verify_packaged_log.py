"""Validate emitted package proof without granting a visual/performance pass."""
from pathlib import Path
import hashlib
import json

PROOF = Path(__file__).resolve().parent
DEST = Path('C:/Project/d2r-combat-baseline/builds/chapter1/chapter1-c2-candidate-20261031-01/qa-captures/package-pilot01')
OUT = PROOF / 'packaged-runtime-summary.json'
assert not OUT.exists()
execution = json.loads((PROOF/'packaged-pilot-execution.json').read_text(encoding='utf-8'))
log = (DEST/'godot.log').read_text(encoding='utf-8')
def emitted(prefix):
    return [json.loads(line[len(prefix):]) for line in log.splitlines() if line.startswith(prefix)]
ready = emitted('CHAPTER1_READY ')
results = emitted('CHAPTER1_RUNTIME_RESULT ')
checks = {
 'actual_exit_zero': execution['actual_exit']==0,
 'ready_one': len(ready)==1,
 'all_five_imported_roles': len(ready)==1 and set(ready[0]['actor_states'])=={'hero','walker','ranged','charger','elite'},
 'all_action_and_direction_states': len(ready)==1 and all(set(['cast','hit','death','move_south','move_east','move_north','move_west']).issubset(states) for states in ready[0]['actor_states'].values()),
 'no_raw_png_fallback': len(ready)==1 and ready[0]['raw_texture_fallbacks']==[],
 'normal_input_driver_explicit':len(ready)==1 and ready[0]['pilot'] and ready[0]['qa_ignore_focus'],
 'result_present':bool(results),
 'no_error_warning':not any(term in log.upper() for term in ['ERROR:','SCRIPT ERROR:','WARNING:']),
}
record = {'checks':checks,'success':all(checks.values()),'ready':ready,'runtime_results':results,
          'captures':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(DEST.glob('*.png'))],
          'scope':'Imported resource/state and actual packaged run evidence only; not C2 quality approval, real audio listening, formal GPU result or completed chapter.'}
OUT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'success':record['success'],'checks':checks,'results':results}))
raise SystemExit(0 if record['success'] else 1)
