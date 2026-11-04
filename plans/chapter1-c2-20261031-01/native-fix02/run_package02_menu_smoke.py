from pathlib import Path
import json,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline')
PROOF=ROOT/'plans/chapter1-c2-20261031-01/package-candidate02'
EXE=ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe'
DEST=EXE.parent/'qa-captures/package-menu-smoke01'
assert EXE.is_file() and not DEST.exists()
assert not (PROOF/'menu-smoke-execution.json').exists()
DEST.mkdir(parents=True)
command=[str(EXE),'--resolution','1920x1080','--log-file',str(DEST/'godot.log'),'--','--chapter1-quit-after=3','--chapter1-capture-dir='+str(DEST)]
result=subprocess.run(command,capture_output=True,text=True,timeout=60)
record={'command':command,'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'scope':'Three-second ordinary-menu resource/QA-mode-capture smoke; not gameplay, performance or quality approval.'}
(PROOF/'menu-smoke-execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
log=(DEST/'godot.log').read_text(encoding='utf-8')
ready=[json.loads(s[len('CHAPTER1_READY '):]) for s in log.splitlines() if s.startswith('CHAPTER1_READY ')]
checks={
 'actual_exit_zero':result.returncode==0,
 'five_imported_roles':len(ready)==1 and set(ready[0]['actor_states'])=={'hero','walker','ranged','charger','elite'},
 'all_action_direction_states':len(ready)==1 and all(set(['cast','hit','death','move_south','move_east','move_north','move_west']).issubset(s) for s in ready[0]['actor_states'].values()),
 'raw_fallback_zero':len(ready)==1 and ready[0]['raw_texture_fallbacks']==[],
 'ordinary_menu':len(ready)==1 and not ready[0]['pilot'] and not ready[0]['qa_ignore_focus'],
 'stable_menu_capture':(DEST/'state-0001-run-000-menu.png').is_file(),
 'no_error_warning':not any(s in log.upper() for s in ['ERROR:','SCRIPT ERROR:','WARNING:']),
}
summary={'checks':checks,'success':all(checks.values()),'ready':ready,'scope':record['scope']}
(PROOF/'menu-smoke-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
raise SystemExit(0 if summary['success'] else 1)
