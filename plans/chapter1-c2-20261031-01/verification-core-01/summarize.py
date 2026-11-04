import hashlib, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[2]
old = json.loads((ROOT/'chapter1/evidence/core-pilot-20261031-02/results.json').read_text())
new = json.loads((OUT/'normal-results.json').read_text())
def strip_cpu(v):
    if isinstance(v, dict): return {k: strip_cpu(x) for k,x in v.items() if k != 'cpu_wall_us'}
    if isinstance(v, list): return [strip_cpu(x) for x in v]
    return v
rows = []
for r in new['cases']:
    ids = ['chapter1.skill.'+s for s in ['ember','frost','arc']]
    rows.append({k:r[k] for k in ['primary','seed','mode','tick','elapsed','kills','hp_raw','elite_spawned','elite_killed','inventory_count','equipped']} | {
        'max_alive':r['metrics']['max_alive'], 'casts':r['metrics']['casts'], 'hits':r['metrics']['hits'],
        'three_skills_learned':all(s in r['growth']['ranks'] for s in ids),
        'primary_evolved':r['primary'] in r['growth']['evolved'],
        'all_three_cast_and_hit':all(r['metrics']['casts'].get(s,0)>0 and r['metrics']['hits'].get(s,0)>0 for s in ids),
        'all_four_equipped':set(r['equipped']) == {'body','charm','ring','weapon'},
        'event_overflow':r['metrics']['events_dropped']})
deps = ['combat/combat_resolver.gd','combat/stat_block.gd','chapter1/core/COMBAT-RUN.ko.md','chapter1/tests/test_growth.gd','project.godot']
summary = {
    'scope':'Frozen candidate02 core only; one known reward-cap counterexample; no art/GPU/audio/fun/complete-chapter approval.',
    'normal_pilot_identical_to_frozen_report_except_cpu_wall':strip_cpu(old)==strip_cpu(new),
    'cases':rows,
    'executions':{p.stem:json.loads(p.read_text())['actual_exit_code'] for p in OUT.glob('*-execution.json')},
    'dependency_and_contract_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in deps},
    'verifier_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.suffix in ['.py','.gd'] or p.name=='independent-v1-source.gd.txt'},
    'known_issue':{'source':'chapter1/core/combat_run.gd:583-584','case':'32 ground items, 0 owned items, kill elite => victory and 0 elite owned rewards','severity':'P2 correctness, not a crash or normal-pilot blocker; ground capacity unnecessarily blocks direct elite inventory reward'},
    'harness_correction':'independent-execution.json actual1 was a verifier coordinate error: point(10,1.0) is within0.44m of +0.14rad fan ray. Corrected point(10,0.7) lies between rays. Both raw logs and original source preserved; v2 actual0/45 checks still explicitly reproduces reward-cap issue.'
}
p = OUT/'verification-summary.json'
if p.exists(): raise RuntimeError('Refusing overwrite')
p.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
