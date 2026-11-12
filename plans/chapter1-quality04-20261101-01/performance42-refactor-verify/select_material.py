"""Select the validated material trial; retain all earlier proposal bytes."""
from pathlib import Path
import shutil
from resume42 import ROOT,BASE,pins,sha,read,write

here=Path(__file__).resolve().parent
before=pins()
trial=Path('C:/Project/game-research/build-staging/actor42-material-exact01')
candidate=BASE/'performance42-actors/refactor-candidate'
backup=candidate/'before-material-selection'
assert not backup.exists() and not (BASE/'full42/SELECTION.json').exists()
for label in ['full','extended','cache']:
    result=read(here/'material01'/(label+'.json'))
    assert result['exit']==0 and not result['errors'] and result['preserved']
summary=read(here/'material-native01/raw/probe/summary.json')
execution=read(here/'material-native01/execution.json')
assert execution=={'exit':0,'preserved':True}
assert summary['eligible_representative_run'] and summary['p95_ms']==16.984
assert summary['p95_ms']<read(BASE/'performance42-components/run04/raw/probe/summary.json')['p95_ms']
backup.mkdir()
leaf='chapter1/view/chapter_actors_quality42.gd'
shutil.copy2(ROOT/leaf,backup/'chapter_actors_quality42.gd')
parents=['chapter_actors_demon19.gd','chapter_actors_quality21.gd']
for name in parents:shutil.copy2(candidate/name,backup/name)
shutil.copy2(trial/leaf,ROOT/leaf)
for name in parents:shutil.copy2(trial/'chapter1/view'/name,candidate/name)
assert before==pins()
selection={'parity_passed':True,'native_improvement_confirmed':True,'root_files':{leaf:sha(ROOT/leaf)},'candidate_parents':{n:sha(candidate/n) for n in parents},'isolated_stage':str(trial),'proof':str(here/'material01'),'native_summary':str(here/'material-native01/raw/probe/summary.json'),'native_p95_ms':summary['p95_ms'],'final_product_performance_passed':False,'rejected_overlap_trial_p95_ms':17.417,'prior_proposals_preserved':str(backup)}
write(BASE/'full42/SELECTION.json',selection)
print('SELECTED material trial; released root parents still unchanged')
