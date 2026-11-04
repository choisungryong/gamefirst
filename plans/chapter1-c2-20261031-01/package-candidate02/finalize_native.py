from pathlib import Path
import hashlib,json,shutil,struct

ROOT=Path('C:/Project/d2r-combat-baseline')
PROOF=Path(__file__).resolve().parent
SOURCE=ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-02/qa-captures/root-native02'
COPY=ROOT/'plans/chapter1-c2-20261031-01/native-runtime-02'
assert not COPY.exists()
assert not (SOURCE/'CAPTURE-MANIFEST.json').exists()
assert not (SOURCE/'NATIVE-SUMMARY.json').exists()
log=(SOURCE/'godot.log').read_text(encoding='utf-8')
exit_record=json.loads((PROOF/'native-menu-exit.json').read_text(encoding='utf-8'))
ready=[json.loads(line[len('CHAPTER1_READY '):]) for line in log.splitlines() if line.startswith('CHAPTER1_READY ')]
results=[json.loads(line[len('CHAPTER1_RUNTIME_RESULT '):]) for line in log.splitlines() if line.startswith('CHAPTER1_RUNTIME_RESULT ')]
errors=[line for line in log.splitlines() if any(x in line.upper() for x in ['ERROR:','SCRIPT ERROR:','WARNING:'])]
captures=[]
for path in sorted(SOURCE.glob('*.png')):
    data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack('>II',data[16:24])
    captures.append({'name':path.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'width':width,'height':height})
(SOURCE/'CAPTURE-MANIFEST.json').write_text(json.dumps({'count':len(captures),'captures':captures},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'actual_exit':exit_record['actual_exit'],'operator':'parent/root actual CUA input; package agent read logs/files only','ready':ready,'runtime_results':results,'error_warning_lines':errors,'capture_count':len(captures),'overwrite_refusal': 'Refusing to overwrite capture' in log,'scope':'Native input/HUD/equipment/growth/retry proof with actual defeat; not native elite victory, real audio listening, formal GPU result or completed chapter.'}
summary['success']=exit_record['actual_exit']==0 and not errors and not summary['overwrite_refusal'] and len(ready)==1 and not ready[0]['pilot'] and not ready[0]['qa_ignore_focus'] and bool(results) and results[0]['hp_raw']==0
(SOURCE/'NATIVE-SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
COPY.mkdir()
for path in SOURCE.iterdir():
    if path.is_file():shutil.copy2(path,COPY/path.name)
for name in ['native-menu-launch.json','native-menu-exit.json']:shutil.copy2(PROOF/name,COPY/name)
rows=[]
for path in sorted(COPY.iterdir()):
    origin=SOURCE/path.name if (SOURCE/path.name).exists() else PROOF/path.name
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual==hashlib.sha256(origin.read_bytes()).hexdigest()
    rows.append({'name':path.name,'source':str(origin),'sha256':actual})
(COPY/'COPY-MANIFEST.json').write_text(json.dumps({'files':rows,'mismatches':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'success':summary['success'],'capture_count':len(captures),'copy_files':len(rows),'actual_exit':summary['actual_exit'],'errors':errors,'copy':str(COPY)}))
raise SystemExit(0 if summary['success'] else 1)
