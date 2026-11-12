"""Prepare fresh comparable component diagnostic, never change released files."""
from pathlib import Path
import json, shutil, subprocess
from resume42 import pins, write, ENGINE, BASE, ROOT

stage=Path('C:/Project/game-research/build-staging/diagnostic42-refactor-01')
proof=Path(__file__).resolve().parent/'native01'
assert not stage.exists() and not proof.exists()
before=pins()
source=Path('C:/Project/game-research/build-staging/diagnostic42-actors-01')
shutil.copytree(source,stage,ignore=shutil.ignore_patterns('.godot'))
proof.mkdir()
for name in ['chapter_actors_demon19.gd','chapter_actors_quality21.gd']:
    shutil.copy2(BASE/'performance42-actors/refactor-candidate'/name,stage/'chapter1/view'/name)
shutil.copy2(ROOT/'chapter1/view/chapter_actors_quality42.gd',stage/'chapter1/view/chapter_actors_quality42.gd')
p=stage/'project.godot'
p.write_text(p.read_text(encoding='utf-8-sig').replace('AshenCloisterDiagnostic42Actors01','AshenCloisterDiagnostic42RefactorNative01'),encoding='utf-8')
result=subprocess.run([str(ENGINE),'--headless','--path',str(stage),'--editor','--import','--quit'],capture_output=True,timeout=240)
(proof/'import.stdout.bin').write_bytes(result.stdout)
(proof/'import.stderr.bin').write_bytes(result.stderr)
assert result.returncode==0 and b'ERROR:' not in result.stdout+result.stderr
assert before==pins()
write(proof/'PRESERVATION-BEFORE.json',before)
write(proof/'STAGE.json',{'stage':str(stage),'source':str(source),'scope':'Instrumented comparison; not packaged final score'})
print('PREPARED',stage)
