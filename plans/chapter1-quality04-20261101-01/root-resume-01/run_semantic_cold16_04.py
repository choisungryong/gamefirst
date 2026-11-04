from pathlib import Path
import json,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/cold16/semantic04';assert not OUT.exists();OUT.mkdir()
cmd=[str(ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'),'--headless','--script',str(Path(__file__).with_name('semantic_cold16_04.gd'))]
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60);report={'command':cmd,'actual_exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr};(OUT/'execution.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');assert r.returncode==0 and not r.stderr,report
print((OUT/'result.json').read_text(encoding='utf-8'),flush=True)
