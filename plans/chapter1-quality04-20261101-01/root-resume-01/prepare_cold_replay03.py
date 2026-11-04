from pathlib import Path
HERE=Path(__file__).parent
s=(HERE/'cold_replay15.gd').read_text(encoding='utf-8').replace('world.sync(run,0);hud.invalidate()','world.sync(run,0);hud.invalidate();hud.sync(run,120)')
p=HERE/'cold_replay15b.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(HERE/'movie_cold_replay15.py').read_text(encoding='utf-8').replace("OUT=BASE/'elements15/replay02'","OUT=BASE/'elements15/replay03'").replace('cold-replay-20261101-02-','cold-replay-20261101-03-').replace('ColdReplay02','ColdReplay03').replace("HERE/'cold_replay15.gd'","HERE/'cold_replay15b.gd'")
s=s.replace('drawtext=text=',"drawtext=fontfile='C\\\\:/Windows/Fonts/arial.ttf':text=")
p=HERE/'movie_cold_replay15_03.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(str(p))
