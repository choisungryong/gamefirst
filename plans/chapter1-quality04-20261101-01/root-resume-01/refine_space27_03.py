from pathlib import Path
H=Path(__file__).parent
s=(H/'prepare_space27_02.py').read_text(encoding='utf-8')
s=s.replace('space27/compare02','space27/compare03').replace('chapter1-space27-compare02','chapter1-space27-compare03')
s=s.replace('vec3 inlay=stone*vec3(1.16,1.08,.88)*mix(.92,1.04,variation);','vec3 inlay=mix(stone*vec3(1.16,1.08,.88),vec3(.205,.187,.145),.45)*mix(.92,1.04,variation);')
s=s.replace('surface*.78','surface*.85').replace('bevel*paving*.65','bevel*paving*.78').replace('bevel*.012-band*.006','bevel*.018-band*.006')
target=H/'prepare_space27_03.py';assert not target.exists();target.write_text(s,encoding='utf-8')
exec(compile(s,str(target),'exec'))
