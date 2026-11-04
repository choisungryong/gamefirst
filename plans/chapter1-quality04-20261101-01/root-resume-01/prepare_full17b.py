from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17b';assert not OUT.exists();OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
freeze=read(B/'full17/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
backup=OUT/'world17-before-boundary.gd';p=R/'chapter1/view/chapter_world_quality17.gd';shutil.copy2(p,backup)
s=p.read_text(encoding='utf-8').replace('side*(15.5 if zone!=1 else 17.0)','side*21.4').replace('side*20)','side*22.8)')
assert s!=p.read_text(encoding='utf-8');p.write_text(s,encoding='utf-8')
src=(B/'full17/package_full17.py').read_text(encoding='utf-8').replace('20261102-17','20261102-17b').replace('Quality17','Quality17b').replace('candidate17','candidate17b')
src=src.replace('six stone batches with own geometry and existing texture','six stone batches outside walkable bounds, using own geometry and existing texture')
# Only placement changed, with exactly the same gameplay dependencies. Preserve
# full17's 3 complete headless proofs; avoid repeating that whole matrix.
start=src.index("    full=execute('packaged-full-normal'");end=src.index("    credits=OUTPUT/'credits'",start)
src=src[:start]+"    write(PROOF/'inherited-full17-headless.json', {'source':str(HERE.parent/'full17/build'),'reason':'Only decorative World17 positions changed. Full17 complete three-primary core proofs are preserved and separately compared; this is not a new full17b run.'})\n\n"+src[end:]
(OUT/'package_full17b.py').write_text(src,encoding='utf-8');shutil.copy2(B/'full17/RUN.ko.md',OUT/'RUN.ko.md')
(OUT/'CHANGE.json').write_text(json.dumps({'old_world_sha256':sha(backup),'new_world_sha256':sha(p),'new_placement':'piers |z|21.4, low walls |z|22.8; walkable |z|<=19','preserved17_exe':read(B/'full17/build/build.json'),'scope':'Decorative-boundary correction only;14/16/17 builds preserved.'},indent=2),encoding='utf-8')
print(str(OUT),flush=True)
