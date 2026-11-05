extends SceneTree
const Run=preload("res://chapter1/core/chapter_run_quality36.gd")
const Items=preload("res://chapter1/core/chapter_items.gd")
const Profile=preload("res://chapter1/core/chapter_profile.gd")
var checks: Array=[]
func check(ok: bool,label: String) -> void:checks.append({"ok":ok,"label":label})
func eligible(seed_: int) -> RefCounted:
 var r=Run.new();r.start(seed_,"chapter1.skill.arc")
 r.growth.award_xp(120);r._refresh_mode()
 var pilot=load("res://chapter1/core/chapter_pilot.gd").new();pilot.run=r
 for index in 20:
  if r.mode!="choice":break
  pilot.decide()
 r._guaranteed_drops=4;r.kills=1000;r.events.clear();r.items.clear();r.inventory.clear()
 return r
func clean_item(item: Dictionary) -> Dictionary:
 var clean: Dictionary={}
 for key in ["base_id","name","slot","stats","quality","item_level","affixes","description"]:clean[key]=item[key]
 return clean
func _initialize() -> void:
 var r=eligible(58311);check(r.growth.snapshot().level>=3,"earned growth makes eligible fixture")
 var rates: Array=[];var all_ids: Dictionary={};var normalized: bool=true
 for elite in [false,true]:
  var drops: int=0;var uniques: int=0;var trials: int=10000 if elite else 200000
  for index in trials:
   r.items.clear();r.inventory.clear();r.events.clear();r._world_uniques36.clear()
   r._maybe_drop_item({"elite":elite,"position":Vector2.ZERO,"chapter_boss":false})
   for event in r.events:
    if event.type!="item_drop":continue
    drops+=1
    if event.item.quality=="unique":
     uniques+=1;all_ids[event.item.base_id]=int(all_ids.get(event.item.base_id,0))+1
     var state: Dictionary=Profile.fresh();state.next_id=2;state.items=[{"storage_id":1,"item":clean_item(event.item)}]
     normalized=normalized and not Profile.normalize(state).is_empty()
  var rate: float=float(uniques)/maxi(1,drops)
  rates.append({"elite":elite,"trials":trials,"drops":drops,"uniques":uniques,"conditional_unique_rate":rate})
  check(rate>.10 and rate<.14 if elite else rate>.02 and rate<.06,"empirical conditional chance "+str(elite))
 check(normalized,"all dropped uniques normalize under unchanged profile grammar")
 check(all_ids.size()==3,"all three special uniques attainable")
 r=eligible(19371);var seen: Dictionary={};var unique_count: int=0;var duplicate: bool=false
 for index in 1000:
  r.events.clear();r.items.clear();r.inventory.clear()
  r._maybe_drop_item({"elite":true,"position":Vector2.ZERO,"chapter_boss":false})
  for event in r.events:
   if event.type=="item_drop" and event.item.quality=="unique":
    unique_count+=1;duplicate=duplicate or seen.has(event.item.base_id);seen[event.item.base_id]=true
 check(unique_count==2 and r._world_uniques36.size()==2 and not duplicate,"world cap two with no duplicate after many eligible drops")
 r.events.clear();r._maybe_drop_item({"elite":true,"position":Vector2.ZERO,"chapter_boss":true})
 var boss_ok: bool=false
 for event in r.events:
  if event.type=="item_drop":boss_ok=event.item.quality=="unique" and event.item.base_id=="chapter1.full.unique.forked_covenant" and event.item.objective_reward
 check(boss_ok,"boss guarantee survives world cap")
 r=eligible(841);r._guaranteed_drops=0;r.kills=6;r.events.clear();r._maybe_drop_item({"elite":false,"position":Vector2.ZERO,"chapter_boss":false})
 var forced_ok: bool=false
 for event in r.events:
  if event.type=="item_drop":forced_ok=event.item.quality=="magic" and event.item.slot=="weapon"
 check(forced_ok,"first guaranteed slot is not replaced by random unique")
 var low=Run.new();low.start(77,"chapter1.skill.arc");low._guaranteed_drops=4;var low_unique: int=0
 for index in 500:
  low.events.clear();low.inventory.clear();low._maybe_drop_item({"elite":true,"position":Vector2.ZERO,"chapter_boss":false})
  for event in low.events:
   if event.type=="item_drop" and event.item.quality=="unique":low_unique+=1
 check(low_unique==0,"no random unique below level3")
 var passed: bool=true
 for c in checks:passed=passed and c.ok
 var f=FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/balance36/loot01/RESULT.json",FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"rates":rates,"unique_ids":all_ids,"scope":"Controlled repeated real drop-function trials. Per-trial world cap cleared only for rate measurement; separate persistent cap/boss tests. In-memory existing profile normalization only; not real save/relaunch or natural whole-run rates."},"\t"));f.close()
 print("LOOT36 ",JSON.stringify({"passed":passed,"rates":rates,"checks":checks}));quit(0 if passed else 2)
