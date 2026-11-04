from pathlib import Path
H=Path(__file__).parent
s=(H/'run_hit26_replay01.py').read_text(encoding='utf-8').replace('hit26/replay01','actor28/replay01').replace('chapter1-hit26-replay01','chapter1-actor28-replay01').replace('skin24-result','actor28-result').replace('skin24-shots','actor28-shots').replace('hit26_blends','hit28_blends').replace('full25b','full27')
exec(compile(s,str(H/'run_actor28_replay_gpu01.py'),'exec'))
