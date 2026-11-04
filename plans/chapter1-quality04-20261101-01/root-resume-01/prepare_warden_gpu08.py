from pathlib import Path
import json
HERE=Path(__file__).parent
s=(HERE/'warden_visibility_probe13.gd').read_text(encoding='utf-8')
s=s.replace('samples.append({"name":sample.name,"overlaps":overlaps,"alpha":alpha})','''samples.append({"name":sample.name,"overlaps":overlaps,"alpha":alpha})
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("res://plans/chapter1-quality04-20261101-01/boss-research12/gpu08/captures/"+sample.name+".png")''')
s=s.replace('for i in 80:actors.sync(run,1.0/60.0)','''for i in 80:
		actors.sync(run,1.0/60.0)
		if i in [0,20,40,79]:
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png("res://plans/chapter1-quality04-20261101-01/boss-research12/gpu08/captures/death-%02d.png"%i)''')
s=s.replace('boss-research12/visibility06','boss-research12/gpu08')
p=HERE/'warden_gpu_probe13.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(HERE/'run_warden_visibility06.py').read_text(encoding='utf-8')
s=s.replace("OUT=BASE/'visibility06'","OUT=BASE/'gpu08'").replace('chapter1-warden-visibility-20261101-06','chapter1-warden-gpu-20261101-08')
s=s.replace('warden_visibility_probe13.gd','warden_gpu_probe13.gd').replace('WardenResearch13Visibility06','WardenResearch13GPU08').replace('boss-research12/visibility06','boss-research12/gpu08')
s=s.replace("for label,args in", "(STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/gpu08/captures').mkdir()\nfor label,args in")
s=s.replace("command=[engine,'--headless','--path',str(STAGE)]+args","command=[engine]+([] if label=='probe' else ['--headless'])+['--path',str(STAGE)]+args")
s+="\nshutil.copytree(STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/gpu08/captures',OUT/'captures')\n"
p=HERE/'run_warden_gpu08.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(str(p))
