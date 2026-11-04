from pathlib import Path
H=Path(__file__).parent
script=(H/'hit26_replay.gd').read_text(encoding='utf-8').replace('26','28').replace('skin24-shots','actor28-shots').replace('skin24-result','actor28-result')
script=script.replace('\teffects=preload("res://chapter1/view/chapter_elements_quality22.gd").new()\n','')
script=script.replace('Unconnected hit28/World22/FX22/HUD23','Unconnected Actor28/World22/FX26/HUD27')
target=H/'actor28_replay.gd';assert not target.exists();target.write_text(script,encoding='utf-8')
s=(H/'prepare_hit26_replay01.py').read_text(encoding='utf-8').replace('hit26/replay01','actor28/replay01').replace('chapter1-hit26-replay01','chapter1-actor28-replay01').replace('full25b','full27').replace('chapter_actors_quality26.gd','chapter_actors_quality28.gd').replace('hit26_replay.gd','actor28_replay.gd').replace('skin24-result','actor28-result').replace('skin24-shots','actor28-shots')
target=H/'run_actor28_replay01.py';assert not target.exists();target.write_text(s,encoding='utf-8');exec(compile(s,str(target),'exec'))
