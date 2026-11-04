from pathlib import Path
import subprocess,json
HERE=Path(__file__).resolve().parent
source=HERE/'mage_export_research04.py';target=HERE/'mage_export_research05.py';assert not target.exists()
s=source.read_text(encoding='utf-8').replace('/gltf-preview-04\'','/gltf-preview-05\'')
marker='for obj in [rig,deform,mesh]:'
assert s.count(marker)==1
repair='''
# The immutable source has an unweighted chest vertex2053. It remained at rest
# while its adjacent faces moved, creating the observed triangular spikes.
valid={g.index:g for g in mesh.vertex_groups if g.name in deform.data.bones}
neighbors={v.index:set() for v in mesh.data.vertices}
for edge in mesh.data.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
repair_report=[]
for v in mesh.data.vertices:
    weights={g.group:g.weight for g in v.groups if g.group in valid and g.weight>0}
    total=sum(weights.values())
    before=weights.copy()
    if total<.001:
        weights={}
        for index in sorted(neighbors[v.index]):
            other=mesh.data.vertices[index]
            coefficient=1.0/max(.001,(v.co-other.co).length)
            for g in other.groups:
                if g.group in valid:weights[g.group]=weights.get(g.group,0)+g.weight*coefficient
        total=sum(weights.values())
        assert total>.001,('No weighted neighbors',v.index)
    if abs(sum(before.values())-1)>.01:
        normalized={group:value/total for group,value in weights.items()}
        for group,value in normalized.items():valid[group].add([v.index],value,'REPLACE')
        repair_report.append({'vertex':v.index,'before':{valid[g].name:w for g,w in before.items()},'after':{valid[g].name:w for g,w in normalized.items()},'neighbors':sorted(neighbors[v.index])})
assert len(repair_report)==5
assert all(sum(g.weight for g in v.groups if g.group in valid)>.99 for v in mesh.data.vertices)
'''
s=s.replace(marker,repair+'\n'+marker)
s=s.replace("'fps':40,'bones'","'weight_repair':repair_report,'fps':40,'bones'")
target.write_text(s,encoding='utf-8')
command=['C:/Project/rea-tools/blender-4.5.15-windows-x64/blender.exe','--background','--disable-autoexec',
 'C:/Project/game-research/art-sources/oga-mage-20261101-01/motion-preview-01/mage_motion_research.blend','--python-exit-code','1','--python',str(target)]
r=subprocess.run(command,capture_output=True,timeout=180)
data={'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')}
with (HERE/'mage-export05-execution.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':data['stderr'],'stdout_tail':data['stdout'][-1800:]}))
