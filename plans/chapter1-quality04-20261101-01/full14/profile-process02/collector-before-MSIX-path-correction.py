from pathlib import Path
import json,hashlib,shutil
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full14/profile-process02'
rows=[]
for phase in ['create','restart','finish']:
 e=json.loads((OUT/(phase+'-execution.json')).read_text(encoding='utf-8'));assert e['actual_exit']==0 and not e['stderr']
 r=json.loads((OUT/(phase+'-result.json')).read_text(encoding='utf-8'));assert not r['failures'];rows.append(r)
user=Path(rows[0]['namespace']).resolve();base=Path('C:/Users/twins/AppData/Roaming').resolve()
assert user.parent==base and user.name=='AshenCloisterChapterOneProfileProcessQA20261101B',user
snapshot=OUT/'user-save-snapshot';assert not snapshot.exists();shutil.copytree(user,snapshot)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((BASE/'full14/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));assert all(sha(ROOT/n)==h for n,h in pins.items())
result={'independent_processes':3,'checks':sum(r['checks']for r in rows),'all_exit0_stderr0':True,'actual_user_namespace':str(user),'owned_after_restart':3,'selected_slots':rows[2]['state']['equipped'],'revision_after_defeat_restart':5,'starter_projectiles':2,'root14_freeze_matches':True,'qa_user_files_retained':{p.name:sha(p)for p in user.iterdir()if p.is_file()},'initial_profile_absent_proof':'create phase actual FileAccess check, not initial Python guessed directory','correction':'Python collector assumed Godot/app_userdata, but use_custom_user_dir places this namespace directly in AppData/Roaming. All3engine phases had already exited0 with31checks; only archival copy failed. Read actual OS.get_user_data_dir from verified phase report; copied exact uniqueQA directory without rerunning/mutating saves. Original source.json/exception preserved.','scope':'Exact14 core/default user path backend new-process nonempty restart/receipt idempotence/starter import/no duplication. No native stashUI, simultaneous CAS race or power loss proof.'}
p=OUT/'RESULT.json';assert not p.exists();p.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({'checks':result['checks'],'processes':3,'actual_user':str(user),'snapshot':str(snapshot)}),flush=True)
