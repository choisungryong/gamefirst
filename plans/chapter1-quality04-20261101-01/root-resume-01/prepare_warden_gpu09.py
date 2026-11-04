from pathlib import Path
HERE=Path(__file__).parent
s=(HERE/'warden_gpu_probe13.gd').read_text(encoding='utf-8').replace('world.update_camera(run.hero.position,0)','world.update_camera(run.hero.position,10)').replace('boss-research12/gpu08','boss-research12/gpu09')
p=HERE/'warden_gpu_probe13b.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(HERE/'run_warden_gpu08.py').read_text(encoding='utf-8').replace("OUT=BASE/'gpu08'","OUT=BASE/'gpu09'").replace('chapter1-warden-gpu-20261101-08','chapter1-warden-gpu-20261101-09').replace('WardenResearch13GPU08','WardenResearch13GPU09').replace('boss-research12/gpu08','boss-research12/gpu09').replace('warden_gpu_probe13.gd','warden_gpu_probe13b.gd')
p=HERE/'run_warden_gpu09.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(str(p))
