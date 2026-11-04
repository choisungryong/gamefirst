"""Same candidate03,120FPS-capped diagnostic with quick hidden-worker launcher."""
from pathlib import Path
import hashlib, json, subprocess, sys, time, re

ROOT=Path('C:/Project/d2r-combat-baseline')
OUT=Path(__file__).resolve().parent
EXE=ROOT/'builds/chapter1/chapter1-c2-candidate-20261101-03/AshenCloister-Chapter1.exe'
SCOPE='Nonformal same-EXE unsmoothed120FPS-limited normal-pilot0-70second diagnostic; no raw trace/excludedwarmup/three repeats/formal60FPS pass/manual play.'
COMMAND=[str(EXE),'--windowed','--always-on-top','--position','0,0','--resolution','1920x1080','--delta-smoothing','disable','--disable-vsync','--max-fps','120','--','--chapter1-start','--chapter1-pilot','--chapter1-seed=90131','--chapter1-quit-after=70']

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):
 p=OUT/n
 assert not p.exists(),'Preserve prior evidence: '+str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pins():
 expected=read(OUT.parent/'performance-diagnostic-01/pins-before.json')
 current={}
 for label,group in expected.items():
  now={p:sha(ROOT/p) for p in group['current']}
  mismatch=[p for p in now if now[p]!=group['current'][p]]
  current[label]={'count':len(now),'current':now,'mismatches':mismatch}
 assert all(not g['mismatches'] for g in current.values()),current
 return current
def prepare():
 write('PREPARATION.json',{'command':COMMAND,'scope':SCOPE,'gpu_launched':False,'pins':pins(),'sample_budget':'120FPS*70s=8400 expected below scene15000cap; actual sample count must be checked','previous_run':'performance-diagnostic-01 uncapped hit15000cap; preserve raw and correction','not_formal_reasons':['Engine delta only; no rawmonotonic times','No10second excludedwarmup','One run, not3','No per-frame focus trace'],'root_required':'Focus actual EXE window within5seconds of fast launcher return'})
 print(json.dumps({'ready':True,'gpu_launched':False}))
def run():
 assert (OUT/'PREPARATION.json').exists()
 assert not (OUT/'RUNNING.json').exists()
 before=pins();write('pins-before.json',before);started=time.time()
 with (OUT/'stdout.log').open('xb') as stdout,(OUT/'stderr.log').open('xb') as stderr:
  process=subprocess.Popen(COMMAND,cwd=EXE.parent,stdout=stdout,stderr=stderr)
  write('RUNNING.json',{'pid':process.pid,'command':COMMAND,'started_unix':started,'scope':SCOPE})
  timeout=False
  try:code=process.wait(timeout=115)
  except subprocess.TimeoutExpired:
   timeout=True;process.terminate();code=process.wait(timeout=10)
 stdout=(OUT/'stdout.log').read_bytes().decode('utf-8','replace');stderr=(OUT/'stderr.log').read_bytes().decode('utf-8','replace')
 results=[json.loads(s.split('CHAPTER1_RUNTIME_RESULT ',1)[1]) for s in stdout.splitlines() if 'CHAPTER1_RUNTIME_RESULT ' in s]
 after=pins();write('pins-after.json',after)
 errors=re.findall(r'(?:SCRIPT ERROR|ERROR:|Parse Error|WARNING:).*',stdout+'\n'+stderr)
 record={'command':COMMAND,'pid':process.pid,'actual_exit':code,'timed_out':timeout,'wall_seconds':time.time()-started,'stdout':stdout,'stderr':stderr,'runtime_results':results,'errors_or_warnings':errors,'source_and_preservation_pins_unchanged':before==after,'sample_cap_not_reached':bool(results) and all(r['frame_samples']<15000 for r in results),'scope':SCOPE,'formal_performance_pass':False}
 write('execution.json',record)
def launch():
 assert not (OUT/'LAUNCH.json').exists()
 with (OUT/'wrapper.log').open('xb') as wrapper:
  worker=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'run'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=wrapper,stderr=wrapper,creationflags=subprocess.CREATE_NO_WINDOW)
 write('LAUNCH.json',{'worker_pid':worker.pid,'scope':SCOPE,'launch_type':'Hidden helper,outputdetached,actualEXEexitworkerrecorded'})
 deadline=time.monotonic()+1.0
 while time.monotonic()<deadline and not (OUT/'RUNNING.json').exists():time.sleep(.02)
 print(json.dumps(read(OUT/'RUNNING.json') if (OUT/'RUNNING.json').exists() else {'worker_pid':worker.pid,'awaiting_game_pid':True}),flush=True)
if __name__=='__main__':
 assert len(sys.argv)==2
 {'prepare':prepare,'run':run,'launch':launch}[sys.argv[1]]()
