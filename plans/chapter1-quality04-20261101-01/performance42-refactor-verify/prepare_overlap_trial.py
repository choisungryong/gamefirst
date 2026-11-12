"""Fresh trial: memoize repeated overlap queries inside one sync only."""
from pathlib import Path
import shutil

here=Path(__file__).resolve().parent
source=Path('C:/Project/game-research/build-staging/actor42-material-exact01')
stage=Path('C:/Project/game-research/build-staging/actor42-overlap-exact01')
assert not stage.exists()
shutil.copytree(source,stage,ignore=shutil.ignore_patterns('.godot'))
leaf=stage/'chapter1/view/chapter_actors_quality42.gd'
text=leaf.read_text(encoding='utf-8')
text=text.replace(' if not _is34(actor):',' _overlap42_results.erase(actor.get_instance_id())\n if not _is34(actor):',1)
text=text.replace('var _overlap42_active := false','var _overlap42_results: Dictionary={}\nvar _overlap42_active := false')
text=text.replace(' _overlap42_ready=false',' _overlap42_results.clear()\n _overlap42_ready=false')
marker=' var state: Dictionary=actor.get_meta("minion19")\n var rig: Skeleton3D=state.skeleton'
assert text.count(marker)==1
text=text.replace(marker,''' var identity42 := actor.get_instance_id()
 var transform42 := actor.global_transform
 if _overlap42_results.has(identity42):
  var previous42: Dictionary=_overlap42_results[identity42]
  if previous42.transform==transform42 and previous42.camera==camera.get_instance_id():return previous42.result
'''+marker)
text=text.replace(' return nearest[0].distance_squared_to(nearest[1])<radius*radius',''' var result42 := nearest[0].distance_squared_to(nearest[1])<radius*radius
 _overlap42_results[identity42]={"transform":transform42,"camera":camera.get_instance_id(),"result":result42}
 return result42''')
leaf.write_text(text,encoding='utf-8')
helper=(here/'resume42.py').read_text(encoding='utf-8').replace("/'resume02'","/'overlap01'").replace('actor42-refactor-exact02','actor42-overlap-exact01')
with (here/'overlap_trial.py').open('x',encoding='utf-8') as output:output.write(helper)
(here/'overlap01').mkdir()
print('PREPARED overlap trial')
