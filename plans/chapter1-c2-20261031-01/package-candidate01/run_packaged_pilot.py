"""One owned packaged GPU run. Records actual exit and never overwrites evidence."""
from pathlib import Path
import json
import subprocess
import time

PROOF = Path(__file__).resolve().parent
EXE = Path('C:/Project/d2r-combat-baseline/builds/chapter1/chapter1-c2-candidate-20261031-01/AshenCloister-Chapter1.exe')
DEST = EXE.parent / 'qa-captures/package-pilot01'
assert not DEST.exists()
assert not (PROOF / 'packaged-pilot-execution.json').exists()
DEST.mkdir(parents=True)
command = [str(EXE), '--resolution', '1920x1080', '--log-file', str(DEST / 'godot.log'), '--',
           '--chapter1-start', '--chapter1-pilot', '--chapter1-qa-ignore-focus',
           '--chapter1-quit-after=100', '--chapter1-capture-dir=' + str(DEST)]
started = time.time()
result = subprocess.run(command, capture_output=True, text=True, timeout=180)
record = {'command': command, 'actual_exit': result.returncode, 'stdout': result.stdout,
          'stderr': result.stderr, 'elapsed_wall_seconds': time.time() - started,
          'scope': 'Explicit QA normal-input driver, ignore-focus flag and synchronous PNG capture. Not formal GPU or quality approval.'}
(PROOF / 'packaged-pilot-execution.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'actual_exit': result.returncode, 'evidence': str(PROOF / 'packaged-pilot-execution.json')}))
raise SystemExit(result.returncode)
