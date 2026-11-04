from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent
source=BASE.parent/'measurement/run_probe.py'
dest=source.with_name('run_probe_packaged.py')
assert not dest.exists()
text=source.read_text(encoding='utf-8')
text=text.replace('import argparse,csv,hashlib,json,math,subprocess,time','import argparse,csv,hashlib,json,math,subprocess,time,shutil')
assert text.count("    probe=folder/'probe'")==1
text=text.replace("    probe=folder/'probe'","    probe=EXE.parent/'qa-probe'/('quality04-'+run_id)\n    assert not probe.exists(),'Choose a fresh exported probe directory'")
needle="    write(folder/'execution.json',"
assert text.count(needle)==1
text=text.replace(needle,"    if probe.exists():\n        shutil.copytree(probe,folder/'probe')\n        write(folder/'probe-copy.json',{'runtime_directory':str(probe),'files':{p.name:sha(p) for p in probe.iterdir() if p.is_file()},'copied_sha256':{p.name:sha(p) for p in (folder/'probe').iterdir() if p.is_file()}})\n"+needle)
with dest.open('x',encoding='utf-8') as f:f.write(text)
with (BASE/'probe-runner-path-fix.json').open('x',encoding='utf-8') as f:
    json.dump({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'derived':str(dest),'derived_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'issue':'Original runner requested project-root evidence path which an exported PCK correctly rejects. Derived runner uses executable qa-probe allowlist, then copies raw files with hashes into new evidence. No runtime source change.'},f,indent=2)
