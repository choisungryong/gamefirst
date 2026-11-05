extends SceneTree
func _initialize() -> void:
 var baseline: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/balance36/normal01/RESULT.json"))
 var rows: Array=[];var passed: bool=true
 for primary in ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]:
  var r=load("res://chapter1/core/chapter_run_quality36.gd").new();var p=load("res://chapter1/core/chapter_pilot.gd").new();p.run=r;r.start(90131,primary)
  var routes_valid: bool=true;var branch_starts: int=0
  while r.mode not in ["victory","defeat"] and r.tick<30000:
   r.step(p.decide())
   for event in r.events:
    if event.type!="cast" or event.skill_id!="chapter1.skill.arc":continue
    var branch: int=-1;var previous: Vector2=event.position
    routes_valid=routes_valid and event.segments.size()==event.targets.size()
    for index in event.segments.size():
     var segment: Dictionary=event.segments[index]
     if int(segment.branch)!=branch:branch=int(segment.branch);previous=event.position;branch_starts+=1
     routes_valid=routes_valid and segment.from==previous and segment.to==event.targets[index]
     previous=segment.to
  var old: Dictionary={}
  for row in baseline.results:
   if row.primary==primary and row.repetition==0:old=row.snapshot;break
  var same: bool=JSON.parse_string(JSON.stringify(r.snapshot()))==old
  rows.append({"primary":primary,"same_complete_terminal_core":same,"routes_valid":routes_valid,"branch_starts":branch_starts,"tick":r.tick})
  passed=passed and same and routes_valid and branch_starts>0
  print("SEGMENT_EQ ",JSON.stringify(rows.back()))
 var f=FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/balance36/arc-segments01/equivalence01/RESULT.json",FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"rows":rows,"scope":"New segment metadata vs preserved pre-change normal01 full terminal snapshots; same seeded normal policies, plus per-cast branch endpoint consistency. Not visual/manual/performance."},"\t"));f.close();quit(0 if passed else 2)
