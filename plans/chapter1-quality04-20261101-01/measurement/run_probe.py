"""Root-scheduled real-time probe. No GPU action on import; run waits in MENU.

Root must reserve the sole GPU, launch, focus the game with CUA, then click Start.
Never pass autostart, screenshots, movie, fixed FPS, ignore-focus, or wall quit.
"""
from pathlib import Path
import argparse,csv,hashlib,json,math,subprocess,time
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
EXE=ROOT/'builds/chapter1/chapter1-c2-candidate-20261101-04/AshenCloister-Chapter1.exe'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p)
    assert not p.exists(),f'Preserve prior evidence: {p}'
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')
def run(run_id):
    assert run_id and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in run_id)
    folder=HERE/'runs'/run_id
    assert not folder.exists(),'Choose a new run id'
    folder.mkdir(parents=True)
    probe=folder/'probe'
    assert EXE.is_file(),'Build the frozen candidate04 first'
    command=[str(EXE),'--windowed','--resolution','1920x1080','--rendering-method','forward_plus',
             '--disable-vsync','--max-fps','0','--delta-smoothing','disable','--',
             '--chapter1-pilot','--chapter1-seed=90131','--chapter1-primary=chapter1.skill.ember',
             '--chapter1-frame-probe-dir='+str(probe),'--chapter1-frame-probe-quit']
    launch={'command':command,'exe_sha256':sha(EXE),'scope':'Raw real-time wall intervals, not GPU hardware timer or fixed60FPS; await focused menu Start',
            'start_unix_observer_only':time.time(),'autostart':False,'gpu_allocation':'Root must reserve sole GPU before invoking run'}
    write(folder/'launch.json',launch)
    started=time.monotonic()
    with (folder/'stdout.txt').open('x',encoding='utf-8') as out,(folder/'stderr.txt').open('x',encoding='utf-8') as err:
        process=subprocess.Popen(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        write(folder/'process.json',{'pid':process.pid,'menu_focus_then_start_required':True})
        print(json.dumps({'pid':process.pid,'run_dir':str(folder),'focus_menu_then_click_start':True}),flush=True)
        timed_out=False
        try:exit_code=process.wait(timeout=300)
        except subprocess.TimeoutExpired:
            timed_out=True;process.terminate();exit_code=process.wait(timeout=30)
    write(folder/'execution.json',{'actual_exit':exit_code,'observer_wall_seconds':time.monotonic()-started,
          'timeout':timed_out,'exe_sha256_after':sha(EXE),'exe_unchanged':sha(EXE)==launch['exe_sha256']})
    audit(folder)

def audit(folder):
    folder=Path(folder).resolve()
    assert folder.is_relative_to(HERE/'runs')
    errors=[]
    probe=folder/'probe'
    if not all((probe/p).is_file() for p in ('metadata.json','frames.csv','summary.json','final-context.json')):
        errors.append('incomplete_probe_artifacts')
        result={'valid':False,'errors':errors,'scope':'Independent raw audit; no invented missing samples'}
        write(folder/'independent-audit.json',result);print(json.dumps(result));return result
    meta=read(probe/'metadata.json');summary=read(probe/'summary.json')
    with (probe/'frames.csv').open(newline='',encoding='utf-8') as f:rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(f)]
    intervals=[];prior=None
    for i,row in enumerate(rows):
        if row['sequence']!=i:errors.append('sequence_gap')
        if prior is not None and row['interval_us']!=row['elapsed_us']-prior['elapsed_us']:errors.append('raw_interval_mismatch')
        expected_phase=0 if prior is None or row['elapsed_us']<10000000 else (1 if prior['elapsed_us']>=10000000 else 3)
        if row['phase']!=expected_phase:errors.append('phase_mismatch')
        if not row['focused']:errors.append('unfocused_armed_frame')
        if row['mode_code'] not in (1,2):errors.append('terminal_or_nonplaying_armed_frame')
        if tuple(row[k] for k in ('window_width','window_height','render_width','render_height'))!=(1920,1080,1920,1080):errors.append('wrong_window_or_texture_size')
        if row['phase']==1:intervals.append(row['interval_us'])
        prior=row
    if len(rows)>180000 or summary['overflow']:errors.append('capacity_invalid')
    if not rows or rows[0]['elapsed_us']!=0 or rows[0]['interval_us']!=0:errors.append('invalid_first_callback')
    if not rows or rows[-1]['elapsed_us']<70000000:errors.append('sample_end_not_reached')
    if sum(intervals)<59000000 or any(v<=0 for v in intervals):errors.append('invalid_sample_duration_or_interval')
    if not summary['eligible_representative_run']:errors.extend(summary['eligibility_errors'])
    if meta['max_fps']!=0 or meta['vsync_mode']!=0 or meta['display_server']=='headless' or meta['rendering_method']!='forward_plus':errors.append('invalid_engine_configuration')
    if summary['raw_csv_sha256']!=sha(probe/'frames.csv'):errors.append('raw_sha_mismatch')
    if summary['measured_samples']!=len(intervals) or summary['rows']!=len(rows) or summary['measured_interval_sum_us']!=sum(intervals):errors.append('summary_counts_mismatch')
    ordered=sorted(intervals)
    def quantile(p):return ordered[max(0,math.ceil(len(ordered)*p)-1)]/1000 if ordered else None
    for key,p in (('p50_ms',.5),('p95_ms',.95),('p99_ms',.99)):
        if quantile(p)!=summary[key]:errors.append('summary_quantile_mismatch_'+key)
    execution=read(folder/'execution.json')
    if execution['actual_exit']!=0 or execution['timeout'] or not execution['exe_unchanged']:errors.append('execution_failed_or_changed')
    logs=(folder/'stdout.txt').read_text(encoding='utf-8')+(folder/'stderr.txt').read_text(encoding='utf-8')
    if any(s in logs for s in ('SCRIPT ERROR','ERROR:','WARNING:')):errors.append('engine_error_or_warning')
    result={'valid':not errors,'errors':sorted(set(errors)),'raw_sha256':sha(probe/'frames.csv'),'raw_rows':len(rows),
            'measured_intervals':len(intervals),'measured_interval_sum_us':sum(intervals),'p50_ms':quantile(.5),'p95_ms':quantile(.95),
            'p99_ms':quantile(.99),'worst_ms':max(intervals)/1000 if intervals else None,'scope':'Independent raw monotonic callback interval audit; not hardware GPU time or fixed60FPS'}
    write(folder/'independent-audit.json',result);print(json.dumps(result));return result

