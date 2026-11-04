"""Read-only three-skill connection proof; original runs are never rewritten."""
from pathlib import Path
import argparse
import hashlib
import json
from collections import Counter


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.output.exists(), 'Preserve prior audit'
    directory = args.directory
    read = lambda name: json.loads((directory / name).read_text(encoding='utf-8-sig'))
    launch, receipt, summary = read('launch.json'), read('receipt.json'), read('case/summary.json')
    events = read('case/combat-events.json')
    skills = ['skill.ember_bolt', 'skill.frost_pulse', 'skill.arc_chain']
    counts = {s: dict(Counter(row['event']['kind'] for row in events if row['selected_skill'] == s)) for s in skills}
    errors = []
    for skill in skills:
        for kind in ('release', 'hit'):
            if counts[skill].get(kind, 0) <= 0:
                errors.append(f'{skill}: no {kind} event')
    harness = directory / 'external-harness.gd'
    if sha(harness) != launch['external_script_sha256'] or sha(harness) != summary['external_script_sha256']:
        errors.append('Harness snapshot pin mismatch')
    if receipt['actual_exit'] != 0 or not receipt['report_success'] or receipt['stderr_bytes'] != 0:
        errors.append('Run receipt failed')
    if receipt['source_mismatches'] or not receipt['native_guards_unchanged']:
        errors.append('Source/native guard mismatch')
    equipped = summary['fixture']['equipment']['equipped']
    if equipped != {'body': 2, 'charm': 3, 'focus': 1}:
        errors.append('Three-item fixture not equipped')
    result = {'scope': 'Short selected-skill-labelled release/hit connection proof only; not formal timing, statistical damage proof, or proof of formal-run per-skill counts',
              'directory': str(directory), 'counts': counts,
              'min_event_tick': min(row['event']['tick'] for row in events),
              'max_event_tick': max(row['event']['tick'] for row in events),
              'events_sha256': sha(directory / 'case/combat-events.json'),
              'harness_sha256': sha(harness), 'exe_sha256': receipt['exe_sha256'],
              'equipment': equipped, 'failures': errors, 'success': not errors}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
