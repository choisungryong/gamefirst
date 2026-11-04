from pathlib import Path
import json,subprocess,sys
H=Path(__file__).parent;B=H.parent
s=(H/'run_performance29.py').read_text(encoding='utf-8')
old="assert 'quality26' in post['fx_script'] and 'quality25b' in post['actor_script']"
new="assert post['fx_script']=='res://chapter1/view/chapter_elements_quality26.gd' and post['actor_script']=='res://chapter1/view/chapter_actors_quality29.gd'"
assert s.count(old)==1;s=s.replace(old,new)
p=H/'run_performance29_v2.py';assert not p.exists();p.write_text(s,encoding='utf-8')
p=B/'full29/performance/runs/formal01/WRAPPER-AUDIT-REPAIR.json';assert not p.exists();p.write_text(json.dumps(dict(original_wrapper='run_performance29.py',failure='Inherited assertion expected actor quality25b, while actual target29 correctly loaded quality29. Actual EXE exit0/raw recordings retained; original wrapper failed and remains preserved.',correction='New v2 verifier pins exact actual29 actor and exact26 FX, all other raw checks unchanged. Re-audit existing data only, no repeated GPU.',startup_capture='Native UI screenshot immediately after Start during initial warmup. Exclude this run from the final three clean-start aggregation; retain complete data.'),indent=2))
subprocess.run([sys.executable,str(H/'run_performance29_v2.py'),'audit','--run-id','formal01'],check=True)
