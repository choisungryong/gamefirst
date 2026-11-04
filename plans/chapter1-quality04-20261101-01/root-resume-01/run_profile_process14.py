from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full14/profile-process01';STAGE=Path('C:/Project/game-research/build-staging/chapter1-profile-process-20261101-01')
USER=Path('C:/Users/twins/AppData/Roaming/Godot/app_userdata/AshenCloisterChapterOneProfileProcessQA20261101A')
assert not OUT.exists()and not STAGE.exists()and not USER.exists();OUT.mkdir();STAGE.mkdir()
pins=json.loads((BASE/'full14/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=[n for n in pins if n.startswith(('chapter1/core/','chapter1/data/','combat/'))]
for n in names:
 assert sha(ROOT/n)==pins[n]
 p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p)
(STAGE/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Isolated Profile Process14"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapterOneProfileProcessQA20261101A"\n',encoding='utf-8')
shutil.copy2(Path(__file__).with_name('profile_process14.gd'),STAGE/'profile_process.gd')
(OUT/'source.json').write_text(json.dumps({'stage':str(STAGE),'runtime_source_sha256':{n:pins[n]for n in names},'user_namespace':str(USER),'initial_user_directory_absent':True,'scope':'Backend cross-process/default user save path; no native profile UI or concurrent writers'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for phase in ['create','restart','finish']:
 cmd=[engine,'--headless','--path',str(STAGE),'--script','res://profile_process.gd','--','--profile-phase='+phase]
 r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
 report={'command':cmd,'actual_exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr};(OUT/(phase+'-execution.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 assert r.returncode==0 and not r.stderr,report
 result=json.loads((STAGE/(phase+'-result.json')).read_text(encoding='utf-8'));assert not result['failures'];shutil.copy2(STAGE/(phase+'-result.json'),OUT/(phase+'-result.json'));print(json.dumps({'phase':phase,'checks':result['checks'],'revision':result['state']['revision'],'owned':len(result['state']['items'])}),flush=True)
shutil.copytree(USER,OUT/'user-save-snapshot')
assert all(sha(ROOT/n)==h for n,h in pins.items())
(OUT/'RESULT.json').write_text(json.dumps({'independent_processes':3,'all_exit0_stderr0':True,'root14_freeze_matches':True,'qa_user_files_retained':{p.name:sha(p)for p in USER.iterdir()if p.is_file()},'scope':'Actual default user-save3-process nonempty restart/idempotent receipt/starter-import/no duplication, exact14 core; no native stash UI or simultaneous CAS/power-loss proof'},indent=2),encoding='utf-8')
