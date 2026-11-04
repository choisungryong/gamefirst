from pathlib import Path
import json,hashlib,importlib.util
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).resolve().parent;RESUME=HERE.parent/'root-resume-01'
def write(path,value):
 with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for name in ['ember','frost','arc']:
 p=RESUME/('full09-release-'+name+'-execution.json');j=json.loads(p.read_text(encoding='utf-8'))
 states=[json.loads(line.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for line in j['stdout'].splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in line]
 result=states[-1];assert j['actual_exit']==0 and not j['stderr'] and result['mode']=='victory' and all(s['cleared'] for s in result['chapter']['seals'])
 assert result['profile_off'] and result['pilot'] and result['elite_reward_uid']>0
 rows.append({'primary':name,'actual_exit':0,'stderr_bytes':0,'seconds':result['tick']/60,'kills':result['kills'],'level':result['growth']['level'],'evolved':result['growth']['evolved'],'max_alive':result['metrics']['max_alive'],'events_dropped':result['metrics']['events_dropped'],'owned_final_reward_uid':result['elite_reward_uid'],'three_seals_cleared':True,'execution_file':str(p),'execution_sha256':sha(p),'history':result['chapter']['history']})
write(HERE/'NORMAL-RELEASE-RESULTS.json',{'runs':rows,'scope':'Packaged release, headless fixed60fps normal input policy, no resource grants/profile IO. Not manual/GPU performance/audio-hearing approval. Console localized strings contain replacement characters; numerical/state results only.'})
spec=importlib.util.spec_from_file_location('frozen_package',HERE/'package_full09.py');pkg=importlib.util.module_from_spec(spec);spec.loader.exec_module(pkg)
pins=json.loads((HERE/'FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'));pkg.check(ROOT,pins)
write(HERE/'FINAL-PRESERVATION.json',{'runtime_freeze_matches':True,'pins':pkg.preservation(),'scope':'Selected baseline51, backup77, historicalEXEs3/profiles2, old candidate03 stage72. Does not assert every historical sidecar unchanged.'})
print(json.dumps([{k:v for k,v in row.items() if k!='history'} for row in rows],ensure_ascii=False))
