from pathlib import Path
import json,math
B=Path('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01');O=B/'actor28/mapped02'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));a=read(O/'25b/RESULT.json');d=read(O/'28/RESULT.json');expected=dict(walker=math.pi/2,ranged=math.pi,charger=-math.pi/2,elite=0)
err=lambda x,y:abs((x-y+math.pi)%(2*math.pi)-math.pi)
rows=[]
for role,target in expected.items():
 before=next(r for r in a['rows'] if r['phase']=='attack' and r['frame']==70)['angles'][role];after=next(r for r in d['rows'] if r['phase']=='attack' and r['frame']==70)['angles'][role]
 windup_before=next(r for r in a['rows'] if r['phase']=='attack' and r['frame']==20)['angles'][role];windup_after=next(r for r in d['rows'] if r['phase']=='attack' and r['frame']==20)['angles'][role]
 rows.append(dict(role=role,paid=target,before_recover=before,after_recover=after,after_paid_error=err(after,target),before_paid_error=err(before,target),windup_both_paid=err(windup_before,target)<.01 and err(windup_after,target)<.01))
passed=all(r['windup_both_paid'] and r['after_paid_error']<.01 and r['before_paid_error']>1 for r in rows)
p=O/'FACING-AUDIT01.json';assert not p.exists();p.write_text(json.dumps(dict(rows=rows,passed=passed,scope='Copied role fixture4cardinal paid directions; intentional perpendicular stale travel in recover. Windupframe20/recover70. Does not establish incidence in ordinary play or modify authoritative attack directions.'),indent=2));print(json.dumps(rows),flush=True);assert passed
