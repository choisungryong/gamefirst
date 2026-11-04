from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path('C:/Project/d2r-combat-baseline')
PROOF=Path(__file__).resolve().parent/'input-observer01'
assert not PROOF.exists()
PROOF.mkdir()
command=[str(Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')),'--path',str(ROOT),'--log-file',str(PROOF/'godot.log'),'res://chapter1/Chapter1.tscn','--','--chapter1-qa-input-log='+str(PROOF/'events.jsonl')]
started=time.time()
with (PROOF/'stdout.log').open('wb') as out,(PROOF/'stderr.log').open('wb') as err:
    p=subprocess.Popen(command,stdout=out,stderr=err)
    record={'pid':p.pid,'command':command,'source_view_sha256':hashlib.sha256((ROOT/'chapter1/chapter_view.gd').read_bytes()).hexdigest(),'scope':'Optional observer only. Hotkey behavior unchanged. Parent controls all OS UI.'}
    (PROOF/'launch.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record),flush=True)
    code=p.wait()
record.update({'actual_exit':code,'elapsed_wall_seconds':time.time()-started})
(PROOF/'exit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actual_exit':code}),flush=True)
raise SystemExit(code)
