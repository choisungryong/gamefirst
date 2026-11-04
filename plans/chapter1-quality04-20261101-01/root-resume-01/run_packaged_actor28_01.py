from pathlib import Path
H=Path(__file__).parent
s=(H/'run_packaged_hud27_01.py').read_text(encoding='utf-8').replace('full27','full28').replace('boss-phase01','hit01').replace('packaged_hud27.gd','packaged_actor28.gd').replace('--hud27-dir=','--actor28-dir=').replace('chapter1.skill.frost','chapter1.skill.ember').replace('PASS ACTUAL27 BOSS PHASE','PASS ACTUAL28 LIVE HIT')
exec(compile(s,str(H/'run_packaged_actor28_01.py'),'exec'))
