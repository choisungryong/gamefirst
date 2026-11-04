from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
O=B/'motion19/attack01';S=Path('C:/Project/game-research/build-staging/chapter1-motion19-attack01')
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=read(B/'motion19/replay03/rig19-source.json');old=Path(source['stage'])
for n,h in source['pins'].items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(H/'motion19_attack_frames.gd',S/'semantics.gd')
p=S/'Replay.tscn';p.write_text(p.read_text().replace('res://replay.gd','res://semantics.gd'),encoding='utf-8')
shutil.copy2(R/'chapter1/view/chapter_actors_readable19.gd',S/'chapter1/view/chapter_actors_readable19.gd')
p=S/'chapter1/chapter_one_view.gd';p.write_text(p.read_text().replace('chapter_actors_demon19.gd','chapter_actors_readable19.gd'),encoding='utf-8')
pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
write(O/'source.json',{'stage':str(S),'pins':pins})
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://semantics.gd']),('gpu',['res://Replay.tscn','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-quit-after=30'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);write(O/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(label,p.pid,flush=True);code=p.wait(timeout=180)
 report={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};write(O/(label+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,report
for n in ['start','end','visual','attacks']:shutil.copy2(S/('motion19-'+n+'.json'),O/(n+'.json'))
shutil.copytree(S/'motion19-shots',O/'shots')
assert all(sha(S/n)==h for n,h in pins.items())
freeze=read(B/'full18/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
shutil.copytree(S/'attack-shots',O/'attack-shots')
report=read(O/'attacks.json');assert len(report['captured'])>=4
write(O/'RESULT.json',{'checks':report,'root18_preserved':True,'source_preserved':True});print('PASS',flush=True)
