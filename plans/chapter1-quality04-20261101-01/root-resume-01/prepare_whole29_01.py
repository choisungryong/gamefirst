from pathlib import Path
H=Path(__file__).parent
s=(H/'packaged_gpu25b.gd').read_text(encoding='utf-8').replace('25b','29').replace('25B','29').replace('Observer25','Observer29')
p=H/'packaged_gpu29.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(H/'run_packaged_gpu25b_01.py').read_text(encoding='utf-8').replace('full25b','full29').replace('packaged_gpu25b.gd','packaged_gpu29.gd').replace('PACKAGED25B','PACKAGED29').replace('packaged25b','packaged29').replace('GPU25B','GPU29')
p=H/'run_packaged_gpu29_01.py';assert not p.exists();p.write_text(s,encoding='utf-8');print('WHOLE29 PREPARED; NOT STARTED')
