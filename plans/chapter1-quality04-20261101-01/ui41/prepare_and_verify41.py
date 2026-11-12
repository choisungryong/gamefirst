from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
STAGE=Path('C:/Project/game-research/build-staging/chapter1-ui41-preview-20261112-01')
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(label,args):
    result=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
    (HERE/(label+'.log')).write_text(result.stdout+'\nSTDERR\n'+result.stderr,encoding='utf-8')
    (HERE/(label+'-execution.json')).write_text(json.dumps({'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr},ensure_ascii=False,indent=2),encoding='utf-8')
    assert result.returncode==0 and 'SCRIPT ERROR' not in result.stdout+result.stderr and 'ERROR:' not in result.stdout+result.stderr,label
closure=json.loads((ROOT/'plans/chapter1-quality04-20261101-01/full40/closure.json').read_text(encoding='utf-8'))
files=closure['runtime_source_files']+['chapter1/view/ui41/chapter_hud_quality41.gd','chapter1/art/portrait41/oath_witch_portrait_v01.png','chapter1/art/portrait41/ATTRIBUTION.ko.md']
freeze=json.loads((ROOT/'plans/chapter1-quality04-20261101-01/full40/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/p)==value for p,value in freeze.items())
if STAGE.exists():
    assert all((STAGE/p).is_file() and sha(STAGE/p)==sha(ROOT/p) for p in files), 'Existing stage is not the untouched copied preparation'
else:STAGE.mkdir()
for p in files:
    target=STAGE/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
project=(Path(closure['stage'])/'project.godot').read_text(encoding='utf-8')
project=project.replace('AshenCloisterChapterOneQuality40','AshenCloisterChapterOneUI41Preview20261112').replace('ChapterOne Quality40','ChapterOne UI41Preview')
(STAGE/'project.godot').write_text(project,encoding='utf-8')
assembly=STAGE/'chapter1/chapter_one_view.gd'
assembly.write_text(assembly.read_text(encoding='utf-8').replace('res://chapter1/view/ui40/chapter_hud_quality40.gd','res://chapter1/view/ui41/chapter_hud_quality41.gd'),encoding='utf-8')
shutil.copy2(HERE/'ui41_probe.gd',STAGE/'ui41_probe.gd')
(HERE/'STAGE.json').write_text(json.dumps({'stage':str(STAGE),'source_count':len(files),'root40_pins':freeze},indent=2),encoding='utf-8')
run('import01',[ENGINE,'--headless','--path',STAGE,'--editor','--import','--quit'])
run('parser01',[ENGINE,'--headless','--path',STAGE,'--check-only','--script','res://ui41_probe.gd'])
run('probe01',[ENGINE,'--path',STAGE,'--position','20,20','--script','res://ui41_probe.gd','--','--chapter1-profile-off','--ui41-output='+str(HERE/'probe01')])
assert all(sha(ROOT/p)==value for p,value in freeze.items())
print('UI41_VERIFIED source40 preserved')
