"""Trial unchanged-color setter suppression in a new isolated stage only."""
from pathlib import Path
import shutil

here=Path(__file__).resolve().parent
source=Path('C:/Project/game-research/build-staging/actor42-refactor-exact02')
stage=Path('C:/Project/game-research/build-staging/actor42-material-exact01')
assert not stage.exists()
shutil.copytree(source,stage,ignore=shutil.ignore_patterns('.godot'))
parent=stage/'chapter1/view/chapter_actors_demon19.gd'
text=parent.read_text(encoding='utf-8')
assert text.count('mat.albedo_color=color')==1
text=text.replace('mat.albedo_color=color','_set_color42(mat,color)')
text+='\nfunc _set_color42(material: StandardMaterial3D,color: Color) -> void:\n\tmaterial.albedo_color=color\n'
parent.write_text(text,encoding='utf-8')
leaf=stage/'chapter1/view/chapter_actors_quality42.gd'
with leaf.open('a',encoding='utf-8') as output:
    output.write('\nfunc _set_color42(material: StandardMaterial3D,color: Color) -> void:\n if material.albedo_color!=color:material.albedo_color=color\n')
helper=(here/'resume42.py').read_text(encoding='utf-8')
helper=helper.replace("/'resume02'","/'material01'").replace('actor42-refactor-exact02','actor42-material-exact01')
with (here/'material_trial.py').open('x',encoding='utf-8') as output:output.write(helper)
(here/'material01').mkdir()
print('PREPARED isolated material trial')
