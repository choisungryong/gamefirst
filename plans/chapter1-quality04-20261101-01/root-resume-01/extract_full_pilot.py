from pathlib import Path
import json,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline')
p=ROOT/'chapter1/core/chapter_pilot.gd';assert not p.exists()
source=ROOT/'chapter1/tests/pilot_full_chapter.gd';s=source.read_text(encoding='utf-8');a=s.index('func equipment_score');b=s.index('func execute')
header='''extends RefCounted
## Explicit QA normal input policy; no resource grants.
const Chapter=preload("res://chapter1/core/chapter_run.gd")
var run: RefCounted
var selections: Array[Dictionary]=[]
var wall_avoidances := 0
var potion_uses := 0
'''
p.write_text(header+s[a:b],encoding='utf-8')
with (Path(__file__).parent/'full-pilot-extraction.json').open('x',encoding='utf-8') as f:json.dump({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target':str(p),'identical_policy_body':p.read_text(encoding='utf-8').endswith(s[a:b]),'prior_shell_attempt':'PowerShell -c quote parse failed before any file write'},f,indent=2)
