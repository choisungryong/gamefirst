from pathlib import Path
H=Path(__file__).parent
s=(H/'prepare_space27_01.py').read_text(encoding='utf-8')
s=s.replace('space27/compare01','space27/compare02').replace('chapter1-space27-compare01','chapter1-space27-compare02')
s=s.replace('float divisions=max(12.,floor(radius*2.1));','float ring_radius=max(1.5,floor((radius-2.)/3.)*3.+3.5);\n  float divisions=max(12.,floor(ring_radius*2.1));')
s=s.replace('float band=1.-smoothstep(.18,.25,radial);','float band=(1.-smoothstep(.18,.25,radial))*smoothstep(.6,.9,radius);')
s=s.replace('vec3 inlay=vec3(.205,.187,.145)*mix(.83,1.12,variation);','vec3 inlay=stone*vec3(1.16,1.08,.88)*mix(.92,1.04,variation);')
s=s.replace('surface*.55','surface*.78').replace('bevel*paving*.82','bevel*paving*.65').replace('bevel*.026-band*.012','bevel*.012-band*.006')
s=s.replace(';assert not target.exists();target.write_text',';target.write_text')
target=H/'prepare_space27_02.py';assert not target.exists();target.write_text(s,encoding='utf-8')
exec(compile(s,str(target),'exec'))
