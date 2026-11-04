from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path('C:/Project/d2r-combat-baseline')
HERE = Path(__file__).resolve().parent
ENGINE = Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
CORE = ROOT/'chapter1/evidence/core-pilot-20261031-03'
PACKAGE = ROOT/'plans/chapter1-c2-20261031-01/package-candidate01'
FIX = {
    'chapter1/chapter_view.gd': 'a315c708027238b13a508a45ae0f9d36c3bd0a7a385421fee6e605f37f842bb9',
    'chapter1/view/cloister_hud.gd': '30360c68c4e8e0bce2e48a33ab6063a221ed74381a97571d662c2b740fea675b',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    p = HERE/name
    assert not p.exists(), 'Refusing to overwrite '+str(p)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def pins():
    core = []
    for e in json.loads((CORE/'source-manifest.json').read_text(encoding='utf-8')):
        current, saved = sha(ROOT/e['path']), sha(CORE/'source'/e['path'])
        core.append({'path':e['path'], 'expected':e['sha256'], 'current':current, 'saved':saved, 'match':current==saved==e['sha256']})
    package = json.loads((PACKAGE/'build.json').read_text(encoding='utf-8'))
    source = json.loads((PACKAGE/'source-manifest.json').read_text(encoding='utf-8'))
    runtime = [{'path':p, 'expected_current':FIX.get(p, h), 'current':sha(ROOT/p), 'match':sha(ROOT/p)==FIX.get(p, h)} for p,h in source.items()]
    baseline = json.loads((ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json').read_text(encoding='utf-8'))
    return {
        'core9':core,
        'runtime42_with_explicit_two_view_fixes':runtime,
        'old_package01_sha':sha(Path(package['exe'])),
        'old_package01_unchanged':sha(Path(package['exe']))==package['sha256'],
        'baseline51_mismatches':[p for p,h in baseline.items() if sha(ROOT/p)!=h],
        'fixture_sha256':sha(HERE/'independent_view.gd'),
    }

def run(label, args):
    log = HERE/(label+'-godot.log')
    observer = HERE/(label+'-observer.jsonl')
    assert not log.exists() and not observer.exists()
    command=[str(ENGINE), '--headless', '--path', str(ROOT), '--log-file', str(log), '--script', 'res://plans/chapter1-c2-20261031-01/verification-view-02/independent_view.gd', '--', '--chapter1-qa-input-log='+str(observer), *args]
    r=subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=60)
    write(label+'-execution.json', {'command':command, 'cwd':str(ROOT), 'actual_exit':r.returncode, 'stdout':r.stdout, 'stderr':r.stderr})
    print(label, r.returncode, r.stdout[-2000:], r.stderr[-1200:])
    return r.returncode

if __name__=='__main__':
    before=pins();write('pins-before.json', before)
    assert all(e['match'] for e in before['core9'])
    assert all(e['match'] for e in before['runtime42_with_explicit_two_view_fixes'])
    assert before['old_package01_unchanged'] and not before['baseline51_mismatches']
    codes={'positive':run('positive', []), 'negative':run('negative', ['--prove-failure'])}
    after=pins();write('pins-after.json', after)
    result={'codes':codes, 'pins_unchanged':before==after, 'scope':'Synthetic headless scene/HUD/key-handler checks. No GPU, OS keyboard, visual or normal-play approval.'}
    write('execution-summary.json', result)
    sys.exit(0 if codes=={'positive':0, 'negative':1} and before==after else 1)
