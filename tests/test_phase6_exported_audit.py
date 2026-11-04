"""Read-only in-memory corruption checks for phase6 exported artifact auditor."""
from pathlib import Path
from copy import deepcopy
import json
import audit_phase6_exported_qa as auditor

directory=auditor.ROOT/'evidence/phase6/exported-qa-20261030-03'
original=auditor.read
cases=[]
def mutate_receipt(value): value[0]['actual_exit']=1
def mutate_metadata(value): value['metadata_sha256']='0'*64
def mutate_native(value): value['native_progress_after']='changed'
def mutate_skill(value): value['final']['skill']['damage_min_raw']+=1
def mutate_stats(value): value['final']['stats']['stat.health']+=1
def mutate_capture(value): value['captures'][0]['dimensions']=[1,1]
def mutate_xp(value): value['final']['progress']['xp']=6
def mutate_save(value): value['isolated_save_sha256']='0'*64
for filename, mutate in [('qa-receipts.json',mutate_receipt),('qa-report.json',mutate_metadata),('qa-report.json',mutate_native),('qa-report.json',mutate_skill),('qa-report.json',mutate_stats),('qa-report.json',mutate_capture),('qa-report.json',mutate_xp),('qa-report.json',mutate_save)]:
    def injected(path):
        value=deepcopy(original(path))
        if path.name==filename and directory in path.parents: mutate(value)
        return value
    auditor.read=injected
    result=auditor.audit(directory)
    cases.append({'case':mutate.__name__,'rejected':not result['success'],'failures':result['failures']})
auditor.read=original
valid=auditor.audit(directory)
result={'scope':'In-memory only: no historical source, user save or QA artifact writes','normal_success':valid['success'],'cases':cases,'success':valid['success'] and all(c['rejected'] for c in cases)}
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if result['success'] else 1)