def aggregate(run_ids,output):
    assert len(run_ids)==3 and len(set(run_ids))==3,'Exactly three unique runs'
    runs=[HERE/'runs'/s for s in run_ids]
    audits=[read(r/'independent-audit.json') for r in runs]
    launches=[read(r/'launch.json') for r in runs]
    eligible=all(a['valid'] for a in audits) and len({v['exe_sha256'] for v in launches})==1
    write(HERE/output,{'runs':run_ids,'same_exe':len({v['exe_sha256'] for v in launches})==1,
          'eligible_three_runs':eligible,'target_p95_ms':16.67,'target_met_all_three':eligible and all(a['p95_ms']<=16.67 for a in audits),
          'audits':audits,'scope':'Three representative normal-pilot runs only; no synthetic180 load or fixed60FPS claim'})

if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='action',required=True)
    p=sub.add_parser('run');p.add_argument('--run-id',required=True)
    p=sub.add_parser('audit');p.add_argument('--run-id',required=True)
    p=sub.add_parser('aggregate');p.add_argument('--runs',nargs=3,required=True);p.add_argument('--output',required=True)
    args=ap.parse_args()
    if args.action=='run':run(args.run_id)
    elif args.action=='audit':audit(HERE/'runs'/args.run_id)
    else:aggregate(args.runs,args.output)
