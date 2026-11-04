"""Append-only same-EXE diagnostic. `prepare` never launches the game/GPU.

The scene reports all-playing-frame p95 only; it is not a raw frame trace or
the required 10-second warmup + 60-second formal performance measurement.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import time

ROOT = Path('C:/Project/d2r-combat-baseline')
OUT = Path(__file__).resolve().parent
EXE = ROOT/'builds/chapter1/chapter1-c2-candidate-20261101-03/AshenCloister-Chapter1.exe'
ENGINE = Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
EXPECTED_EXE = 'c916e280facbc89c6fcb1b21ee9a3fc9725313e248956e1918342ac2d4602fbb'
SCOPE = 'Nonformal same-EXE unsmoothed uncapped normal-pilot 0-70 second diagnostic; no raw trace, no excluded warmup, no formal 60FPS pass, no manual play.'
COMMAND = [str(EXE), '--windowed', '--always-on-top', '--position', '0,0',
    '--resolution', '1920x1080', '--delta-smoothing', 'disable', '--disable-vsync',
    '--max-fps', '0', '--', '--chapter1-start', '--chapter1-pilot',
    '--chapter1-seed=90131', '--chapter1-quit-after=70']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(name, data):
    path = OUT/name
    assert not path.exists(), 'Preserve previous evidence: '+str(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def pins():
    result = {}
    for label, path in [
        ('source70', 'plans/chapter1-quality-20261031-01/package03/build/source-manifest.json'),
        ('core9', 'chapter1/evidence/core-pilot-20261031-03/source-manifest.json'),
        ('baseline51', 'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json')]:
        expected = read(ROOT/path)
        if isinstance(expected, list):
            expected = {row['path']:row['sha256'] for row in expected}
        current = {p:sha(ROOT/p) for p in expected}
        result[label] = {'count':len(expected), 'current':current,
            'mismatches':[p for p in expected if expected[p] != current[p]]}
    extra = {
        str(EXE):EXPECTED_EXE,
        'builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe':'111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188',
        'builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe':'5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29',
        'C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/equipment-v1.json':'b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353',
        'C:/Users/twins/AppData/Roaming/Godot/app_userdata/D2R Combat Baseline/progress-v1.json':'56a9d80654774ec7fc013e1a1e4c7b614243c796f4d02d5af77059ab9849b227'}
    current = {p:sha(ROOT/p) for p in extra}
    result['exe3-save2'] = {'count':5, 'current':current,
        'mismatches':[p for p in extra if extra[p] != current[p]]}
    assert all(not row['mismatches'] for row in result.values()), result
    return result


def prepare():
    # Read-only CLI help is safe while another GPU activity owns the machine.
    help_run = subprocess.run([str(ENGINE), '--help'], capture_output=True)
    assert help_run.returncode == 0
    text = help_run.stdout.decode('utf-8', 'replace')
    flags = ['--resolution', '--always-on-top', '--delta-smoothing', '--disable-vsync', '--max-fps']
    assert all(flag in text for flag in flags)
    proof = {'command':COMMAND, 'cwd':str(EXE.parent), 'scope':SCOPE,
        'gpu_launched':False, 'pins':pins(),
        'cli_help':[line.strip() for line in text.splitlines() if any(flag in line for flag in flags)],
        'foreground_proof':'Root CUA must inspect/focus the actual window after launch. The runtime has no per-frame focus trace.',
        'not_collected':['raw Time.get_ticks_usec frame trace', '10-second excluded warmup', '3 repeated 60-second samples', 'maximum simultaneous 180 enemies', 'manual input', 'actual audio hearing']}
    write('PREPARATION.json', proof)
    print(json.dumps({'ready':True, 'no_gpu_launched':True, 'scope':SCOPE}))


def run():
    assert (OUT/'PREPARATION.json').exists()
    assert not any((OUT/name).exists() for name in ['RUNNING.json','execution.json','stdout.log','stderr.log','pins-before.json','pins-after.json'])
    before = pins()
    write('pins-before.json', before)
    started = time.time()
    with (OUT/'stdout.log').open('xb') as stdout, (OUT/'stderr.log').open('xb') as stderr:
        process = subprocess.Popen(COMMAND, cwd=EXE.parent, stdout=stdout, stderr=stderr)
        write('RUNNING.json', {'pid':process.pid, 'command':COMMAND, 'started_unix':started, 'scope':SCOPE})
        print(json.dumps({'pid':process.pid, 'root_cua_focus_now':True}), flush=True)
        # Root allocation is required before invoking this subcommand. Timeout
        # is a failure record, never an automatic relaunch or success rewrite.
        timed_out = False
        try:
            code = process.wait(timeout=115)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            code = process.wait(timeout=10)
    raw_stdout = (OUT/'stdout.log').read_bytes()
    raw_stderr = (OUT/'stderr.log').read_bytes()
    stdout_text = raw_stdout.decode('utf-8', 'replace')
    stderr_text = raw_stderr.decode('utf-8', 'replace')
    results = [json.loads(line.split('CHAPTER1_RUNTIME_RESULT ',1)[1]) for line in stdout_text.splitlines() if 'CHAPTER1_RUNTIME_RESULT ' in line]
    after = pins()
    write('pins-after.json', after)
    errors = re.findall(r'(?:SCRIPT ERROR|ERROR:|Parse Error|WARNING:).*', stdout_text+'\n'+stderr_text)
    record = {'command':COMMAND, 'cwd':str(EXE.parent), 'pid':process.pid,
        'actual_exit':code, 'timed_out':timed_out, 'wall_seconds':time.time()-started,
        'stdout':stdout_text, 'stderr':stderr_text, 'runtime_results':results,
        'source_and_preservation_pins_unchanged':before == after,
        'errors_or_warnings':errors, 'scope':SCOPE,
        'formal_performance_pass':False,
        'foreground_proof':'See separate root CUA observations; no per-frame focus telemetry.'}
    write('execution.json', record)
    print(json.dumps({'actual_exit':code, 'runtime_results':results, 'warnings':errors, 'scope':SCOPE}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare','run'])
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else run()
