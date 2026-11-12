from pathlib import Path
import shutil,subprocess
from resume42 import pins,write,ENGINE

here=Path(__file__).resolve().parent
stage=Path('C:/Project/game-research/build-staging/diagnostic42-material-01')
proof=here/'material-native01'
assert not stage.exists() and not proof.exists()
before=pins()
shutil.copytree(Path('C:/Project/game-research/build-staging/diagnostic42-refactor-01'),stage,ignore=shutil.ignore_patterns('.godot'))
trial=Path('C:/Project/game-research/build-staging/actor42-material-exact01')
for name in ['chapter_actors_quality42.gd','chapter_actors_demon19.gd']:
    shutil.copy2(trial/'chapter1/view'/name,stage/'chapter1/view'/name)
p=stage/'project.godot'
p.write_text(p.read_text(encoding='utf-8-sig').replace('AshenCloisterDiagnostic42RefactorNative01','AshenCloisterDiagnostic42MaterialNative01'),encoding='utf-8')
proof.mkdir()
result=subprocess.run([str(ENGINE),'--headless','--path',str(stage),'--editor','--import','--quit'],capture_output=True,timeout=240)
(proof/'import.stdout.bin').write_bytes(result.stdout)
(proof/'import.stderr.bin').write_bytes(result.stderr)
assert result.returncode==0 and b'ERROR:' not in result.stdout+result.stderr and before==pins()
write(proof/'PRESERVATION-BEFORE.json',before)
text=(here/'run_native.py').read_text(encoding='utf-8').replace("/'native01'","/'material-native01'").replace('diagnostic42-refactor-01','diagnostic42-material-01')
with (here/'run_material_native.py').open('x',encoding='utf-8') as output:output.write(text)
print('PREPARED',stage)
