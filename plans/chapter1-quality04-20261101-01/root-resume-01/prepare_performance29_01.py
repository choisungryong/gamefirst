from pathlib import Path
H=Path(__file__).parent
s=(H/'performance26_observer.gd').read_text(encoding='utf-8').replace('--performance26-dir=','--performance29-dir=').replace('Actual26 EXE','Actual29 EXE').replace('PERFORMANCE24_READY','PERFORMANCE29_READY')
p=H/'performance29_observer.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(H/'run_performance26.py').read_text(encoding='utf-8').replace("'full26/performance'","'full29/performance'").replace('chapter1-full-candidate-20261104-26','chapter1-full-candidate-20261104-29').replace('performance26_observer.gd','performance29_observer.gd').replace('quality26-','quality29-').replace('--performance26-dir=','--performance29-dir=')
p=H/'run_performance29.py';assert not p.exists();p.write_text(s,encoding='utf-8');print('PERFORMANCE29 PREPARED; GPU NOT STARTED')
