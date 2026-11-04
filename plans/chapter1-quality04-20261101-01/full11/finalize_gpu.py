from pathlib import Path
import json,hashlib,importlib.util,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).parent;ROOT=Path('C:/Project/d2r-combat-baseline')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def results(p):return [json.loads(s.split(' ',1)[1])for s in Path(p).read_text(encoding='utf-8',errors='replace').splitlines()if s.startswith('FULL_CHAPTER_RUNTIME_RESULT ')]
execution=read(HERE/'runtime/gpu-full01/execution.json')
assert execution['actual_exit']==0 and execution['stderr_bytes']==0
all_current=results(HERE/'runtime/gpu-full01/stdout.txt')
current=next(row for row in all_current if row['mode']=='victory')
old=next(row for row in results(HERE.parent/'full09/runtime/gpu-preview01/stdout.txt')if row['mode']=='victory')
keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid']
equal={key:current[key]==old[key]for key in keys}
assert all(equal.values()),equal
assert current['mode']=='victory' and current['tick']==21749 and current['kills']==3185
assert current['growth']['level']==11 and current['growth']['evolved'] and current['metrics']['events_dropped']==0
with(HERE/'GPU-FULL-RESULT.json').open('x',encoding='utf-8')as f:json.dump({'actual_exit':execution['actual_exit'],'stderr_bytes':0,'capture_count':execution['capture_count'],'same_gameplay_as09':equal,'result':current,'post_victory_ui_final':all_current[-1],'scope':'Actual RTX2070SUPER/Forward+ packaged GPU, normal policy through first victory, max-fps120/profile-off/captures. Root later manually inspected and equipped unique via native UI. First victory is compared with09 before those UI actions. Not manual whole run, heard audio or formal performance.'},f,ensure_ascii=False,indent=2)
post=all_current[-1]
assert post['equipped']['weapon']==36 and post['hero']['hp_raw']==current['hero']['hp_raw']
with(HERE/'NATIVE-REWARD-UI.json').open('x',encoding='utf-8')as f:json.dump({'scope':'Root native CUA after automatic first victory, profile explicitly off; no persistence or manual whole-run claim','observed_steps':['victory3185/Lv11/23items','open acquired equipment','scroll to last unique','select Ashflower Testament: -10% damage, +1 projectile, fire kill burst','equip; current column changes to unique and notification appears','return to victory'],'final_weapon_uid':post['equipped']['weapon'],'hp_before_raw':current['hero']['hp_raw'],'hp_after_raw':post['hero']['hp_raw'],'scroll_issue':'Selecting last item resets list to top; still open'},f,ensure_ascii=False,indent=2)
spec=importlib.util.spec_from_file_location('package11',HERE/'package_full11.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
freeze=read(HERE/'FINAL-SOURCE-FREEZE.json');p.check(ROOT,freeze)
oldfreeze=read(HERE.parent/'full09/FINAL-SOURCE-FREEZE.json')
old_changed=[name for name,h in oldfreeze.items()if p.sha(ROOT/name)!=h]
assert old_changed==['chapter1/chapter_one_view.gd'],old_changed
oldexe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-09/AshenCloister-Chapter1.exe'
assert p.sha(oldexe)=='98ead9b666373b1e746d8c57910c8ee27265290b78c0c01e35c9e268ad358724'
with(HERE/'FINAL-PRESERVATION.json').open('x',encoding='utf-8')as f:json.dump({'source11_freeze_matches':True,'source09_changed_files':old_changed,'source09_backup':'C:/Project/game-research/implementation-backups/chapter1-full10-before-20261101-01/chapter_one_view.gd','candidate09_exe_matches':True,'selected_historical_pins':p.preservation(),'scope':'Selected historical pins and immutable source11 runtime; not every historical sidecar'},f,indent=2)
print(json.dumps({'victory':True,'ticks':current['tick'],'kills':current['kills'],'same_gameplay_as09':all(equal.values()),'captures':execution['capture_count']}))
