from pathlib import Path
import json
HERE=Path(__file__).parent
rows=[]
for name in ['ember','frost','arc']:
 p=HERE/('full09-release-'+name+'-execution.json')
 if not p.exists():continue
 j=json.loads(p.read_text(encoding='utf-8'))
 values=[json.loads(s.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for s in j['stdout'].splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in s]
 r=values[-1]
 rows.append({'primary':name,'actual_exit':j['actual_exit'],'stderr_bytes':len(j['stderr'].encode()),'mode':r['mode'],'elapsed_seconds':r['tick']/60,'kills':r['kills'],'level':r['growth']['level'],'evolved':r['growth']['evolved'],'max_alive':r['metrics']['max_alive'],'events_dropped':r['metrics']['events_dropped'],'final_owned_reward':r['elite_reward_uid'],'three_seals_cleared':all(s['cleared'] for s in r['chapter']['seals']),'history':r['chapter']['history'],'scope':'Packaged release headless/fixed60fps normal driver, not manual/GPU performance. Raw localized console strings show replacement characters; numeric/state proof only.'})
print(json.dumps(rows,ensure_ascii=False,indent=2))
