from pathlib import Path
import shutil

here=Path(__file__).resolve().parent
stage=Path('C:/Project/game-research/build-staging/arc44-preview01')
source=(stage/'compare44.gd').read_text(encoding='utf-8')
with (here/'proof/compare44-720-used.gd').open('x',encoding='utf-8') as output:output.write(source)
text=source.replace('"branch_casts":0','"branch_casts":0,"three_branch_casts":0')
text=text.replace('origins[segment.from]=true','origins[segment.from]=int(origins.get(segment.from,0))+1')
needle='\t\t\t\t\tif branched:counts.branch_casts+=1'
assert needle in text
text=text.replace(needle,needle+'''
\t\t\t\t\tvar three_way := false
\t\t\t\t\tfor count in origins.values():
\t\t\t\t\t\tif int(count)>=3:three_way=true
\t\t\t\t\tif three_way:
\t\t\t\t\t\tcounts.three_branch_casts+=1
\t\t\t\t\t\tif not captures.has("three_branch"):capture="three_branch"
''')
with (here/'compare44-branch.gd').open('x',encoding='utf-8') as output:output.write(text)
destination=stage/'compare44-branch.gd';assert not destination.exists()
shutil.copy2(here/'compare44-branch.gd',destination)
print('Prepared natural three-way branch capture; original720 fixture preserved')
