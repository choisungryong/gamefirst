from pathlib import Path
import importlib.util,json,shutil,subprocess,sys

here=Path(__file__).resolve().parent
root=here.parents[2]
attempt=sys.argv[2] if len(sys.argv)>2 else '01'
assert attempt in ['01','02']
stage=Path('C:/Project/game-research/build-staging')/('arc44-preview'+attempt)
proof=here/('proof' if attempt=='01' else 'proof'+attempt)
engine=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
spec=importlib.util.spec_from_file_location('final43',here.parent/'final-performance43/run_performance43.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def write(path,value):
    with Path(path).open('x',encoding='utf-8') as output:json.dump(value,output,ensure_ascii=False,indent=2)
action=sys.argv[1]
if action=='prepare':
    assert not stage.exists() and not proof.exists()
    before=module.package_snapshot()
    stage.mkdir();proof.mkdir()
    closure=module.read(here.parent/'full43/closure.json')
    for name in closure['runtime_source_files']+['chapter1/view/chapter_elements_quality44.gd','chapter1/view/arc_core_quality44.gdshader','chapter1/view/arc_contact_quality44.gdshader']:
        target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
    shutil.copy2(Path(closure['stage'])/'project.godot',stage/'project.godot')
    p=stage/'project.godot';p.write_text(p.read_text(encoding='utf-8-sig').replace('AshenCloisterChapterOneQuality43','AshenCloisterDiagnosticArc44'),encoding='utf-8')
    shutil.copy2(here/'compare44.gd',stage/'compare44.gd')
    write(proof/'PRESERVATION-BEFORE.json',before)
    assert before==module.package_snapshot()
    print('PREPARED',stage,flush=True)
else:
    assert action in ['import','720','1080']
    before=module.package_snapshot();result_path=proof/(action+'-execution.json')
    assert not result_path.exists()
    fixture='res://compare44-branch.gd' if action=='1080' else 'res://compare44.gd'
    args=([str(engine),'--headless','--path',str(stage),'--editor','--import','--quit'] if action=='import' else [str(engine),'--path',str(stage),'--script',fixture,'--rendering-method','forward_plus','--','--chapter1-profile-off','--chapter1-seed=90131','--arc44-width='+('1280' if action=='720' else '1920'),'--arc44-output='+str(proof/('compare'+action))])
    r=subprocess.run(args,capture_output=True,timeout=240)
    (proof/(action+'.stdout.bin')).write_bytes(r.stdout);(proof/(action+'.stderr.bin')).write_bytes(r.stderr)
    bad=any(marker in r.stdout+r.stderr for marker in [b'ERROR:',b'SCRIPT ERROR',b'SHADER ERROR'])
    write(result_path,{'command':args,'exit':r.returncode,'errors':bad,'preserved':before==module.package_snapshot()})
    print(json.dumps({'action':action,'attempt':attempt,'exit':r.returncode,'errors':bad,'preserved':before==module.package_snapshot()}),flush=True)
    if bad:
        for stream in [r.stdout,r.stderr]:
            try:decoded=stream.decode('utf-8')
            except UnicodeDecodeError:decoded=stream.decode('cp949',errors='replace')
            print(decoded[-1800:])
    assert r.returncode==0 and not bad and before==module.package_snapshot()
