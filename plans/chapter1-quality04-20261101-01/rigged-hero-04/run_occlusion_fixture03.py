from pathlib import Path
import subprocess,json,shutil
HERE=Path(__file__).parent
STAGE=Path('C:/Project/game-research/build-staging/rigged-hero-20261101-04')
OUT=HERE/'occlusion-fixture03';assert not OUT.exists();OUT.mkdir()
target=STAGE/'occlusion_fixture.gd'
target.write_text((HERE/target.name).read_text(encoding='utf-8').replace('occlusion-fixture/captures','occlusion-fixture03/captures'),encoding='utf-8')
command=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--path',str(STAGE),'res://OcclusionFixture.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=6.2']
r=subprocess.run(command,capture_output=True,timeout=60)
with (OUT/'execution.json').open('x',encoding='utf-8') as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),'scope':'Visual fixture. Previous fixture02 reused existing capture paths and has no new captures; not visual proof.'},f,indent=2)
source=STAGE/'plans/chapter1-quality04-20261101-01/rigged-hero-04/occlusion-fixture03/captures'
if source.exists():shutil.copytree(source,OUT/'captures')
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:1200]}))
