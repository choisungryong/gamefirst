import hashlib, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
GODOT = r'C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe'
manifest = json.loads((ROOT/'chapter1/evidence/core-pilot-20261031-02/source-manifest.json').read_text())

def pins():
    rows = []
    for pin in manifest:
        p = ROOT/pin['path']
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        frozen = ROOT/'chapter1/evidence/core-pilot-20261031-02/source'/pin['path']
        if not frozen.exists():
            frozen = ROOT/'chapter1/evidence/core-pilot-20261031-02/source'/p.name
        rows.append(dict(pin, actual=actual, match=actual==pin['sha256'],
                         archived_path=str(frozen), archived_matches=frozen.exists() and hashlib.sha256(frozen.read_bytes()).hexdigest()==pin['sha256']))
    return rows

def save(name, value):
    p = OUT/name
    if p.exists(): raise RuntimeError('Refusing to overwrite '+str(p))
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

mode = sys.argv[1]
if mode == 'pins':
    rows = pins(); save('pins-before.json', rows)
    print(json.dumps(rows)); sys.exit(0 if all(r['match'] and r['archived_matches'] for r in rows) else 1)

cases = {
    'functional': ['chapter1/tests/test_combat_run.gd'],
    'negative': ['chapter1/tests/test_combat_run.gd', '--prove-failure'],
    'growth': ['chapter1/tests/test_growth.gd'],
    'independent': ['plans/chapter1-c2-20261031-01/verification-core-01/independent.gd'],
    'independent-v2': ['plans/chapter1-c2-20261031-01/verification-core-01/independent.gd'],
    'dash-observation': ['plans/chapter1-c2-20261031-01/verification-core-01/dash-observation.gd'],
    'pilot': ['chapter1/tests/pilot_combat_run.gd', '--output='+str(OUT/'normal-results.json')],
}
if mode == 'pins-after':
    rows = pins(); save('pins-after.json', rows)
    print(json.dumps(rows)); sys.exit(0 if all(r['match'] and r['archived_matches'] for r in rows) else 1)
script, *args = cases[mode]
cmd = [GODOT, '--headless', '--path', str(ROOT), '--script', 'res://'+script]
if args: cmd += ['--']+args
result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=180)
row = dict(command=cmd, actual_exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
save(mode+'-execution.json', row)
print(json.dumps(row, ensure_ascii=False))
sys.exit(result.returncode)
