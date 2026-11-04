from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17/independent-audit01';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={};freeze=read(B/'full17/FINAL-SOURCE-FREEZE.json');checks['root17_freeze']=all(sha(R/n)==h for n,h in freeze.items())
for number in [14,16,17]:
 closure=read(B/('full%d/build/closure.json'%number));stage=Path(closure['stage']);pins=read(B/('full%d/build/staging-manifest.json'%number));checks['stage%d_pins'%number]=all(sha(stage/n)==h for n,h in pins.items())
 build=read(B/('full%d/build/build.json'%number));checks['exe%d_pin'%number]=sha(Path(build['exe']))==build['sha256']
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before17-20261102-01');pins=read(backup/'manifest.json');checks['complete_root16_backup']=all(sha(backup/n)==h for n,h in pins.items())
keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];pacing={}
for name,key in [('full-release-proof.json','result'),('full-frost-proof.json','first_victory'),('full-arc-proof.json','first_victory')]:
 current=read(B/('full17/build/'+name))[key];previous=read(B/('full16/build/'+name))[key]
 for k in keys:checks[name+':'+k]=current[k]==previous[k]
 pacing[name]={'tick':current['tick'],'seconds':current['tick']/60,'kills':current['kills']}
native=read(B/'full17/runtime/native-gear01/execution.json');checks['native_exit0_quiet']=native=={'exit':0,'stderr_bytes':0}
spec=importlib.util.spec_from_file_location('pck_parser17',R/'tools/build_phase7.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
build=read(B/'full17/build/build.json');audit=read(B/'full17/build/pck-audit.json');actual=module.pck_entries(Path(build['exe']));checks['pck_reparse_matches']=actual['entries']==audit['entries'] and sha(Path(build['exe']))==audit['exe_sha256']
spec=importlib.util.spec_from_file_location('package17',B/'full17/package_full17.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package);selected_preservation=package.preservation()
result={'checks':checks,'pacing':pacing,'selected_historical_preservation':selected_preservation,'build':build,'scope':'Independent read-only root/stage/EXE/PCK, complete16backup, 30 headless state comparisons and native exit audit. GPU result remains separate; not every historical byte/user profile or formal performance/manual/audio approval.'}
(OUT/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'passed':len(checks),'build':build,'pacing':pacing},ensure_ascii=False),flush=True)
